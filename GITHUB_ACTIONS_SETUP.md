# GitHub Actions Setup for Metasnie — Complete Guide

---

## Step 1: Prepare Your Repository

### 1.1 Clone or Create Repo

```bash
# If you don't have it yet
git clone https://github.com/nicoisnotseeingthis/metasnie.git
cd metasnie
```

### 1.2 Add Headless CLI

Copy `metasnie_headless_cli.py` into your repo root:

```bash
cp metasnie_headless_cli.py ./metasnie_headless_cli.py
```

### 1.3 Create Workflow Directory

```bash
mkdir -p .github/workflows
```

### 1.4 Add Workflow File

Copy `.github_workflows_sniper.yml` to `.github/workflows/sniper.yml`:

```bash
cp .github_workflows_sniper.yml .github/workflows/sniper.yml
```

Your repo structure should look like:
```
metasnie/
├── main.py
├── headless.py
├── metasnie_headless_cli.py  ← NEW
├── requirements.txt
├── lists/
│   └── names.txt
├── creds/
│   └── creds.json
└── .github/
    └── workflows/
        └── sniper.yml  ← NEW
```

---

## Step 2: Set Up GitHub Secrets

GitHub Secrets are **encrypted environment variables** that GitHub Actions can access.

### 2.1 Go to Settings

1. Open: https://github.com/YOUR_USERNAME/metasnie
2. Click **Settings** (top right)
3. Click **Secrets and variables** (left sidebar)
4. Click **Actions**

### 2.2 Create Secret: CREDS_JSON

This is your account credentials (needed for sniping).

**Create the JSON:**

```json
[
  {
    "PROFILE_ID": "YOUR_PROFILE_ID_1",
    "fs": "YOUR_FS_TOKEN_1",
    "username": "yourname",
    "sniped": null,
    "rate_limited": false,
    "rate_limited_since": null,
    "sniper_enabled": true,
    "locked": false
  },
  {
    "PROFILE_ID": "YOUR_PROFILE_ID_2",
    "fs": "YOUR_FS_TOKEN_2",
    "username": "yourname2",
    "sniped": null,
    "rate_limited": false,
    "rate_limited_since": null,
    "sniper_enabled": true,
    "locked": false
  }
]
```

**Steps:**
1. Click **New repository secret**
2. **Name:** `CREDS_JSON`
3. **Value:** Paste the JSON above (with YOUR values)
4. Click **Add secret**

### 2.3 Create Secret: WEBHOOK_URL

Discord webhook for notifications (optional but recommended).

**How to get Discord webhook:**
1. Open Discord server
2. Right-click channel → **Edit Channel**
3. **Integrations** → **Webhooks** → **New Webhook**
4. Copy the **Webhook URL**

**Steps:**
1. Click **New repository secret**
2. **Name:** `WEBHOOK_URL`
3. **Value:** `https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN`
4. Click **Add secret**

### 2.4 Create Secret: PROXIES

Your 11 proxies (optional but recommended for faster checking).

**Steps:**
1. Click **New repository secret**
2. **Name:** `PROXIES`
3. **Value:** 
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
4. Click **Add secret**

---

## Step 3: Prepare Your Names List

Add the usernames you want to snipe to `lists/names.txt`:

```bash
mkdir -p lists
cat > lists/names.txt << 'EOF'
coolname1
coolname2
coolname3
testusername
sniperboy
anothertest
EOF
```

Commit to git:
```bash
git add lists/names.txt
git commit -m "Add names list"
git push
```

---

## Step 4: Test the Workflow

### 4.1 Manual Trigger

1. Go to your repo
2. Click **Actions** (top menu)
3. Click **Metasnie Sniper** (left sidebar)
4. Click **Run workflow** → **Run workflow**

Wait 1-2 minutes for it to run.

### 4.2 Check Logs

1. Click the running workflow
2. Click **snipe** job
3. Scroll through logs to see:
   ```
   [INFO] Loaded 6 names
   [INFO] Loaded 2 credentials
   [INFO] Warming 2 accounts...
   [INFO] 2/2 accounts ready
   [START] Checker running... (Press Ctrl+C to stop)
   [STATS] Cycle: 0 | Found: 0 | Checks: 156 | CPS: 31.2
   ```

### 4.3 Check for Errors

Common errors:
- **`ModuleNotFoundError: No module named 'aiohttp'`** → Dependencies didn't install (wait longer)
- **`FileNotFoundError: creds/creds.json`** → Secret not set properly
- **`[WARN] Sniper accounts not ready`** → Invalid PROFILE_ID or fs token

---

## Step 5: Set Schedule (Automatic)

The workflow currently runs **every minute** via cron.

To change frequency, edit `.github/workflows/sniper.yml`:

```yaml
on:
  schedule:
    # Every minute
    - cron: '* * * * *'
    
    # Every 5 minutes
    # - cron: '*/5 * * * *'
    
    # Every hour
    # - cron: '0 * * * *'
    
    # Every day at 3 PM UTC
    # - cron: '0 15 * * *'
```

Cron format: `minute hour day month day_of_week`

Common examples:
```
* * * * *     = Every minute
*/5 * * * *   = Every 5 minutes
0 * * * *     = Every hour
0 12 * * *    = Every day at noon UTC
0 9 * * 1     = Every Monday at 9 AM UTC
```

Commit changes:
```bash
git add .github/workflows/sniper.yml
git commit -m "Update sniper schedule"
git push
```

---

## Step 6: Get Notifications

When a name is AVAILABLE, you'll get Discord notifications.

### 6.1 Webhook Format

By default, messages look like:
```
🎯 **AVAILABLE** `coolname1`
```

### 6.2 Custom Messages (Advanced)

Edit `metasnie_headless_cli.py` line ~200:

```python
def _send_webhook(self, name):
    requests.post(url, json={
        "content": f"🎯 **AVAILABLE** `{name}`",  # ← Change this
        "username": "Metasnie Sniper"
    })
```

Examples:
```python
"content": f"@everyone SNIPE READY: `{name}`"
"content": f"⚡ **{name.upper()}** IS AVAILABLE"
"content": f":tada: New available: `{name}`"
```

---

## Step 7: Add More Credentials (Optional)

If you have more accounts, just update `CREDS_JSON` secret:

1. Go to **Settings → Secrets and variables → Actions**
2. Click **CREDS_JSON** → **Update**
3. Add more accounts to the JSON array
4. Save

No need to restart — changes take effect next run.

---

## Step 8: Monitor Performance

After running for a few minutes, check the stats:

**Actions → Metasnie Sniper → Latest run → sniper job → Logs**

Look for:
```
[STATS] Cycle: 1 | Found: 0 | Checks: 500 | CPS: 100.0
[STATS] Cycle: 2 | Found: 0 | Checks: 1000 | CPS: 95.2
```

**CPS = Checks Per Second**
- With proxies: 50-150 CPS
- Without proxies: 30-50 CPS
- This is good! ✓

---

## Troubleshooting

### Problem: Workflow doesn't run

**Solution:** Check Actions are enabled
1. Go repo → **Actions**
2. Click **Enable Actions** if grayed out

### Problem: "CREDS_JSON not found"

**Solution:** Secret name might be wrong
1. Go **Settings → Secrets and variables → Actions**
2. Make sure secret is named exactly: `CREDS_JSON`

### Problem: "No module named 'aiohttp'"

**Solution:** Wait longer or check Python version
1. Workflow might still be installing
2. Or your `requirements.txt` doesn't include it
3. Add to requirements.txt:
   ```
   aiohttp
   urllib3
   requests
   ```

### Problem: "fs token expired"

**Solution:** Get new token
1. Go to https://accountscenter.meta.com/profiles/YOUR_ID/username/
2. Open DevTools → **Application → Cookies**
3. Find cookie named `fs`
4. Copy value
5. Update `CREDS_JSON` secret

---

## Advanced: Local Testing

Before deploying to GitHub Actions, test locally:

```bash
# Test with environment variables
export NAMES_LIST="lists/names.txt"
export WEBHOOK_URL="https://discord.com/api/webhooks/..."
export PROXIES="http://user:pass@host:port"
export SNIPE_MODE="true"

python metasnie_headless_cli.py --env
```

Or with arguments:
```bash
python metasnie_headless_cli.py \
  --names lists/names.txt \
  --webhook "https://discord.com/.../webhooks/..." \
  --proxies "http://5m12gq1d:40b1f1e9@p.tokenu.to:10000,http://..."
```

---

## Summary

✅ **Step 1:** Add files to repo
✅ **Step 2:** Set GitHub Secrets (CREDS_JSON, WEBHOOK_URL, PROXIES)
✅ **Step 3:** Add names to `lists/names.txt`
✅ **Step 4:** Test with manual trigger
✅ **Step 5:** Set auto schedule
✅ **Step 6:** Get Discord notifications
✅ **Step 7:** Monitor performance

**That's it!** Your sniper is now running 24/7 on GitHub.

---

## What Happens

```
Every minute (or your schedule):
├─ GitHub starts the workflow
├─ Python installs dependencies (first run only)
├─ Loads your credentials & names list
├─ Rotates through proxies (if set)
├─ Checks all names ~500 times
├─ If AVAILABLE found → snipes all accounts
├─ Sends Discord webhook notification
└─ Stops (workflow ends)

Next cycle: Repeat
```

---

## Pro Tips

1. **Multiple name lists:** Create different secrets for different lists
2. **Different schedules:** Create multiple workflows (e.g., one every minute, one every hour)
3. **Alert levels:** Use Discord role mentions: `"<@&ROLE_ID> Name available!"`
4. **Rotate proxies:** Update PROXIES secret weekly to prevent blocks

---

Need help? Check:
- Workflow logs: **Actions → Latest run**
- Secrets: **Settings → Secrets and variables → Actions**
- Syntax: https://docs.github.com/en/actions
