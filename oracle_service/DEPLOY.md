# Deploy Oracle Service - One Time Setup

**Deploy once, everyone uses it forever. True plug-and-play.**

---

## Why Deploy?

Instead of every user running their own oracle:
- ✅ Deploy once to cloud (Railway, Render, Heroku)
- ✅ Users just install and use (no oracle setup)
- ✅ True plug-and-play experience
- ✅ Centralized, production-ready oracle

---

## Quick Deploy (Railway - Easiest)

### 1. Generate Oracle Keypair

```bash
python3 -m loggerheads.oracle_secure --generate
```

This creates: `~/.loggerheads/oracle-keypair.json`

### 2. Convert Keypair to Environment Variable

```bash
python3 oracle_service/prepare_deploy.py
```

This outputs something like:
```
ORACLE_KEYPAIR_JSON=[198,80,45,77,...]
```

Copy this value.

### 3. Deploy to Railway

**Option A: Via Railway CLI**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create new project
railway init

# Add environment variable
railway variables set ORACLE_KEYPAIR_JSON="[198,80,45,...]"

# Deploy
railway up
```

**Option B: Via Railway Dashboard**
1. Go to https://railway.app
2. Sign up / Login
3. New Project → Deploy from GitHub
4. Connect your repository
5. Select `oracle_service` directory
6. Add environment variable:
   - Key: `ORACLE_KEYPAIR_JSON`
   - Value: `[198,80,45,...]` (from step 2)
7. Deploy!

### 4. Get Your Oracle URL

Railway will give you a URL like:
```
https://kapture-oracle-production.up.railway.app
```

### 5. Update Client Default

Edit `loggerheads/oracle_client.py`:
```python
def _get_default_oracle_url(self) -> str:
    """Get oracle URL from environment or use default."""
    import os
    return os.getenv('KAPTURE_ORACLE_URL', 'https://kapture-oracle-production.up.railway.app')
```

### 6. Commit and Push

```bash
git add loggerheads/oracle_client.py
git commit -m "Update oracle URL to production deployment"
git push
```

### 7. Test It

```bash
curl https://kapture-oracle-production.up.railway.app/health
```

Should return:
```json
{
  "status": "healthy",
  "oracle_pubkey": "3fRGj4mzWot9Vmdb...",
  "timestamp": "2025-10-27..."
}
```

---

## Alternative: Deploy to Render

### 1. Prepare Keypair (Same as above)

```bash
python3 oracle_service/prepare_deploy.py
```

### 2. Deploy to Render

1. Go to https://render.com
2. Sign up / Login
3. New → Web Service
4. Connect your repository
5. Settings:
   - **Name:** kapture-oracle
   - **Root Directory:** `oracle_service`
   - **Build Command:** `pip install -r requirements.txt && cd .. && pip install -e .`
   - **Start Command:** `python3 app.py`
6. Add environment variable:
   - Key: `ORACLE_KEYPAIR_JSON`
   - Value: `[198,80,45,...]`
7. Create Web Service

### 3. Get URL and Update Client (Same as Railway)

---

## Alternative: Deploy to Heroku

### 1. Prepare Keypair (Same as above)

### 2. Deploy to Heroku

```bash
# Install Heroku CLI
brew tap heroku/brew && brew install heroku

# Login
heroku login

# Create app
heroku create kapture-oracle

# Set environment variable
heroku config:set ORACLE_KEYPAIR_JSON="[198,80,45,...]"

# Deploy
git subtree push --prefix oracle_service heroku main

# Or if that fails:
git push heroku `git subtree split --prefix oracle_service main`:main --force
```

### 3. Get URL

```bash
heroku open
```

Your URL will be: `https://kapture-oracle.herokuapp.com`

---

## After Deployment

### Update Documentation

Remove all "start oracle service" instructions from:
- `README.md`
- `docs/TESTING_GUIDE.md`
- `QUICKSTART_ORACLE.md`

Users no longer need to do anything with the oracle!

### User Experience Now

**Before (Complex):**
```bash
# Terminal 1: Start oracle
python3 oracle_service/app.py

# Terminal 2: Use app
loggerheads
```

**After (Plug-and-Play):**
```bash
# Just use it!
loggerheads
```

That's it. Oracle is already running in the cloud.

---

## Verify Deployment

### Test Health

```bash
curl https://your-oracle-url.com/health
```

### Test from Client

```bash
python3 -c "
from loggerheads.oracle_client import get_oracle_client

oracle = get_oracle_client()
health = oracle.health_check()
print(f'Oracle: {health[\"oracle_pubkey\"]}')
print(f'Status: {health[\"status\"]}')
"
```

### Create Test Vault

```bash
loggerheads
# Choose: Employer
```

If vault creation works, oracle is working!

---

## Cost

### Railway
- **Free Tier:** $5 credit/month
- **Enough for:** ~500 hours of runtime
- **Cost after free:** ~$0.01/hour

### Render
- **Free Tier:** Yes (with sleep after inactivity)
- **Paid:** $7/month for always-on

### Heroku
- **Free Tier:** Removed (now requires payment)
- **Paid:** $7/month minimum

**Recommendation:** Railway (best free tier)

---

## Monitoring

### Railway Dashboard
- View logs
- Monitor CPU/memory
- Track requests
- Set up alerts

### Add Basic Monitoring to Oracle

Edit `oracle_service/app.py`:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

This will log all submissions to Railway/Render dashboard.

---

## Security

### Environment Variable Security

✅ **Safe:** ORACLE_KEYPAIR_JSON in Railway/Render env vars
- Encrypted at rest
- Not visible in logs
- Only accessible by your service

❌ **Unsafe:** Committing keypair to git
- Never commit `oracle-keypair.json`
- It's in `.gitignore` already

### Production Hardening

After deployment, add:

1. **Rate Limiting**
```python
from flask_limiter import Limiter

limiter = Limiter(app, default_limits=["200 per day", "50 per hour"])

@app.route('/submit-hours', methods=['POST'])
@limiter.limit("10 per hour")
def submit_hours_endpoint():
    ...
```

2. **Request Logging**
```python
@app.before_request
def log_request():
    logging.info(f"{request.method} {request.path} from {request.remote_addr}")
```

3. **Error Monitoring (Sentry)**
```python
import sentry_sdk
sentry_sdk.init("your-dsn")
```

---

## Troubleshooting

### "Build failed"

**Railway/Render:**
- Check build logs
- Ensure `requirements.txt` has all dependencies
- Verify Python version compatibility

### "Oracle not loading"

**Check environment variable:**
```bash
# Railway
railway variables

# Render
# Check in dashboard under Environment

# Heroku
heroku config
```

### "Cannot reach oracle"

**Check URL:**
- Is service running? (Check dashboard)
- Is URL correct in `oracle_client.py`?
- Try health check: `curl https://your-url/health`

### "Vault trusts different oracle"

**You changed oracle!**
- Delete old test vaults
- Create new vaults with new oracle
- Or keep using old oracle if you still have the keypair

---

## Updating Deployed Oracle

### Code Changes

```bash
git add oracle_service/
git commit -m "Update oracle service"
git push
```

Railway/Render auto-deploys on push!

### Changing Oracle Keypair (Rare)

**WARNING:** This breaks all existing vaults!

Only do this if:
- Starting fresh
- Security compromise
- Testing new features

Steps:
1. Generate new keypair
2. Update `ORACLE_KEYPAIR_JSON` env var
3. Restart service
4. All users must create new vaults

---

## Success Checklist

- [ ] Oracle deployed to cloud
- [ ] Health check returns 200
- [ ] Oracle pubkey is stable (not changing)
- [ ] Updated `oracle_client.py` with production URL
- [ ] Removed "start oracle" from user docs
- [ ] Tested vault creation
- [ ] Tested submission
- [ ] Monitoring enabled

---

## Result

**Users now experience:**

1. Install: `pip install -e .`
2. Run: `loggerheads`
3. Done!

**No oracle setup, no services to start, no complexity.**

**Pure plug-and-play. That's the goal!**
