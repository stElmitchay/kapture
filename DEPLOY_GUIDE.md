# Oracle Service Deployment Guide

Complete step-by-step guide to deploy the Kapture Oracle Service to production.

---

## Overview

The oracle service is a Flask API that:
- Verifies employee work submissions
- Signs blockchain transactions with oracle keypair
- Submits validated hours to Solana smart contract

**Architecture:**
```
Employee Client → Oracle API → Solana Blockchain
    (POSTs)      (Verifies)      (Validates)
```

---

## Prerequisites

Before deploying, ensure you have:

- [ ] Oracle keypair generated (`python3 -m loggerheads.oracle_secure --generate`)
- [ ] Solana CLI installed
- [ ] Tested locally (oracle service runs on localhost)
- [ ] Git repository with oracle_service/ directory
- [ ] Account on deployment platform (Railway/Render/Heroku)

---

## Deployment Options

Choose your platform:

1. **Railway** - Easiest, automatic deployments, $5/month
2. **Render** - Free tier available, similar to Railway
3. **Heroku** - Classic PaaS, requires credit card
4. **AWS/GCP** - Most control, more complex
5. **DigitalOcean** - VPS, manual setup

---

## Option 1: Railway (Recommended)

**Why Railway:**
- Automatic deployments from GitHub
- Built-in environment variables
- HTTPS out of the box
- $5/month (~750 hours)
- Dead simple

### Step 1: Prepare Oracle Keypair

```bash
# Generate if you haven't already
python3 -m loggerheads.oracle_secure --generate

# This creates: ~/.loggerheads/oracle-keypair.json
# Copy the base64 encoded version for Railway
cat ~/.loggerheads/oracle-keypair.json | base64
```

Copy the base64 output. You'll need this for environment variables.

### Step 2: Push to GitHub

```bash
cd /path/to/daily_log_ai

# Create new repo on GitHub first, then:
git remote add origin https://github.com/yourusername/kapture.git
git add .
git commit -m "Add oracle service"
git push -u origin main
```

### Step 3: Deploy to Railway

1. **Go to Railway:** https://railway.app
2. **Sign up** with GitHub
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose your kapture repository**
6. **Railway auto-detects Python** ✅

### Step 4: Configure Environment Variables

In Railway dashboard:

1. Click your project → **Variables** tab
2. Add these variables:

```bash
# Oracle keypair (base64 encoded)
ORACLE_KEYPAIR_BASE64=<paste base64 from step 1>

# Port (Railway provides this automatically)
PORT=5001

# Solana network
SOLANA_NETWORK=devnet

# RPC URL (optional, uses default if not set)
RPC_URL=https://api.devnet.solana.com
```

### Step 5: Create railway.json

Railway needs to know how to start your app:

```bash
# Already created in oracle_service/railway.json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd oracle_service && pip install -r requirements.txt && python3 app.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100
  }
}
```

### Step 6: Deploy

Railway automatically deploys when you push to GitHub!

```bash
git add railway.json
git commit -m "Add Railway config"
git push
```

**Railway will:**
1. Clone your repo
2. Install dependencies
3. Start the oracle service
4. Assign a public URL

### Step 7: Get Your Oracle URL

In Railway dashboard:
- Click **Settings** → **Domains**
- You'll see something like: `kapture-oracle-production.up.railway.app`
- Test it: `curl https://kapture-oracle-production.up.railway.app/health`

### Step 8: Update Clients

Tell your users to set:

```bash
export KAPTURE_ORACLE_URL=https://kapture-oracle-production.up.railway.app
```

**Done!** Your oracle is live 🎉

---

## Option 2: Render

**Why Render:**
- Free tier (750 hours/month)
- Good for testing
- Easy setup

### Step 1: Prepare Repository

```bash
cd /path/to/daily_log_ai

# Create render.yaml (already exists in oracle_service/)
# Commit and push to GitHub
git add .
git commit -m "Add Render config"
git push
```

### Step 2: Create Render Account

1. Go to: https://render.com
2. Sign up with GitHub
3. Click **New** → **Web Service**
4. Connect your GitHub repo

### Step 3: Configure Service

**Build Command:**
```bash
cd oracle_service && pip install -r requirements.txt
```

**Start Command:**
```bash
cd oracle_service && python3 app.py
```

**Environment:**
- Python 3.11

### Step 4: Add Environment Variables

In Render dashboard:

```bash
ORACLE_KEYPAIR_BASE64=<base64 encoded keypair>
PORT=10000  # Render default
SOLANA_NETWORK=devnet
```

### Step 5: Deploy

Click **Create Web Service**

Render will:
- Build your app
- Start the service
- Provide HTTPS URL: `https://kapture-oracle.onrender.com`

### Step 6: Test

```bash
curl https://kapture-oracle.onrender.com/health
```

**Note:** Free tier sleeps after 15 min of inactivity. First request takes ~30 seconds to wake up.

---

## Option 3: Heroku

### Step 1: Install Heroku CLI

```bash
# macOS
brew install heroku/brew/heroku

# Or download from: https://devcenter.heroku.com/articles/heroku-cli
```

### Step 2: Login and Create App

```bash
heroku login
heroku create kapture-oracle

# This creates: https://kapture-oracle.herokuapp.com
```

### Step 3: Add Procfile

Already created in `oracle_service/Procfile`:

```
web: cd oracle_service && python3 app.py
```

### Step 4: Set Environment Variables

```bash
# Encode oracle keypair
ORACLE_KEYPAIR_BASE64=$(cat ~/.loggerheads/oracle-keypair.json | base64)

# Set on Heroku
heroku config:set ORACLE_KEYPAIR_BASE64=$ORACLE_KEYPAIR_BASE64
heroku config:set PORT=\$PORT  # Heroku provides this
heroku config:set SOLANA_NETWORK=devnet
```

### Step 5: Deploy

```bash
git add .
git commit -m "Add Heroku config"
git push heroku main
```

### Step 6: Test

```bash
heroku open /health
# Or: curl https://kapture-oracle.herokuapp.com/health
```

---

## Option 4: DigitalOcean Droplet (VPS)

**For more control and reliability.**

### Step 1: Create Droplet

1. Go to: https://www.digitalocean.com
2. Create Droplet
   - Image: **Ubuntu 22.04 LTS**
   - Size: **Basic $6/month** (1GB RAM)
   - Datacenter: Choose closest to your users

### Step 2: SSH into Droplet

```bash
ssh root@your-droplet-ip
```

### Step 3: Install Dependencies

```bash
# Update system
apt update && apt upgrade -y

# Install Python and pip
apt install python3 python3-pip git -y

# Install Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
export PATH="/root/.local/share/solana/install/active_release/bin:$PATH"
```

### Step 4: Clone Repository

```bash
cd /opt
git clone https://github.com/yourusername/kapture.git
cd kapture
```

### Step 5: Install Python Dependencies

```bash
pip3 install -r oracle_service/requirements.txt
pip3 install -e .  # Install loggerheads package
```

### Step 6: Transfer Oracle Keypair

From your local machine:

```bash
# Copy oracle keypair to server
scp ~/.loggerheads/oracle-keypair.json root@your-droplet-ip:/root/.loggerheads/
```

Or generate new one on server:

```bash
mkdir -p /root/.loggerheads
python3 -m loggerheads.oracle_secure --generate
```

### Step 7: Create Systemd Service

Create `/etc/systemd/system/oracle.service`:

```ini
[Unit]
Description=Kapture Oracle Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/kapture
Environment="ORACLE_KEYPAIR_PATH=/root/.loggerheads/oracle-keypair.json"
Environment="PORT=5001"
Environment="SOLANA_NETWORK=devnet"
ExecStart=/usr/bin/python3 /opt/kapture/oracle_service/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Step 8: Start Service

```bash
# Reload systemd
systemctl daemon-reload

# Start oracle service
systemctl start oracle

# Enable auto-start on boot
systemctl enable oracle

# Check status
systemctl status oracle
```

### Step 9: Setup Nginx (Reverse Proxy)

```bash
# Install nginx
apt install nginx -y

# Create nginx config
cat > /etc/nginx/sites-available/oracle <<EOF
server {
    listen 80;
    server_name your-domain.com;  # Or use droplet IP

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/oracle /etc/nginx/sites-enabled/
nginx -t  # Test config
systemctl restart nginx
```

### Step 10: Setup HTTPS (Certbot)

```bash
# Install certbot
apt install certbot python3-certbot-nginx -y

# Get SSL certificate
certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

### Step 11: Configure Firewall

```bash
# Allow SSH, HTTP, HTTPS
ufw allow 22
ufw allow 80
ufw allow 443
ufw enable
```

### Step 12: Test

```bash
curl http://your-droplet-ip/health
# Or: curl https://your-domain.com/health
```

---

## Option 5: AWS EC2

### Quick Steps

1. **Launch EC2 instance** (Ubuntu, t2.micro)
2. **SSH into instance**
3. **Follow same steps as DigitalOcean** (steps 3-12 above)
4. **Configure security group** (allow ports 22, 80, 443)
5. **Use Elastic IP** for static IP
6. **Optional:** Use Route53 for DNS

---

## Security Best Practices

### 1. Environment Variables

**Never commit secrets to git!**

```bash
# ❌ Bad
ORACLE_KEYPAIR_PATH=./oracle-keypair.json

# ✅ Good
export ORACLE_KEYPAIR_BASE64=<base64>
```

### 2. HTTPS Only

Always use HTTPS in production:

```bash
# ❌ Bad
export KAPTURE_ORACLE_URL=http://oracle.example.com

# ✅ Good
export KAPTURE_ORACLE_URL=https://oracle.example.com
```

### 3. Rate Limiting

Add to `oracle_service/app.py`:

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.json.get('employee_wallet'),
    default_limits=["10 per minute"]
)

@app.route('/submit-hours', methods=['POST'])
@limiter.limit("3 per day")
def submit_hours_endpoint():
    # ... existing code
```

### 4. Monitoring

**Railway/Render:** Built-in monitoring in dashboard

**VPS/EC2:** Setup monitoring:

```bash
# Install monitoring
apt install prometheus-node-exporter -y

# View logs
journalctl -u oracle -f
```

### 5. Backups

**Database:** If you add a submissions database:

```bash
# Daily backup cron
0 0 * * * /usr/bin/sqlite3 /opt/kapture/submissions.db ".backup /backups/submissions-$(date +\%Y\%m\%d).db"
```

**Keypair:** Keep secure backup of oracle keypair!

```bash
# Encrypted backup
gpg -c ~/.loggerheads/oracle-keypair.json
# Store oracle-keypair.json.gpg in secure location
```

---

## Testing Your Deployment

### 1. Health Check

```bash
curl https://your-oracle-url.com/health
```

Expected response:

```json
{
  "status": "healthy",
  "oracle_pubkey": "7xJ9XxQp...",
  "timestamp": "2025-10-30..."
}
```

### 2. Get Oracle Pubkey

```bash
curl https://your-oracle-url.com/oracle-pubkey
```

### 3. End-to-End Test

**Employer:**
```bash
export KAPTURE_ORACLE_URL=https://your-oracle-url.com
loggerheads  # Create vault
```

**Employee:**
```bash
export KAPTURE_ORACLE_URL=https://your-oracle-url.com
loggerheads  # Setup
loggerheads start  # Track work
loggerheads submit  # Submit hours
```

---

## Troubleshooting

### "Cannot reach oracle service"

**Check 1:** Is service running?

```bash
# Railway/Render: Check dashboard
# VPS: systemctl status oracle
```

**Check 2:** Firewall?

```bash
# VPS: ufw status
# AWS: Check security group
```

**Check 3:** URL correct?

```bash
echo $KAPTURE_ORACLE_URL
```

### "Oracle keypair not found"

**Railway/Render:** Check environment variable is set correctly

```bash
# In dashboard, verify ORACLE_KEYPAIR_BASE64 is set
```

**VPS:** Check file exists

```bash
ls -la /root/.loggerheads/oracle-keypair.json
```

### "Transaction failed"

**Check 1:** Solana network

```bash
# Make sure RPC_URL matches your client network
# Devnet: https://api.devnet.solana.com
# Mainnet: https://api.mainnet-beta.solana.com
```

**Check 2:** Vault exists

```bash
# Test vault-status endpoint
curl -X POST https://your-oracle-url.com/vault-status \
  -H "Content-Type: application/json" \
  -d '{
    "employee_wallet": "...",
    "admin_wallet": "..."
  }'
```

### "502 Bad Gateway"

Service crashed. Check logs:

```bash
# Railway/Render: View logs in dashboard
# VPS: journalctl -u oracle -n 100
```

---

## Monitoring & Maintenance

### Check Uptime

**Railway/Render:** Built-in uptime monitoring

**VPS:** Setup UptimeRobot (free)
- Monitor: https://your-oracle-url.com/health
- Alert email if down

### View Logs

**Railway:**
- Dashboard → Logs tab
- Real-time logs

**Render:**
- Dashboard → Logs
- Last 7 days free tier

**VPS:**
```bash
journalctl -u oracle -f  # Follow logs
journalctl -u oracle -n 100  # Last 100 lines
```

### Update Code

**Railway/Render:**
```bash
git push  # Auto-deploys
```

**VPS:**
```bash
cd /opt/kapture
git pull
systemctl restart oracle
```

### Database Backups

If you add submission tracking:

```bash
# Automatic daily backup
0 0 * * * /usr/bin/sqlite3 /opt/kapture/submissions.db ".backup /backups/submissions-$(date +\%Y\%m\%d).db"

# Keep 30 days
find /backups -name "submissions-*.db" -mtime +30 -delete
```

---

## Migration: Devnet → Mainnet

When ready for production:

### 1. Update Smart Contract

Deploy to mainnet:

```bash
cd workchain-program
anchor build
solana program deploy --url mainnet-beta target/deploy/workchain_program.so
```

### 2. Update Environment Variables

**Change these:**

```bash
# Before (Devnet)
SOLANA_NETWORK=devnet
RPC_URL=https://api.devnet.solana.com

# After (Mainnet)
SOLANA_NETWORK=mainnet-beta
RPC_URL=https://api.mainnet-beta.solana.com
```

### 3. Update USDC Mint

In `loggerheads/blockchain.py`:

```python
# Before (Devnet USDC)
USDC_MINT = Pubkey.from_string("4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU")

# After (Mainnet USDC)
USDC_MINT = Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
```

### 4. Update Program ID

```python
# Update to mainnet program ID
PROGRAM_ID = Pubkey.from_string("YourMainnetProgramID...")
```

### 5. Test with Small Amount

Create test vault with $10 USDC before going full scale.

---

## Cost Estimates

### Railway
- **$5/month** (~750 hours)
- Includes: Hosting, HTTPS, auto-deploy
- **Best for:** Small teams, testing

### Render
- **Free tier:** 750 hours/month (sleeps after 15 min)
- **Paid:** $7/month (always on)
- **Best for:** Side projects, testing

### Heroku
- **$7/month** (eco dyno)
- **$25/month** (basic dyno, better uptime)
- **Best for:** Established projects

### DigitalOcean
- **$6/month** (basic droplet)
- **$12/month** (recommended for production)
- **Best for:** Control, reliability

### AWS EC2
- **$8-15/month** (t2.micro to t2.small)
- **Best for:** Enterprise, existing AWS infrastructure

---

## Next Steps

1. **Choose platform** based on your needs
2. **Deploy oracle** following guide above
3. **Test end-to-end** with devnet
4. **Monitor for 1 week** to ensure stability
5. **Migrate to mainnet** when ready
6. **Implement work verification** (screenshot analysis)
7. **Add fraud detection** (activity patterns)
8. **Security audit** before handling real money

---

## Support

**Issues deploying?**
- Check oracle logs first
- Verify environment variables
- Test locally before deploying
- Open issue: https://github.com/stElmitchay/kapture/issues

**Platform-specific help:**
- Railway: https://docs.railway.app
- Render: https://render.com/docs
- Heroku: https://devcenter.heroku.com
- DigitalOcean: https://docs.digitalocean.com
