# GitHub Actions Quick Start — Copy/Paste

---

## TL;DR (3 minutes)

```bash
# 1. Copy headless CLI to repo
cp metasnie_headless_cli.py ./

# 2. Create workflow directory & file
mkdir -p .github/workflows
cp .github_workflows_sniper.yml .github/workflows/sniper.yml

# 3. Commit to git
git add metasnie_headless_cli.py .github/workflows/sniper.yml
git commit -m "Add GitHub Actions sniper"
git push

# 4. Set secrets (go to GitHub web UI — see next section)
```

---

## Step 1: Add Files to Your Repo

In your local metasnie folder:

```bash
# Copy the headless CLI
wget https://raw.githubusercontent.com/YOUR_REPO/main/metasnie_headless_cli.py
# OR if you have the file:
cp /path/to/metasnie_headless_cli.py ./

# Create workflow directory
mkdir -p .github/workflows

# Add workflow file
cat > .github/workflows/sniper.yml << 'EOF'
name: Metasnie Sniper

on:
  schedule:
    - cron: '* * * * *'
  workflow_dispatch:

jobs:
  snipe:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - run: |
          pip install aiohttp urllib3 requests
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
      
      - run: |
          mkdir -p lists
          if [ ! -f lists/names.txt ]; then
            echo "testname1" > lists/names.txt
          fi
      
      - run: |
          mkdir -p creds
          cat > creds/creds.json << 'CREDS'
          ${{ secrets.CREDS_JSON }}
          CREDS
      
      - run: python metasnie_headless_cli.py --env --proxies "$PROXIES" --webhook "${{ secrets.WEBHOOK_URL }}"
        env:
          NAMES_LIST: lists/names.txt
          WEBHOOK_URL: ${{ secrets.WEBHOOK_URL }}
          PROXIES: ${{ secrets.PROXIES }}
          CONCURRENCY: 500
          SNIPE_MODE: 'true'
        timeout-minutes: 5
EOF

# Commit
git add .github/workflows/sniper.yml metasnie_headless_cli.py
git commit -m "Add GitHub Actions sniper"
git push origin main
```

---

## Step 2: Set GitHub Secrets

Go to: **https://github.com/YOUR_USERNAME/metasnie/settings/secrets/actions**

### Secret 1: CREDS_JSON

**Format:** Single line JSON (no line breaks)

**Get your credentials:**

From your local `creds/creds.json`, minify it (remove spaces):

```bash
# Minify your creds.json
python3 -c "import json; print(json.dumps(json.load(open('creds/creds.json'))))" | tr -d '\n'
```

Copy the output and paste into GitHub secret:

```json
[{"PROFILE_ID":"YOUR_ID","fs":"YOUR_TOKEN","username":"name","sniped":null,"rate_limited":false,"rate_limited_since":null,"sniper_enabled":true,"locked":false}]
```

**Or if you don't have it, get fresh tokens:**

1. Open https://accountscenter.meta.com/profiles/YOUR_PROFILE_ID/username/
2. Open DevTools (F12) → **Application** → **Cookies**
3. Find: `fs` (copy the value)
4. Find: Your PROFILE_ID in the URL or in the page HTML

**Paste in GitHub:**
```json
[{"PROFILE_ID":"123456789","fs":"ABCDEF...XYZ","username":"yourname","sniped":null,"rate_limited":false,"rate_limited_since":null,"sniper_enabled":true,"locked":false}]
```

### Secret 2: WEBHOOK_URL

Discord notifications (optional).

**Get webhook:**

1. Discord server → Right-click channel
2. **Edit Channel** → **Integrations** → **Webhooks**
3. **New Webhook** → Copy URL

**Paste in GitHub:**
```
https://discord.com/api/webhooks/12345678/ABCDEFghijklmnop_QRST
```

### Secret 3: PROXIES

Proxy rotation (optional).

**Paste in GitHub:**
```
http://5m12gq1d:40b1f1e9@p.tokenu.to:10000
http://5m12gq1d:40b1f1e9@p.tokenu.to:10001
http://5m12gq1d:40b1f1e9@p.tokenu.to:10002
http://5m12gq1d:40b1f1e9@p.tokenu.to:10003
http://5m12gq1d:40b1f1e9@p.tokenu.to:10004
http://5m12gq1d:40b1f1e9@p.tokenu.to:10005
http://5m12gq1d:40b1f1e9@p.tokenu.to:10006
http://5m12gq1d:40b1f1e9@p.tokenu.to:10007
http://5m12gq1d:40b1f1e9@p.tokenu.to:10008
http://5m12gq1d:40b1f1e9@p.tokenu.to:10009
```

---

## Step 3: Update Your Names List

```bash
# Add names to snipe
cat > lists/names.txt << 'EOF'
coolname1
coolname2
dreamusername
targetname
anothersnipe
EOF

git add lists/names.txt
git commit -m "Update names list"
git push
```

---

## Step 4: Test It

Go to: **https://github.com/YOUR_USERNAME/metasnie/actions**

1. Click **Metasnie Sniper** (left sidebar)
2. Click **Run workflow** → **Run workflow**
3. Wait 1-2 minutes
4. Click the running job
5. Scroll logs to see:
   ```
   [INFO] Loaded 5 names
   [INFO] Loaded 1 credentials
   [INFO] Warming 1 accounts...
   [INFO] 1/1 accounts ready
   [START] Checker running...
   [STATS] Cycle: 1 | Found: 0 | Checks: 250 | CPS: 50.0
   ```

**If you see errors:**
- Check GitHub secrets are set (Settings → Secrets)
- Check creds/creds.json format is valid JSON
- Check PROFILE_ID and fs token are correct

---

## Checklist

- [ ] Copied `metasnie_headless_cli.py` to repo
- [ ] Created `.github/workflows/sniper.yml`
- [ ] Set secret: `CREDS_JSON`
- [ ] Set secret: `WEBHOOK_URL` (optional)
- [ ] Set secret: `PROXIES` (optional)
- [ ] Added names to `lists/names.txt`
- [ ] Committed and pushed to GitHub
- [ ] Manual workflow test passed
- [ ] Got Discord notification (if webhook set)

---

## Change Schedule

Edit `.github/workflows/sniper.yml` line with `cron`:

```yaml
# Every minute (default)
- cron: '* * * * *'

# Every 5 minutes
- cron: '*/5 * * * *'

# Every hour
- cron: '0 * * * *'

# Twice a day (9 AM and 9 PM UTC)
- cron: '0 9,21 * * *'
```

Then:
```bash
git add .github/workflows/sniper.yml
git commit -m "Change sniper schedule"
git push
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Workflow doesn't appear | Go Actions → Enable Actions |
| "Secret not found" | Check spelling: `CREDS_JSON` (exact case) |
| "Invalid JSON" | Use https://jsonlint.com to validate |
| "Token expired" | Get new `fs` cookie from accountscenter.meta.com |
| "No module found" | Wait 30 seconds (dependencies installing) |
| "Too many redirects" | Your proxy might be dead, try direct IP |

---

## Run Locally (Test First)

```bash
# Install dependencies
pip install aiohttp urllib3 requests

# Test without proxies
python metasnie_headless_cli.py --names lists/names.txt

# Test with proxies
python metasnie_headless_cli.py \
  --names lists/names.txt \
  --proxies "http://user:pass@host:port,http://..." \
  --webhook "https://discord.com/api/webhooks/..."

# Test with environment variables (like GitHub Actions)
export CREDS_JSON='[{"PROFILE_ID":"...","fs":"..."}]'
export WEBHOOK_URL="https://discord.com/..."
export PROXIES="http://..."
python metasnie_headless_cli.py --env
```

---

## One-Liner Setup

If you have everything ready:

```bash
# 1. Add files
cp metasnie_headless_cli.py . && mkdir -p .github/workflows
cat > .github/workflows/sniper.yml << 'WORKFLOW'
# Paste workflow YAML from above
WORKFLOW

# 2. Commit
git add metasnie_headless_cli.py .github/workflows/sniper.yml
git commit -m "Add GitHub Actions" && git push

# 3. Go to GitHub and add secrets manually (no way around this)
# Then done!
```

---

## Monitor Performance

After running for a few cycles, check:

```
https://github.com/YOUR_USERNAME/metasnie/actions/workflows/sniper.yml
```

Click latest run to see stats:
```
[STATS] Cycle: 5 | Found: 0 | Checks: 2500 | CPS: 100.5
```

**Good metrics:**
- CPS 50-150 (depends on proxies/internet)
- Checks increasing steadily
- No errors in logs

---

## Get Help

1. Check logs: Actions → Latest run → sniper
2. Validate JSON: https://jsonlint.com
3. Test locally first
4. Check Discord webhook is correct

---

## Costs

**GitHub Actions for public repos: FREE**

- Unlimited workflows
- Unlimited runs
- 20 concurrent jobs
- 35 days job history

Just make sure your repo is public (or you have a paid plan).

---

That's it! Your sniper is running 24/7 now. 🚀
