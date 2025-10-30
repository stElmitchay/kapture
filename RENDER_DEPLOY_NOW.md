# Deploy Oracle to Render - Step by Step

## What You Need

1. GitHub account
2. Render account (free)
3. 10 minutes

---

## Step 1: Get Oracle Keypair Ready

```bash
# Check if you have oracle keypair
ls ~/.loggerheads/oracle-keypair.json

# If not, generate one:
python3 -m loggerheads.oracle_secure --generate
```

**Important:** Copy this file's contents. You'll need it for Render.

```bash
cat ~/.loggerheads/oracle-keypair.json
```

Copy the entire JSON output (it's just one line). Should look like:
```
[1,2,3,4,5...] (64 numbers)
```

---

## Step 2: Push to GitHub

If not already on GitHub:

```bash
cd /Users/mitch_1/daily_log_ai

# Initialize git (if needed)
git add .
git commit -m "Add oracle service"

# Create new repo on GitHub: https://github.com/new
# Name it: kapture

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/kapture.git
git push -u origin main
```

---

## Step 3: Create Render Account

1. Go to: https://render.com
2. Click **Get Started**
3. Sign up with **GitHub** (easiest)
4. Authorize Render to access your repos

---

## Step 4: Create Web Service

1. Click **New +** (top right)
2. Select **Web Service**
3. Click **Connect a repository**
4. Find your **kapture** repo → Click **Connect**

---

## Step 5: Configure Build Settings

Render shows you a form. Fill it in:

**Name:**
```
kapture-oracle
```

**Region:**
```
Oregon (US West) or closest to you
```

**Branch:**
```
main
```

**Root Directory:**
```
oracle_service
```

**Runtime:**
```
Python 3
```

**Build Command:**
```
pip install -r requirements.txt && pip install solders solana anchorpy
```

**Start Command:**
```
python3 app.py
```

---

## Step 6: Add Environment Variables

Still on the same page, scroll to **Environment Variables**.

Click **Add Environment Variable** and add these:

### Variable 1: ORACLE_KEYPAIR_JSON
- **Key:** `ORACLE_KEYPAIR_JSON`
- **Value:** Paste the JSON array from Step 1 (the [1,2,3,4...] numbers)

### Variable 2: PORT
- **Key:** `PORT`
- **Value:** `10000`

### Variable 3: SOLANA_NETWORK
- **Key:** `SOLANA_NETWORK`
- **Value:** `devnet`

### Variable 4: PYTHONPATH
- **Key:** `PYTHONPATH`
- **Value:** `/opt/render/project/src`

---

## Step 7: Deploy

1. Scroll down
2. Select **Free** plan
3. Click **Create Web Service**

Render will:
- Clone your repo
- Install dependencies
- Start oracle service
- Takes ~3-5 minutes

**Watch the logs** - you'll see:
```
==> Installing dependencies
==> Starting service
🔮 KAPTURE ORACLE SERVICE
✅ Oracle Public Key: ...
📡 Starting API server...
```

---

## Step 8: Get Your Oracle URL

Once deployed (green checkmark ✓):

1. Look at top of page for URL
2. Should be: `https://kapture-oracle.onrender.com`
3. Copy this URL

---

## Step 9: Test It Works

```bash
# Test health endpoint
curl https://kapture-oracle.onrender.com/health
```

Should return:
```json
{
  "status": "healthy",
  "oracle_pubkey": "7xJ9XxQp...",
  "timestamp": "2025-10-30..."
}
```

**If you get error:** Oracle is still starting up. Wait 30 seconds and try again.

---

## Step 10: Update Your Code (Make it Seamless)

Now we'll hardcode this URL so users don't need to configure anything.

I'll do this next - just need your deployed URL from Step 8.

---

## Troubleshooting

### "Application failed to respond"

**Issue:** Dependencies not installed correctly

**Fix:** Update Build Command:
```bash
cd .. && pip install -e . && cd oracle_service && pip install -r requirements.txt
```

### "Oracle keypair not found"

**Issue:** Environment variable not set correctly

**Fix:**
1. Go to **Environment** tab
2. Check `ORACLE_KEYPAIR_JSON` is set
3. Value should be JSON array `[1,2,3...]`
4. Click **Manual Deploy** → **Deploy latest commit**

### "Cannot connect to Solana"

**Issue:** RPC connection

**Fix:** Add environment variable:
```
RPC_URL=https://api.devnet.solana.com
```

---

## Important: Free Tier Behavior

**Render Free Tier:**
- Sleeps after 15 minutes of inactivity
- First request takes ~30 seconds to wake up
- **This is fine for testing!**

**For Production:**
- Upgrade to paid ($7/month)
- Oracle stays awake 24/7
- Instant responses

---

## What's Your Oracle URL?

Once you complete Step 8, tell me your URL and I'll:
1. Update the code to use it by default
2. Make the experience seamless for end users
3. Your 3 test volunteers won't need to set any environment variables

**After deployment, end users just run:**
```bash
pip install kapture
kapture
```

**And it works!** No configuration needed.
