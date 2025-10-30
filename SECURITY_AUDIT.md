# Security Audit Report - Kapture (Hackathon Submission)

**Date:** 2025-10-30
**Audited Components:** Smart Contract, Oracle Service, Python Client, Infrastructure

---

## Executive Summary

**Overall Assessment:** The application demonstrates good architecture and several security best practices, but has **CRITICAL vulnerabilities** that must be addressed before mainnet deployment.

**Risk Level:** 🔴 **HIGH** - Multiple critical issues found
**Production Ready:** ❌ **NO** - Requires fixes before real money usage
**Hackathon Demo Ready:** ⚠️ **YES with caveats** - Works for demo, but reviewers will spot issues

---

## 🔴 CRITICAL Issues (Must Fix)

### 1. **Smart Contract: No Rate Limiting on submit_hours**

**Location:** `workchain-program/src/lib.rs:51-86`

**Issue:**
```rust
pub fn submit_hours(
    ctx: Context<SubmitHours>,
    hours_worked: u8,
) -> Result<()> {
    // ❌ No check for duplicate submissions
    // ❌ No timestamp tracking
    // ❌ No daily submission limit
```

**Vulnerability:**
- Oracle can call `submit_hours` **multiple times per day**
- Employee gets paid multiple times for same day
- Example: Submit 8 hours → $150 unlocked → Submit again → $150 more → Repeat...

**Attack Scenario:**
```
Day 1:
- Employee works 8 hours
- Oracle submits at 6PM → $150 unlocked ✅
- Malicious actor calls submit_hours again at 7PM → $150 unlocked ❌
- Calls again at 8PM → $150 unlocked ❌
- Employee drains vault in one day
```

**Impact:** 🔴 **CRITICAL** - Direct financial loss, vault drained

**Fix Required:**
```rust
#[account]
pub struct Vault {
    // ... existing fields
    pub last_submission_day: i64,  // Unix timestamp (days)
}

pub fn submit_hours(
    ctx: Context<SubmitHours>,
    hours_worked: u8,
) -> Result<()> {
    let vault = &mut ctx.accounts.vault;
    let current_day = Clock::get()?.unix_timestamp / 86400;

    // ✅ Check if already submitted today
    require!(
        vault.last_submission_day < current_day,
        ErrorCode::AlreadySubmittedToday
    );

    vault.last_submission_day = current_day;

    // ... rest of logic
}
```

**Recommendation:** Add `last_submission_day` field and check before unlock.

---

### 2. **Oracle Service: No Work Proof Verification**

**Location:** `oracle_service/app.py:124-130`

**Issue:**
```python
# TODO: Verify work proof (screenshots, timestamps, etc.)
# For now, we trust the client (appropriate for devnet testing)
```

**Vulnerability:**
- Oracle **blindly trusts** client's claimed hours
- No verification of screenshots, timestamps, or work legitimacy
- Employee can submit fake data

**Attack Scenario:**
```python
# Employee sends fake submission
{
    "hours": 8,
    "proof": {
        "screenshot_count": 100,  // Fake
        "first_screenshot_time": "2025-10-30 09:00:00",  // Fake
        "last_screenshot_time": "2025-10-30 17:00:00"  // Fake
    }
}
# Oracle accepts without verification ❌
```

**Impact:** 🔴 **CRITICAL** - Complete bypass of work verification

**Fix Required:**
```python
def verify_work_proof(proof, hours):
    """Verify work proof is legitimate."""
    # 1. Check screenshot count is reasonable (10-15 per hour)
    expected_screenshots = hours * 12  # ~5 min intervals
    if proof['screenshot_count'] < expected_screenshots * 0.5:
        raise ValueError("Too few screenshots for claimed hours")

    # 2. Verify timestamps are consistent
    first = datetime.fromisoformat(proof['first_screenshot_time'])
    last = datetime.fromisoformat(proof['last_screenshot_time'])
    time_span = (last - first).total_seconds() / 3600

    if abs(time_span - hours) > 0.5:
        raise ValueError("Time span doesn't match claimed hours")

    # 3. Check timestamps are recent (within 24 hours)
    if (datetime.now() - last).total_seconds() > 86400:
        raise ValueError("Submission too old")

    return True
```

**Recommendation:** Implement basic proof verification before accepting submissions.

---

### 3. **Hours Calculation: Time Span vs Actual Work**

**Location:** `loggerheads/database.py:114-144`

**Issue:**
```python
# Calculate time span from first to last screenshot
time_span = times[-1] - times[0]
hours = time_span.total_seconds() / 3600
```

**Vulnerability:**
- Calculates **elapsed time**, not **actual work time**
- Employee can:
  - Take screenshot at 9 AM
  - Leave computer idle all day
  - Take screenshot at 5 PM
  - Gets credited for 8 hours ❌

**Example:**
```
9:00 AM: Screenshot (working)
9:05 AM: Leaves computer
...
4:55 PM: Comes back, takes screenshot
5:00 PM: Screenshot
Credited hours: 8 hours ❌
Actual work: ~10 minutes
```

**Impact:** 🟡 **HIGH** - Employees can game the system

**Fix Required:**
```python
def calculate_hours_worked_today(db_path=None):
    """
    Calculate hours based on screenshot frequency, not time span.
    Assumes screenshots every 5 minutes during active work.
    """
    # ... get timestamps

    # Count consecutive screenshot pairs (max 5 min gap)
    active_minutes = 0
    for i in range(len(times) - 1):
        gap = (times[i+1] - times[i]).total_seconds() / 60
        if gap <= 7:  # Allow some variance
            active_minutes += 5
        # Else: idle period, don't count

    hours = active_minutes / 60
    return round(hours, 1)
```

**Recommendation:** Calculate based on screenshot frequency, not time span.

---

### 4. **Oracle Keypair Exposure Risk**

**Location:** `oracle_service/app.py:27-35`

**Issue:**
```python
# Load oracle keypair on startup
ORACLE = get_oracle_keypair()  # Stays in memory
ORACLE_PUBKEY = str(ORACLE.pubkey())
```

**Vulnerability:**
- Oracle keypair stays in **server memory** throughout runtime
- If server is compromised (RCE, memory dump), keypair is exposed
- Flask debug mode (if enabled) could expose stack traces with keypair data

**Impact:** 🟡 **HIGH** - Complete oracle compromise

**Current State:**
- Render deployment has keypair in env var ✅
- But loaded into memory on startup ❌
- No key rotation mechanism ❌

**Fix Required:**
```python
# Don't store keypair in global variable
# Load on each use and clear from memory

def get_oracle_keypair_for_signing():
    """Load keypair only when needed, then let it be garbage collected."""
    keypair = load_oracle_keypair_from_env()
    return keypair

@app.route('/submit-hours', methods=['POST'])
def submit_hours_endpoint():
    # ...
    oracle = get_oracle_keypair_for_signing()
    signature = submit_hours(..., oracle)
    del oracle  # Explicit cleanup
    # ...
```

**Recommendation:**
- Use HSM or secure enclave for keypair (production)
- Implement key rotation policy
- Consider multi-sig oracle (multiple keys required)

---

## 🟡 HIGH Priority Issues

### 5. **No Input Validation on Wallet Addresses**

**Location:** `oracle_service/app.py:105-115`

**Issue:**
```python
try:
    Pubkey.from_string(employee_wallet)
    Pubkey.from_string(admin_wallet)
except (ValueError, Exception) as e:
    # Generic error handling
```

**Vulnerability:**
- Accepts any string that parses as Pubkey
- No check if wallet actually exists on-chain
- Could submit to non-existent vaults

**Fix:**
```python
def validate_wallet_exists(client, pubkey):
    """Verify wallet exists and has rent-exempt balance."""
    try:
        account_info = client.get_account_info(pubkey)
        if account_info.value is None:
            raise ValueError(f"Wallet does not exist: {pubkey}")
        return True
    except:
        raise ValueError(f"Invalid wallet: {pubkey}")
```

---

### 6. **No Rate Limiting on Oracle API**

**Location:** `oracle_service/app.py` (entire file)

**Issue:**
- No rate limiting on `/submit-hours` endpoint
- Attacker can spam submissions (even if smart contract prevents double-pay)
- Oracle pays gas fees for each attempt

**Attack Scenario:**
```bash
# Spam oracle with invalid submissions
for i in {1..1000}; do
    curl -X POST https://kapture-oracle.onrender.com/submit-hours \
        -H "Content-Type: application/json" \
        -d '{"employee_wallet": "fake", "admin_wallet": "fake", "hours": 8}'
done
# Oracle runs out of SOL from failed transaction fees
```

**Fix:**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/submit-hours', methods=['POST'])
@limiter.limit("5 per day")  # Max 5 submissions per day per IP
def submit_hours_endpoint():
    # ...
```

---

### 7. **Smart Contract: Missing Token Account Validation**

**Location:** `workchain-program/src/lib.rs:196-214`

**Issue:**
```rust
#[derive(Accounts)]
pub struct Withdraw<'info> {
    #[account(mut)]
    pub vault_token_account: Account<'info, TokenAccount>,

    #[account(mut)]
    pub owner_token_account: Account<'info, TokenAccount>,
    // ❌ No constraint checking vault_token_account belongs to vault
}
```

**Vulnerability:**
- No verification that `vault_token_account` is derived from vault PDA
- Attacker could pass wrong token account

**Fix:**
```rust
#[account(
    mut,
    constraint = vault_token_account.key() == get_associated_token_address(&vault.key(), &USDC_MINT)
)]
pub vault_token_account: Account<'info, TokenAccount>,
```

---

### 8. **Database: No Backup or Recovery**

**Location:** `loggerheads/database.py`

**Issue:**
- Screenshots and work logs stored in local SQLite
- No backup mechanism
- No recovery if DB is corrupted
- Employee loses proof of work

**Impact:** User can't prove work, loses payment

**Fix:**
- Automatic backups to cloud storage
- Checksum verification
- Export functionality

---

## 🟢 MEDIUM Priority Issues

### 9. **Flask Debug Mode in Production**

**Location:** `oracle_service/app.py:278`

**Issue:**
```python
app.run(host='0.0.0.0', port=port, debug=debug_mode)
```

**Vulnerability:**
- If `FLASK_DEBUG=1` set in production, enables debug mode
- Exposes stack traces with sensitive data
- Allows arbitrary code execution via debugger

**Fix:**
```python
# Never use debug mode in production
if os.getenv('ENVIRONMENT') == 'production':
    debug_mode = False
else:
    debug_env = os.getenv('FLASK_DEBUG', 'false').lower()
    debug_mode = debug_env in ('1', 'true', 'yes')
```

---

### 10. **No Logging or Audit Trail**

**Location:** `oracle_service/app.py`

**Issue:**
- Oracle decisions not logged
- No audit trail of submissions
- Can't investigate disputes

**Fix:**
```python
import logging

logger = logging.getLogger(__name__)

@app.route('/submit-hours', methods=['POST'])
def submit_hours_endpoint():
    logger.info(f"Submission received: {employee_wallet}, {hours} hours")
    # ...
    logger.info(f"Submission approved: {signature}")
```

---

### 11. **Hardcoded RPC URL**

**Location:** `loggerheads/blockchain.py:30`

**Issue:**
```python
DEFAULT_RPC_URL = "https://api.devnet.solana.com"
```

**Vulnerability:**
- Public RPC endpoints have rate limits
- Could fail during high usage
- No fallback

**Fix:**
- Use paid RPC provider (Helius, Alchemy)
- Implement fallback RPC URLs
- Add retry logic

---

### 12. **No Error Recovery in Auto-Submit**

**Location:** `loggerheads/auto_submit.py:97-101`

**Issue:**
```python
except ConnectionError as e:
    print(f"❌ Connection Error: {e}")
    sys.exit(1)  # ❌ Fails permanently
```

**Vulnerability:**
- If submission fails once, it never retries
- Employee loses that day's payment

**Fix:**
```python
# Implement exponential backoff retry
for attempt in range(3):
    try:
        result = oracle.submit_hours(...)
        break
    except ConnectionError as e:
        if attempt < 2:
            time.sleep(2 ** attempt)  # 1s, 2s, 4s
        else:
            # Log failure, queue for manual review
            save_failed_submission(...)
```

---

## ✅ Good Security Practices Found

1. **✅ Oracle Signature Verification** (smart contract line 188)
   - Contract properly validates oracle signature
   - Uses Anchor constraints

2. **✅ Checked Arithmetic** (smart contract lines 66, 75-77, 122-124)
   - Uses `checked_add`, `checked_sub` to prevent overflow/underflow
   - Good Rust practices

3. **✅ PDA Derivation** (smart contract line 158)
   - Proper use of seeds for deterministic addresses
   - Owner + admin as seeds prevents conflicts

4. **✅ No Hardcoded Secrets**
   - Git history clean ✅
   - Secrets loaded from environment variables ✅
   - `.gitignore` properly configured ✅

5. **✅ Signer Requirements**
   - Oracle must sign submit_hours ✅
   - Employee must sign withdraw ✅
   - Admin must sign initialize_vault ✅

6. **✅ Balance Checks**
   - Can't withdraw more than unlocked ✅
   - Can't unlock more than available ✅

---

## Solana-Specific Best Practices

### ✅ Following

1. **Using Anchor Framework** - Reduces boilerplate and common bugs
2. **PDA for vault** - Deterministic, secure address derivation
3. **CPI with signer seeds** - Proper vault authority delegation
4. **Account validation** - Anchor constraints for access control

### ❌ Missing

1. **Close instruction** - No way to close vault and recover rent
2. **Pause mechanism** - Can't pause contract in emergency
3. **Upgrade authority** - No program upgrade path specified
4. **Event emissions** - Limited logging (only msg! macros)

---

## Python-Specific Issues

### ✅ Following Standards

1. **Type hints** - Good use of Optional, str, int, etc.
2. **Docstrings** - Most functions documented
3. **Error handling** - Try/except blocks present
4. **Module organization** - Clear separation of concerns

### ❌ Not Following Standards

1. **No unit tests** - No test coverage found
2. **No mypy** - Type checking not enforced
3. **No black/flake8** - Code formatting inconsistent
4. **No requirements.txt pinning** - Version numbers not locked
   ```
   flask>=2.3.0  # ❌ Could break on 3.0.0
   flask==2.3.2  # ✅ Better
   ```

---

## Infrastructure & Deployment

### ✅ Good

1. **Environment variables for secrets** - Keypair not hardcoded
2. **HTTPS** - Render provides SSL
3. **CORS enabled** - For future web frontend

### ❌ Issues

1. **Single point of failure** - One oracle, one server
2. **No monitoring** - No alerts if oracle goes down
3. **No health checks** - Could fail silently
4. **Free tier Render** - Sleeps after 15 min inactivity

---

## Recommendations by Priority

### Before Hackathon Demo

1. **Add rate limiting** - Prevent abuse during demo
2. **Add comments** - Explain submit_hours vulnerability in comments for reviewers
3. **Add disclaimer** - "MVP/Hackathon - Not production ready"

### Before Mainnet

1. **Fix submit_hours rate limiting** - CRITICAL
2. **Implement work proof verification** - CRITICAL
3. **Fix hours calculation** - HIGH
4. **Add unit tests** - HIGH
5. **Security audit by professional** - CRITICAL
6. **Multi-sig oracle or decentralized oracle network** - HIGH

### Future Improvements

1. **HSM for oracle keypair** - Production security
2. **Decentralized oracle network** - Multiple oracles vote
3. **Dispute resolution** - Smart contract for handling conflicts
4. **Comprehensive logging** - Full audit trail
5. **Real screenshot analysis** - AI verification of work legitimacy

---

## Hackathon Judge Review Concerns

**What judges will likely notice:**

1. ⚠️ **"Why no daily submission limit?"** - Most critical question
2. ⚠️ **"How do you verify screenshots are real?"** - Will ask about proof verification
3. ⚠️ **"What if oracle goes down?"** - Single point of failure
4. ⚠️ **"Time span vs actual work?"** - Hours calculation flaw
5. ✅ **"Clean architecture"** - Will appreciate separation of concerns
6. ✅ **"Good use of Anchor"** - Modern Solana practices
7. ✅ **"No hardcoded secrets"** - Security hygiene

**How to address in presentation:**

> "This is an MVP demonstrating the concept. We're aware of the rate limiting issue and have designed (show fix on slide) the solution for production. For the hackathon, we focused on proving the end-to-end flow works."

---

## Final Verdict

**For Hackathon Demo:** ⚠️ **ACCEPTABLE**
- Core functionality works
- Architecture is sound
- Demonstrates the concept
- Issues are MVP-appropriate

**For Production:** ❌ **NOT READY**
- Multiple critical vulnerabilities
- Would lose money immediately
- Needs professional security audit

**Estimated Fix Time:**
- Critical issues: 2-3 days
- High priority: 1 week
- All issues: 2-3 weeks

---

## Positive Notes

Despite the vulnerabilities, this is **solid hackathon work**:

1. ✅ **Complete end-to-end system** - Rare for hackathons
2. ✅ **Clean architecture** - Separates concerns properly
3. ✅ **Good documentation** - README explains clearly
4. ✅ **User-focused UX** - Hides blockchain complexity
5. ✅ **Deployable** - Actually works, not vaporware
6. ✅ **Proper oracle pattern** - Independent API service, not shared keypair

**The vulnerabilities are fixable** and don't reflect poor engineering - they're typical of MVP development where you prioritize "does it work" over "is it bulletproof."

For a hackathon, this is **impressive scope and execution**. Just be transparent about the known issues when presenting.

---

**Last Updated:** 2025-10-30
**Next Review:** After critical fixes implemented
