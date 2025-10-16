
## 🧪 End-to-End Test

### Test 1: Employer Creates Vault

**As employer, create a vault for your employee:**

```bash
cd workchain-program
npx ts-node scripts/create-vault.ts
```

**Save the output:**
- Admin wallet address (you'll give this to employee)
- All other addresses (for your records)

**Expected:** Vault created on devnet, 3000 USDC locked, 6 hour daily target, 150 USDC daily unlock.

---

### Test 2: Employee Setup (Simplified - Just 2 Inputs!)

**As employee, configure your loggerheads:**

```bash
# Clear any old config first
rm ~/.loggerheads_vault.json

# Run setup
loggerheads setup-vault
```

**When prompted:**
1. **Employee wallet:** Press `Enter` to use default (~/.config/solana/id.json)
2. **Admin wallet:** Paste the admin address from Test 1

**Expected output:**
```
✅ Vault configured successfully!

✨ Auto-derived addresses:
   🔐 Vault PDA:      [matches TypeScript output]
   💰 Vault Token:    [matches TypeScript output]
   💳 Employee Token: [matches TypeScript output]
```

**Enable auto-submission:**
- When asked about auto-submit: `y`
- Time: `18:00` (or any time)

---

### Test 3: Check Vault Status

**Verify vault exists and has correct settings:**

```bash
loggerheads vault-info
```

**Expected output:**
```
💰 Vault Information:
   Owner: [employee wallet]
   Admin: [admin wallet]
   Oracle: GiAShFnTU8YCzYzUXgovDwyu86NrQxcyvRJDbNMGeVug
   Total Locked: 3000.00 USDC
   Unlocked: 0.00 USDC
   Still Locked: 3000.00 USDC
   Daily Target: 6 hours
   Daily Unlock: 150.00 USDC
```

---

### Test 4: Simulate Work and Submit Hours

**Option A: Quick test (fake data)**

```bash
# Insert some fake work data into database
python3 -c "
from loggerheads.database import init_db
from datetime import datetime
import sqlite3

init_db()
conn = sqlite3.connect('activity_log.db')
cursor = conn.cursor()

# Add 8 hours worth of work entries (every 5 minutes = 96 entries)
now = datetime.now()
for i in range(96):
    timestamp = now.replace(hour=9+i//12, minute=(i%12)*5)
    cursor.execute('INSERT INTO logs (window_name, timestamp) VALUES (?, ?)',
                   ('PyCharm - coding.py', timestamp))

conn.commit()
conn.close()
print('✅ Added 8 hours of fake work data')
"

# Now submit
loggerheads submit
```

**Option B: Real tracking**

```bash
# Track for a few minutes
loggerheads start
# (Let it run for 1-2 minutes, use your computer)
# Ctrl+C to stop

# Manually submit
loggerheads submit
```

**Expected output:**
```
📊 Calculated hours worked today: 8 (or whatever you tracked)
📤 Submitting 8 hours to blockchain...
✅ Success!
📝 Transaction: [signature]
🔍 Explorer: https://explorer.solana.com/tx/[signature]?cluster=devnet

💰 Vault Status:
   Unlocked: 150.00 USDC  (because 8 hours >= 6 hour target)
   Locked: 2850.00 USDC
```

---

### Test 5: Withdraw Funds

**Withdraw the unlocked funds:**

```bash
loggerheads withdraw
```

**When prompted:**
```
💰 Available to withdraw: 150.0 USDC
Amount to withdraw (max 150.0): [press Enter for all]
```

**Expected output:**
```
💸 Withdrawing 150.0 USDC...
✅ Success!
📝 Transaction: [signature]
🔍 Explorer: https://explorer.solana.com/tx/[signature]?cluster=devnet
```

**Verify balance:**
```bash
# Check vault again
loggerheads vault-info
```

**Expected:** Unlocked should now be 0.00 USDC (withdrawn), Locked still 2850.00 USDC.

---

### Test 6: Check Employee Token Balance

**Verify USDC arrived in employee's wallet:**

```bash
solana balance --url devnet [EMPLOYEE_TOKEN_ACCOUNT]
```

**Expected:** 150 USDC (or 150000000 lamports with 6 decimals)

---

## 🎯 Success Criteria

✅ **Derivation:** TypeScript and Python produce identical addresses
✅ **Vault Creation:** Vault created with 3000 USDC locked
✅ **Employee Setup:** Only 2 inputs needed (employee + admin wallets)
✅ **Auto-Derivation:** All addresses calculated correctly
✅ **Submit Hours:** Hours successfully submitted via embedded oracle
✅ **Unlock:** Funds unlock when target met (8 >= 6 hours)
✅ **Withdraw:** Employee can withdraw unlocked USDC
✅ **Balance:** USDC appears in employee's token account

---

## 🐛 Troubleshooting

### "Vault not found"
- Check addresses match between TypeScript and Python derivation
- Verify vault was actually created (check Solana explorer)

### "Transaction failed"
- Check wallet has SOL for transaction fees
- Verify program is deployed: `solana program show 5BzzMPy2vJx6Spgcy6hsepQsdBdWAe9SmGvTqpssrk2D --url devnet`

### "No hours detected"
- Check database has entries: `sqlite3 activity_log.db "SELECT COUNT(*) FROM logs WHERE date(timestamp) = date('now')"`
- Use fake data method from Test 4 Option A

### "Insufficient unlocked funds"
- Check vault-info to see unlocked amount
- Verify hours were >= daily target when submitted
- May need to submit hours again if target not met

---

## 📊 Quick Test Summary

```bash
# 1. Verify derivation
cd workchain-program && npx ts-node scripts/verify-derivation.ts

# 2. Create vault
npx ts-node scripts/create-vault.ts

# 3. Employee setup
loggerheads setup-vault  # Enter admin wallet when prompted

# 4. Check vault
loggerheads vault-info

# 5. Add fake data + submit
python3 -c "[fake data script from Test 4]"
loggerheads submit

# 6. Withdraw
loggerheads withdraw

# 7. Verify
loggerheads vault-info
```

---

## 🚀 Next Steps After Testing

Once all tests pass:

1. **Update SETUP_AND_TESTING_GUIDE.md** with simplified instructions
2. **Update README.md** to reflect 2-input setup
3. **Deploy to mainnet** (when ready for production)
4. **Add monitoring** (Discord notifications, etc.)
5. **Package for distribution** (`pip install loggerheads`)

---

## 📝 Notes

- All tests use **devnet** (test network, fake money)
- Embedded oracle public key: `GiAShFnTU8YCzYzUXgovDwyu86NrQxcyvRJDbNMGeVug`
- Program ID: `5BzzMPy2vJx6Spgcy6hsepQsdBdWAe9SmGvTqpssrk2D`
- Devnet USDC mint: `4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU`
