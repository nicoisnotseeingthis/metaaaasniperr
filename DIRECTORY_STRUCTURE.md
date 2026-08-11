# Directory Structure — What Goes Where

---

## Your Final Repo Layout

```
metasnie/
│
├── 📄 main.py                           (Original GUI version)
├── 📄 headless.py                       (Your original headless version)
├── 📄 metasnie_headless_cli.py          ← NEW (GitHub Actions compatible)
├── 📄 requirements.txt
├── 📄 checker_config.json
│
├── 📁 lists/
│   └── names.txt                        (Usernames to snipe)
│
├── 📁 creds/
│   └── creds.json                       (Your Meta accounts - GITIGNORE this!)
│
├── 📁 .github/                          ← NEW
│   └── 📁 workflows/
│       └── sniper.yml                   ← NEW (GitHub Actions workflow)
│
└── 📁 .github/
    └── .gitignore                       (Ignore sensitive files)
```

---

## File-by-File Breakdown

### 🟢 Keep as-is (Already in your repo)

```
main.py
├─ GUI version
├─ Used locally
└─ Still works as before

headless.py
├─ Your original headless mode
├─ Can still use locally
└─ Not needed for GitHub Actions

requirements.txt
├─ Must include: aiohttp, requests, urllib3
└─ GitHub Actions will install these

lists/names.txt
├─ One username per line
├─ Example:
│   coolname1
│   testuser
│   dreamname
└─ Add/update as needed

creds/creds.json
├─ Your Meta account credentials
├─ ⚠️ NEVER commit to public repo
├─ Add to .gitignore (see below)
└─ Store in GitHub Secrets instead
```

### 🔴 NEW Files (Add these)

```
metasnie_headless_cli.py
├─ Headless CLI runner
├─ Works with or without GitHub Actions
├─ No GUI dependencies
├─ Use this for testing locally too
└─ Commit to repo

.github/workflows/sniper.yml
├─ GitHub Actions workflow
├─ Runs automatically on schedule
├─ Pulls secrets from GitHub
└─ Commit to repo
```

### 🟡 Configuration (GitHub Secrets - NOT in repo)

These go in GitHub settings, NOT in files:

```
GitHub Secrets (Settings → Secrets and variables → Actions)
├─ CREDS_JSON          (Your Meta accounts)
├─ WEBHOOK_URL         (Discord notifications)
└─ PROXIES             (Proxy list)

⚠️ NEVER store these in the repo itself!
⚠️ They're only visible in GitHub settings
```

---

## Step-by-Step File Setup

### 1️⃣ Create .gitignore (Protect Secrets)

```bash
# In repo root
cat > .gitignore << 'EOF'
# Ignore sensitive files (never commit these)
creds/
creds.json
creds/*.json
*.pyc
__pycache__/
.env
.env.local
EOF

git add .gitignore
git commit -m "Add gitignore"
git push
```

### 2️⃣ Add Headless CLI

```bash
# Copy to repo root
cp /path/to/metasnie_headless_cli.py ./metasnie_headless_cli.py

# Check it's there
ls -la metasnie_headless_cli.py

# Commit it
git add metasnie_headless_cli.py
git commit -m "Add headless CLI for GitHub Actions"
git push
```

### 3️⃣ Create GitHub Actions Workflow

```bash
# Create directory
mkdir -p .github/workflows

# Create workflow file
cat > .github/workflows/sniper.yml << 'WORKFLOW_EOF'
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
          [ -f requirements.txt ] && pip install -r requirements.txt || true
      
      - run: |
          mkdir -p lists creds
          [ ! -f lists/names.txt ] && echo -e "testname1\ntestname2" > lists/names.txt || true
          echo '${{ secrets.CREDS_JSON }}' > creds/creds.json
      
      - run: python metasnie_headless_cli.py --env --proxies "$PROXIES" --webhook "${{ secrets.WEBHOOK_URL }}"
        env:
          NAMES_LIST: lists/names.txt
          WEBHOOK_URL: ${{ secrets.WEBHOOK_URL }}
          PROXIES: ${{ secrets.PROXIES }}
          CONCURRENCY: 500
          SNIPE_MODE: 'true'
        timeout-minutes: 5
WORKFLOW_EOF

# Check it's there
ls -la .github/workflows/sniper.yml

# Commit it
git add .github/workflows/
git commit -m "Add GitHub Actions workflow"
git push
```

### 4️⃣ Update Your Names List (Locally, COMMIT)

```bash
# Create/update lists/names.txt
cat > lists/names.txt << 'EOF'
coolname1
coolname2
dreamusername
testsnipe
anotheruser
EOF

# Commit and push
git add lists/names.txt
git commit -m "Update names to snipe"
git push
```

### 5️⃣ Add Secrets to GitHub (WEB UI ONLY - DON'T COMMIT)

Go to: https://github.com/YOUR_USERNAME/metasnie/settings/secrets/actions

**Add 3 secrets:**

1. **CREDS_JSON**
   ```json
   [{"PROFILE_ID":"123456","fs":"ABC...XYZ","username":"yourname","sniped":null,"rate_limited":false,"rate_limited_since":null,"sniper_enabled":true,"locked":false}]
   ```

2. **WEBHOOK_URL**
   ```
   https://discord.com/api/webhooks/12345/ABCDEF...
   ```

3. **PROXIES**
   ```
   http://5m12gq1d:40b1f1e9@p.tokenu.to:10000
   http://5m12gq1d:40b1f1e9@p.tokenu.to:10001
   ...
   ```

---

## Which Files Go Where

| File | Location | Commit to Git? | Contains Secrets? | Notes |
|------|----------|---|---|---|
| `main.py` | Root | ✅ Yes | ❌ No | GUI version |
| `headless.py` | Root | ✅ Yes | ❌ No | Your CLI version |
| `metasnie_headless_cli.py` | Root | ✅ Yes | ❌ No | NEW for GitHub Actions |
| `requirements.txt` | Root | ✅ Yes | ❌ No | Keep as-is |
| `lists/names.txt` | lists/ | ✅ Yes | ❌ No | Public usernames OK |
| `creds/creds.json` | creds/ | ❌ NO | ✅ YES | Add to .gitignore! |
| `.github/workflows/sniper.yml` | .github/workflows/ | ✅ Yes | ❌ No | References secrets by name |
| `CREDS_JSON` | GitHub Secrets | N/A | ✅ YES | Not a file, web only |
| `WEBHOOK_URL` | GitHub Secrets | N/A | ✅ YES | Not a file, web only |
| `PROXIES` | GitHub Secrets | N/A | ❌ No | Not a file, web only |

---

## Git Commands Reference

```bash
# Check what will be committed
git status

# Add specific files
git add metasnie_headless_cli.py
git add .github/workflows/sniper.yml
git add lists/names.txt

# Add all (except .gitignore'd)
git add .

# Commit
git commit -m "Add GitHub Actions setup"

# Push to GitHub
git push origin main

# Verify files in repo
git ls-files
```

---

## Verify Setup

### ✅ Check Repo Has Files

```bash
# Should show these files
git ls-files | grep -E "(metasnie_headless_cli|\.github/workflows|lists/names)"

# Output should be:
# .github/workflows/sniper.yml
# lists/names.txt
# metasnie_headless_cli.py
```

### ✅ Check Secrets Are Set

Go to: https://github.com/YOUR_USERNAME/metasnie/settings/secrets/actions

Should show:
- ✅ CREDS_JSON
- ✅ WEBHOOK_URL (optional)
- ✅ PROXIES (optional)

### ✅ Check .gitignore Works

```bash
# This should NOT show:
git ls-files | grep creds

# This should NOT output anything (good)
```

### ✅ Test Workflow

Go to: https://github.com/YOUR_USERNAME/metasnie/actions

Click **Metasnie Sniper** → **Run workflow**

Should see:
- Workflow runs
- Python installs dependencies
- Gets credentials from secrets
- Starts checking names
- Gets results in logs

---

## Common Mistakes

❌ **Mistake 1:** Committing `creds/creds.json`

```bash
# DON'T do this:
git add creds/creds.json
git push

# DO this instead:
# Add to .gitignore, store in GitHub Secrets
```

❌ **Mistake 2:** Secret name wrong

```bash
# Wrong (won't work):
- name: CREDS

# Right (must match exactly):
- name: CREDS_JSON
```

❌ **Mistake 3:** Multi-line secrets

```bash
# Wrong (GitHub doesn't allow):
WEBHOOK_URL = https://discord.com/api/webhooks/...
EXTRA_LINE

# Right (single line only):
WEBHOOK_URL = https://discord.com/api/webhooks/...
```

❌ **Mistake 4:** Forgetting to push

```bash
# You edited files locally but didn't push
git add .
git commit -m "..."
git push  # ← DON'T forget this!
```

---

## Example: Complete Setup from Scratch

```bash
# 1. Clone your repo
git clone https://github.com/YOUR_USERNAME/metasnie.git
cd metasnie

# 2. Add .gitignore
echo "creds/" >> .gitignore

# 3. Copy headless CLI
cp /path/to/metasnie_headless_cli.py ./

# 4. Create workflow
mkdir -p .github/workflows
# (Copy workflow file content from YAML above)

# 5. Update names
echo -e "coolname1\ncoolname2\ncoolname3" > lists/names.txt

# 6. Commit everything
git add .gitignore metasnie_headless_cli.py .github/workflows/ lists/names.txt
git commit -m "Setup GitHub Actions sniper"
git push

# 7. Go to GitHub and add 3 secrets (web UI)
# Done! 🎉
```

---

## File Sizes

These should be reasonable:

```
metasnie_headless_cli.py    ~20 KB (fine)
.github/workflows/sniper.yml ~1 KB (fine)
lists/names.txt             ~1-10 KB (depends on list size)
creds/creds.json            ~200-500 bytes (JSON)
```

---

## Summary

| What | Where | How |
|------|-------|-----|
| **Code files** | Root directory | Commit to git |
| **Names list** | `lists/names.txt` | Commit to git |
| **Credentials** | GitHub Secrets | Never in repo |
| **Workflow** | `.github/workflows/` | Commit to git |
| **Config** | Environment variables in workflow | References secrets |

You're all set! 🚀
