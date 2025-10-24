# Oracle Security Guide

## Overview

The oracle is the trusted authority that verifies and signs work submissions in Loggerheads. **Securing the oracle keypair is critical** to prevent fraudulent work submissions.

## Security Model

### ❌ Old (Insecure) Model
- Oracle private key hardcoded in source code
- Same key used by all installations
- Key visible in public GitHub repository
- Anyone can extract and forge work submissions

### ✅ New (Secure) Model
- Each deployment generates its own oracle keypair
- Private key stored securely, never committed to git
- Loaded from environment variable or config file
- Demo oracle available only for testing (with warnings)

---

## Quick Setup

### For Production Deployments

1. **Generate Oracle Keypair**
   ```bash
   python -m loggerheads.oracle_secure --generate
   ```
   This creates `~/.loggerheads/oracle-keypair.json` with secure permissions (0600).

2. **Set Environment Variable**
   ```bash
   export ORACLE_KEYPAIR_PATH=~/.loggerheads/oracle-keypair.json
   ```
   
   Add to `~/.bashrc` or `~/.zshrc` for persistence:
   ```bash
   echo 'export ORACLE_KEYPAIR_PATH=~/.loggerheads/oracle-keypair.json' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **Get Oracle Public Key**
   ```bash
   python -m loggerheads.oracle_secure --pubkey
   ```
   Share this public key with employers when they create vaults.

4. **Verify Setup**
   ```bash
   loggerheads
   ```
   Should NOT show the demo oracle warning.

### For Testing/Demo

The app will automatically use a demo oracle if no secure keypair is found, with prominent warnings.

To explicitly allow demo oracle:
```bash
export LOGGERHEADS_ALLOW_DEMO_ORACLE=true
```

---

## Keypair Storage Locations

The app searches for oracle keypair in this order:

1. **Environment Variable** (highest priority)
   ```
   ORACLE_KEYPAIR_PATH=/custom/path/oracle-keypair.json
   ```

2. **Default Config Location**
   ```
   ~/.loggerheads/oracle-keypair.json
   ```

3. **Demo Oracle** (lowest priority, testing only)
   - Used if no secure keypair found
   - Shows security warnings
   - Not recommended for production

---

## Security Best Practices

### ✅ DO:
- Generate a unique oracle keypair for each deployment
- Store keypair in a secure location with restricted permissions (0600)
- Use environment variables to specify keypair path
- Keep keypair backups in secure, encrypted storage
- Rotate keypairs periodically (requires vault recreation)
- Use different oracles for testing vs production

### ❌ DON'T:
- NEVER commit oracle keypair files to git
- NEVER share oracle private key
- NEVER reuse oracle keypairs across environments
- NEVER use demo oracle in production
- NEVER store keypair in publicly accessible locations

---

## File Permissions

Oracle keypair files should have restrictive permissions:

```bash
# Set correct permissions
chmod 600 ~/.loggerheads/oracle-keypair.json

# Verify
ls -la ~/.loggerheads/oracle-keypair.json
# Should show: -rw------- (only owner can read/write)
```

---

## Vault Creation with Custom Oracle

When creating a vault, admins specify which oracle they trust:

```bash
# 1. Get your oracle public key
python -m loggerheads.oracle_secure --pubkey

# 2. Share this with employer
# Employer uses this when creating vault on-chain

# 3. Employee configures to use same oracle
export ORACLE_KEYPAIR_PATH=/path/to/oracle-keypair.json
```

**Important:** Employee and employer must agree on which oracle to trust before vault creation.

---

## Multiple Oracles (Advanced)

For enterprise deployments, you may want separate oracles for:
- **Development:** Demo oracle (low security)
- **Staging:** Test oracle (medium security)
- **Production:** Production oracle (high security)

Example setup:
```bash
# Development
export ORACLE_KEYPAIR_PATH=~/.loggerheads/oracle-dev.json

# Production
export ORACLE_KEYPAIR_PATH=/secure/vault/oracle-prod.json
```

---

## Troubleshooting

### Error: "No oracle keypair found!"

**Solution:**
```bash
# Generate keypair
python -m loggerheads.oracle_secure --generate

# Set environment variable
export ORACLE_KEYPAIR_PATH=~/.loggerheads/oracle-keypair.json
```

### Warning: "Using demo oracle keypair (NOT SECURE)"

This means no secure oracle found. For production, generate a secure keypair (see above).

For testing/demo, this is acceptable but you'll see warnings.

### Error: "Failed to load oracle keypair"

**Check:**
1. File exists: `ls ~/.loggerheads/oracle-keypair.json`
2. Permissions: `ls -la ~/.loggerheads/oracle-keypair.json`
3. Valid JSON format
4. Environment variable set correctly: `echo $ORACLE_KEYPAIR_PATH`

---

## Migrating from Old (Insecure) Oracle

If you have vaults created with the old hardcoded oracle:

1. **Generate new oracle keypair**
   ```bash
   python -m loggerheads.oracle_secure --generate
   ```

2. **Get new public key**
   ```bash
   python -m loggerheads.oracle_secure --pubkey
   ```

3. **Create new vaults** with the new oracle
   - Old vaults will continue using old oracle (can't update on-chain)
   - New vaults should use new secure oracle

4. **Deprecate old oracle**
   - Once all vaults migrated, old oracle becomes useless
   - Old key is public knowledge, so don't rely on it for security

---

## Architecture

```
┌─────────────────┐
│   Employee      │
│   Loggerheads   │
└────────┬────────┘
         │
         │ 1. Track work (screenshots, OCR)
         │ 2. Generate proof
         │
         ▼
┌─────────────────┐
│ Oracle Keypair  │◄── Loaded from secure file
│  (Private Key)  │    Never exposed
└────────┬────────┘
         │
         │ 3. Sign transaction
         │
         ▼
┌─────────────────┐
│ Solana Blockchain│
│ Smart Contract  │◄── 4. Verify signature
│  (Vault)        │    5. Unlock payment
└─────────────────┘
```

---

## FAQ

**Q: Can I use the same oracle for multiple employees?**
A: Yes, one oracle can serve multiple vaults/employees. The oracle is per-deployment, not per-employee.

**Q: What happens if I lose my oracle keypair?**
A: You can't sign new work submissions for existing vaults. You'll need to generate a new oracle and create new vaults.

**Q: Can I change the oracle for an existing vault?**
A: No, oracle is set at vault creation and immutable on-chain.

**Q: Is the demo oracle really insecure?**
A: Yes. The private key is in public source code, so anyone can forge signatures. Only use for testing.

**Q: How do I backup my oracle keypair?**
A: Copy `~/.loggerheads/oracle-keypair.json` to encrypted backup storage. Keep multiple secure copies.

---

## Support

For security concerns, open an issue at: https://github.com/stElmitchay/loggerheads/issues

**DO NOT** post your oracle private key in issues/discussions!
