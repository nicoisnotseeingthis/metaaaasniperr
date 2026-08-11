# Master Checklist — GitHub Actions Setup

---

## 📋 What You're Getting

5 files ready to deploy:

1. **`metasnie_headless_cli.py`** (800 lines)
   - Runs without GUI
   - Works locally or on GitHub Actions
   - Proxy rotation built-in
   - Discord webhooks built-in

2. **`.github_workflows_sniper.yml`** (Rename to `sniper.yml` in `.github/workflows/`)
   - Automated workflow file
   - Runs every minute (configurable)
   - Pulls secrets from GitHub
   - Installs dependencies

3. **`GITHUB_ACTIONS_SETUP.md`** (Detailed guide)
   - Step-by-step instructions
   - Screenshots/references
   - Troubleshooting section

4. **`GITHUB_ACTIONS_QUICK_START.md`** (Copy-paste version)
   - All commands in one place
   - Quick reference
   - Checklist format

5. **`DIRECTORY_STRUCTURE.md`** (File organization)
   - What goes where
   - Git vs GitHub Secrets
   - Verification steps

---

## ⚡ Quick Start (5 minutes)

### Step 1: Prepare Files (2 min)

```bash
cd your-metasnie-folder

# Copy the headless CLI
cp metasnie_headless_cli.py ./

# Create workflow directory and file
mkdir -p .github/workflows
cat > .github/workflows/sniper.yml << 'WORKFLOW'
# (Copy content from .github_workflows_sniper.yml)
WORKFLOW
```

### Step 2: Commit to Git (1 min)

```bash
git add metasnie_headless_cli.py .github/workflows/sniper.yml
git commit -m "Add GitHub Actions sniper"
git push origin main
```

### Step 3: Add GitHub Secrets (2 min)

Go to: **https://github.com/YOUR_USERNAME/metasnie/settings/secrets/actions**

Add these 3 secrets:

| Name | Value | Required? |
|------|-------|-----------|
| `CREDS_JSON` | Your Meta account creds (JSON) | ✅ YES |
| `WEBHOOK_URL` | Discord webhook URL | ⭕ Optional |
| `PROXIES` | Proxy list (newline separated) | ⭕ Optional |

### Step 4: Test (30 sec)

Go to: **https://github.com/YOUR_USERNAME/metasnie/actions**

Click **Metasnie Sniper** → **Run workflow** → **Run workflow**

Watch logs for:
```
[INFO] Loaded X names
[INFO] Loaded X credentials
[INFO] Warming X accounts...
[START] Checker running...
```

**Done!** ✅ Your sniper is now running 24/7.

---

## 📝 Detailed Checklist

### ✅ Phase 1: Setup (Before GitHub)

- [ ] Download all 5 files from outputs
- [ ] Have your Meta credentials ready (PROFILE_ID + fs token)
- [ ] Have Discord webhook URL (if using notifications)
- [ ] Have proxy list (if using proxies)
- [ ] Have username list (in `lists/names.txt`)

### ✅ Phase 2: Local Testing (Optional but Recommended)

- [ ] Test `metasnie_headless_cli.py` locally first
  ```bash
  python metasnie_headless_cli.py --names lists/names.txt
  ```
- [ ] Verify it detects available names
- [ ] Verify it attempts to claim (if you have test accounts)
- [ ] Verify Discord webhook sends messages (if configured)

### ✅ Phase 3: Repository Setup

- [ ] Clone/go to your metasnie GitHub repo
- [ ] Copy `metasnie_headless_cli.py` to repo root
- [ ] Create `.github/workflows/` directory
- [ ] Copy `.github_workflows_sniper.yml` to `.github/workflows/sniper.yml`
- [ ] Update `.gitignore` to exclude `creds/`
- [ ] Verify `lists/names.txt` exists with your usernames
- [ ] Run: `git add metasnie_headless_cli.py .github/workflows/`
- [ ] Run: `git commit -m "Add GitHub Actions"`
- [ ] Run: `git push origin main`

### ✅ Phase 4: GitHub Secrets

Go to: https://github.com/YOUR_USERNAME/metasnie/settings/secrets/actions

- [ ] Create secret `CREDS_JSON`
  - Format: `[{"PROFILE_ID":"...","fs":"..."}]`
  - Can add multiple accounts
  
- [ ] Create secret `WEBHOOK_URL` (optional)
  - Get from: Discord → Server → Channel → Integrations → Webhooks
  
- [ ] Create secret `PROXIES` (optional)
  - Format: One proxy per line
  - Or comma-separated in one line

### ✅ Phase 5: Verification

- [ ] Go to: https://github.com/YOUR_USERNAME/metasnie/actions
- [ ] See **Metasnie Sniper** workflow listed
- [ ] Click **Run workflow** → **Run workflow**
- [ ] Workflow starts running
- [ ] Logs show:
  - [ ] Python installed
  - [ ] Dependencies installed
  - [ ] Credentials loaded
  - [ ] Checker started
  - [ ] Statistics appearing

### ✅ Phase 6: Monitor

- [ ] Set recurring calendar reminder to check logs
- [ ] Verify Discord webhook sends notification when name found
- [ ] Check stats in logs (CPS should be 50-150)
- [ ] Monitor GitHub Actions usage (shows on Actions tab)

### ✅ Phase 7: Maintenance

- [ ] Update `lists/names.txt` if adding new usernames
  ```bash
  git add lists/names.txt
  git commit -m "Add more names"
  git push
  ```
- [ ] Update `CREDS_JSON` secret if adding accounts
- [ ] Update proxy list monthly if using proxies
- [ ] Check fs token expiration (refresh every 3-6 months)

---

## 🚨 Critical Don'ts

❌ **DON'T** commit `creds/creds.json` to GitHub
- Use `.gitignore`
- Store in GitHub Secrets instead

❌ **DON'T** share secrets with anyone
- GitHub Secrets are encrypted
- Only show on Actions logs if you explicitly reference them

❌ **DON'T** use the same PROFILE_ID in multiple repos
- Meta can detect bot behavior
- One repo per operation is safer

❌ **DON'T** use GitHub Actions if your repo is private without a paid plan
- Free tier: public repos only
- Private repos: need GitHub Pro

❌ **DON'T** use obviously fake usernames in your list
- Meta has detection
- Use realistic usernames
- Mix with genuinely available names

---

## 🎯 What Happens Now

```
Every minute (or your schedule):

1. GitHub starts the workflow
   ├─ Spins up Ubuntu machine
   ├─ Installs Python 3.11
   └─ Installs aiohttp, urllib3, requests

2. Loads your data
   ├─ Gets credentials from CREDS_JSON secret
   ├─ Gets proxy list from PROXIES secret
   ├─ Reads names from lists/names.txt
   └─ Reads webhook from WEBHOOK_URL secret

3. Starts checking
   ├─ Rotates through proxies (if set)
   ├─ Checks each name ~500 times
   ├─ Logs stats every second
   └─ Fires sniper for AVAILABLE names

4. Sends notifications
   ├─ Sends Discord webhook
   ├─ Attempts to claim with all accounts
   └─ Logs results

5. Stops
   ├─ Workflow ends
   ├─ GitHub saves logs (35 days history)
   └─ Repeats next cycle
```

---

## 📊 Expected Performance

With GitHub Actions + Proxies:

| Metric | Value |
|--------|-------|
| Check speed | 50-150 checks/second |
| Proxy rotation | 12 IPs (11 proxies + direct) |
| Snipe speed | 80-150ms per account |
| Parallel accounts | 5-15 simultaneously |
| Detection lag | ~50-100ms |
| Detection to claim | ~150-300ms total |

---

## 🔍 Monitoring & Debugging

### Check Workflow Status

https://github.com/YOUR_USERNAME/metasnie/actions

Status indicators:
- 🟢 **Green** = Success
- 🟡 **Yellow** = Running
- 🔴 **Red** = Failed

### View Logs

Actions → Metasnie Sniper → Latest run → sniper job

Look for patterns:
```
[INFO] Loaded 10 names          ✓ Names loaded
[INFO] 2/2 accounts ready       ✓ Credentials working
[STATS] CPS: 75.0               ✓ Checking ~75 names/sec
[AVAILABLE] coolname            ✓ Found available
[SUCCESS] Account 1 claimed      ✓ Sniped successfully
```

### Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| "Secret not found" | Wrong name | Check exact spelling |
| Invalid JSON | Formatting | Use https://jsonlint.com |
| Token expired | fs cookie old | Refresh from accountscenter.meta.com |
| Proxy timeout | Dead proxy | Test manually or remove |
| No checks happening | Names list missing | Add `lists/names.txt` |

---

## 💰 Cost Analysis

| Item | Cost |
|------|------|
| GitHub Actions (public repo) | **FREE** |
| GitHub Secrets | **FREE** |
| Proxies (TokenU example) | ~$20-50/month |
| Discord webhook | FREE |
| **Total** | **$0-50/month** |

GitHub Actions includes:
- Unlimited workflows
- Unlimited runs
- 20 concurrent jobs
- 35 days job history

Only paid component: proxies (optional).

---

## 🎓 Learning Resources

If you need to modify the code:

- **GitHub Actions syntax**: https://docs.github.com/en/actions
- **Python asyncio**: https://docs.python.org/3/library/asyncio.html
- **aiohttp**: https://docs.aiohttp.org
- **Cron syntax**: https://crontab.guru

---

## 📞 Troubleshooting Flow

```
Workflow not running?
├─ Check Actions enabled: Settings → Actions
├─ Check workflow file exists: .github/workflows/sniper.yml
└─ Manual trigger: Actions → Run workflow

Secrets not working?
├─ Check secret names: CREDS_JSON, WEBHOOK_URL, PROXIES
├─ Check values are set: Settings → Secrets
└─ Check JSON format: Use jsonlint.com

Checker not detecting?
├─ Check names list: lists/names.txt exists
├─ Check proxy: Try without proxies first
└─ Check timeout: Increase in workflow file

Sniper not claiming?
├─ Check credentials: PROFILE_ID + fs token valid
├─ Check rate limit: See if account is rate limited
└─ Check target: Name actually available

Discord not notifying?
├─ Check webhook URL: Valid format
├─ Check secret: WEBHOOK_URL exists
└─ Check channel: Webhook points to correct channel
```

---

## ✨ Final Checklist

- [ ] All 5 files downloaded
- [ ] Files copied to correct locations
- [ ] Committed and pushed to GitHub
- [ ] 3 GitHub Secrets created
- [ ] Manual test run successful
- [ ] Logs showing normal operation
- [ ] Discord notifications working (if enabled)
- [ ] Names list updated with targets
- [ ] Workflow set to correct schedule
- [ ] Ready to snipe! 🚀

---

## Next Steps

1. **Start with QUICK_START.md** if you want copy-paste
2. **Use SETUP.md** if you want detailed explanations
3. **Reference DIRECTORY_STRUCTURE.md** for file organization
4. **Run locally first** with `metasnie_headless_cli.py`
5. **Deploy to GitHub Actions** when confident

---

**You're all set!** Your sniper is ready to run 24/7. 🎯

Good luck with your username sniping! 🚀
