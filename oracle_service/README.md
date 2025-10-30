# Kapture Oracle Service

**Independent API service for verifying work and submitting hours to blockchain.**

The oracle acts as a neutral third party between employers and employees, ensuring work verification is trustless and automatic.

---

## What Is This?

The oracle is the trust layer in Kapture:

```
┌──────────┐                  ┌─────────┐                ┌──────────────┐
│ EMPLOYEE │──work proof─────>│ ORACLE  │──signed tx────>│ BLOCKCHAIN   │
│          │  (screenshots)   │ SERVICE │  (verified)    │ (enforces)   │
└──────────┘                  └─────────┘                └──────────────┘
```

**Why It's Needed:**
- Without oracle: Employee could fake work hours
- With oracle: Work must be verified before payment unlocks
- Oracle is independent: Neither party controls it

---

## Quick Start

### 1. Install Dependencies

```bash
cd oracle_service
pip3 install -r requirements.txt
```

### 2. Generate Oracle Keypair

```bash
python3 -m loggerheads.oracle_secure --generate
```

This creates: `~/.loggerheads/oracle-keypair.json`

**IMPORTANT:** Keep this file secure! It controls work verification.

### 3. Start Oracle Service

```bash
python3 oracle_service/app.py
```

You'll see:
```
🔮 KAPTURE ORACLE SERVICE
══════════════════════════════════════════════════════════════════════

✅ Oracle Public Key: 7xJ9...

📡 Starting API server...
   Employers: Use this oracle pubkey when creating vaults
   Employees: Submit hours to this service
```

The service runs on `http://localhost:5000`

### 4. Test It

```bash
curl http://localhost:5000/health
```

You should see:
```json
{
  "status": "healthy",
  "oracle_pubkey": "7xJ9...",
  "timestamp": "2025-10-27T..."
}
```

---

## API Endpoints

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "oracle_pubkey": "7xJ9XxQp...",
  "timestamp": "2025-10-27T10:30:00"
}
```

### GET /oracle-pubkey

Get oracle public key (employers need this when creating vaults).

**Response:**
```json
{
  "oracle_pubkey": "7xJ9XxQp..."
}
```

### POST /submit-hours

Submit work hours for verification and blockchain submission.

**Request:**
```json
{
  "employee_wallet": "HzVw...",
  "admin_wallet": "4KcY...",
  "hours": 8.5,
  "proof": {
    "screenshot_count": 102,
    "first_screenshot_time": "2025-10-27 09:00:00",
    "last_screenshot_time": "2025-10-27 17:30:00",
    "work_summary": "8.5 hours tracked"
  }
}
```

**Response (Success):**
```json
{
  "success": true,
  "transaction_signature": "5xRt...",
  "hours_submitted": 9,
  "vault_status": {
    "unlocked_amount": 150.0,
    "locked_amount": 3000.0,
    "daily_target_hours": 8,
    "daily_unlock": 150.0
  },
  "explorer_url": "https://explorer.solana.com/tx/5xRt...?cluster=devnet"
}
```

**Response (Error - Vault Not Found):**
```json
{
  "success": false,
  "error": "Vault not found. Employer must create vault first."
}
```

**Response (Error - Wrong Oracle):**
```json
{
  "success": false,
  "error": "Vault trusts different oracle: 9xHw..."
}
```

### POST /vault-status

Get current vault status.

**Request:**
```json
{
  "employee_wallet": "HzVw...",
  "admin_wallet": "4KcY..."
}
```

**Response:**
```json
{
  "success": true,
  "vault": {
    "employee": "HzVw...",
    "admin": "4KcY...",
    "oracle": "7xJ9...",
    "unlocked_amount": 450.0,
    "locked_amount": 3000.0,
    "daily_target_hours": 8,
    "daily_unlock": 150.0
  }
}
```

---

## How Clients Use It

### Automatic Submission (Employees)

When employee runs `loggerheads submit` or auto-submit triggers:

1. Client calculates hours worked from local database
2. Client packages work proof (screenshot count, timestamps)
3. Client POSTs to `/submit-hours`
4. Oracle verifies proof (TODO: implement full verification)
5. Oracle signs transaction with its keypair
6. Oracle submits to Solana blockchain
7. Client receives transaction signature

**Code example:**
```python
from loggerheads.oracle_client import get_oracle_client

oracle = get_oracle_client('http://localhost:5000')

result = oracle.submit_hours(
    employee_wallet='HzVw...',
    admin_wallet='4KcY...',
    hours=8.5,
    proof={
        'screenshot_count': 102,
        'work_summary': '8.5 hours tracked'
    }
)

print(f"Transaction: {result['transaction_signature']}")
print(f"Unlocked: ${result['vault_status']['unlocked_amount']}")
```

### Vault Creation (Employers)

When employer creates vault:

1. Get oracle public key from `/oracle-pubkey`
2. Create vault with that oracle address
3. Smart contract stores oracle address
4. Only that oracle can submit hours for this vault

---

## Configuration

### Environment Variables

**KAPTURE_ORACLE_URL** (Client-side)
- Where clients send submissions
- Default: `http://localhost:5000`
- Production: `https://oracle.kapture.io`

Example:
```bash
export KAPTURE_ORACLE_URL=https://oracle.kapture.io
```

### Oracle Keypair Location

Oracle looks for keypair at:
1. `$ORACLE_KEYPAIR_PATH` (environment variable)
2. `~/.loggerheads/oracle-keypair.json` (default)

Example:
```bash
export ORACLE_KEYPAIR_PATH=/secure/oracle-keypair.json
python3 oracle_service/app.py
```

---

## Security Considerations

### Current Implementation (Devnet Testing)

**Work Verification:**
- Currently minimal (accepts client-reported hours)
- Appropriate for testing on devnet
- TODO: Implement full verification

**Oracle Keypair:**
- Loaded at startup from local file
- Service should run on secure server
- Never expose keypair publicly

### Production Requirements

**Must Implement:**

1. **Screenshot Verification**
   - Validate screenshot timestamps
   - Check for manipulated images
   - Verify OCR text authenticity

2. **Rate Limiting**
   - Prevent spam submissions
   - Limit per wallet per day
   - Track submission patterns

3. **Fraud Detection**
   - Flag suspicious patterns
   - Alert on unusual submissions
   - Manual review queue

4. **Infrastructure Security**
   - Run on secure server (not localhost)
   - HTTPS only
   - Oracle keypair in secure enclave/vault
   - Regular security audits

5. **Monitoring & Logging**
   - Log all submissions
   - Track success/failure rates
   - Alert on anomalies
   - Blockchain transaction monitoring

6. **High Availability**
   - Multiple oracle instances
   - Load balancing
   - Failover mechanisms
   - Database for submission history

---

## Deployment

### Development (Local Testing)

```bash
# Terminal 1: Start oracle
python3 oracle_service/app.py

# Terminal 2: Run employee client
loggerheads submit
```

### Production (Cloud Deployment)

**Option 1: Docker**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install -r oracle_service/requirements.txt
RUN pip install -e .

ENV ORACLE_KEYPAIR_PATH=/secure/oracle-keypair.json

CMD ["python3", "oracle_service/app.py"]
```

**Option 2: Systemd Service**

Create `/etc/systemd/system/kapture-oracle.service`:

```ini
[Unit]
Description=Kapture Oracle Service
After=network.target

[Service]
Type=simple
User=oracle
WorkingDirectory=/opt/kapture
Environment="ORACLE_KEYPAIR_PATH=/secure/oracle-keypair.json"
ExecStart=/usr/bin/python3 oracle_service/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable kapture-oracle
sudo systemctl start kapture-oracle
sudo systemctl status kapture-oracle
```

**Option 3: Cloud Platform**
- Heroku: `Procfile` + `gunicorn`
- AWS: EC2 + Application Load Balancer
- Google Cloud: Cloud Run
- DigitalOcean: App Platform

**Production WSGI Server:**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 oracle_service.app:app
```

---

## Monitoring

### Health Checks

```bash
# Manual check
curl http://localhost:5000/health

# Automated monitoring (add to cron)
*/5 * * * * curl -f http://localhost:5000/health || /alert-script.sh
```

### Logs

Service logs to stdout. Capture with:

```bash
python3 oracle_service/app.py >> /var/log/kapture-oracle.log 2>&1
```

Or use systemd journal:
```bash
sudo journalctl -u kapture-oracle -f
```

---

## Troubleshooting

### "Oracle keypair not found"

```
❌ Failed to load oracle keypair: NO ORACLE KEYPAIR FOUND
```

**Solution:**
```bash
python3 -m loggerheads.oracle_secure --generate
```

### "Cannot reach oracle service"

**From client:**
```
❌ Cannot reach oracle service at http://localhost:5000
```

**Solution:**
1. Check oracle is running: `curl http://localhost:5000/health`
2. Check firewall allows port 5000
3. Verify KAPTURE_ORACLE_URL is correct

### "Vault trusts different oracle"

```
{
  "error": "Vault trusts different oracle: 9xHw..."
}
```

**Solution:**
- Vault was created with different oracle
- Get correct oracle URL from employer
- Or recreate vault with current oracle

### Port Already in Use

```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find process using port 5000
lsof -i :5000

# Kill it
kill -9 <PID>

# Or use different port
# Edit app.py: app.run(port=5001)
```

---

## Future Enhancements

### Planned Features

1. **Multi-Oracle Support**
   - Multiple oracles vote on validity
   - Requires M-of-N signatures
   - Increases decentralization

2. **AI-Based Verification**
   - Analyze screenshot content
   - Detect fake/idle activity
   - Score work quality

3. **Dispute Resolution**
   - Manual review queue
   - Appeal mechanism
   - Arbitration process

4. **Oracle Marketplace**
   - Multiple oracle providers
   - Employers choose trusted oracles
   - Reputation system

5. **Privacy Enhancements**
   - Zero-knowledge proofs
   - Screenshots never leave device
   - Only proof submitted

---

## Support

**Issues:** https://github.com/stElmitchay/loggerheads/issues
**Docs:** See `ARCHITECTURE.md` for system design
**Security:** Report security issues privately to mitchell@kapture.io
