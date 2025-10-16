/**
 * Verification script to test that TypeScript and Python derive the same addresses.
 * This is CRITICAL - both employer (TS) and employee (Python) must calculate identical addresses.
 */

import { PublicKey } from "@solana/web3.js";
import * as anchor from "@coral-xyz/anchor";

// Program ID
const PROGRAM_ID = new PublicKey("5BzzMPy2vJx6Spgcy6hsepQsdBdWAe9SmGvTqpssrk2D");

// USDC Mint (Devnet)
const USDC_MINT = new PublicKey("4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU");

// Test wallets (same as Python test)
const EMPLOYEE = new PublicKey("9Efq78Zw3r1r3f8YP5hy4nQF31cYBbP1J9B3i2cVRc6G");
const ADMIN = new PublicKey("ErrirMoZfpUPS16ttsSpcND6r72wNVRvZyr6Vcy9ZzVb");

console.log("\n" + "=".repeat(70));
console.log("🔍 CROSS-PLATFORM ADDRESS VERIFICATION");
console.log("=".repeat(70));

console.log("\n📥 INPUTS:");
console.log(`  Employee: ${EMPLOYEE.toBase58()}`);
console.log(`  Admin:    ${ADMIN.toBase58()}`);

// Derive Vault PDA
const [vaultPDA, bump] = PublicKey.findProgramAddressSync(
  [Buffer.from("vault"), EMPLOYEE.toBuffer(), ADMIN.toBuffer()],
  PROGRAM_ID
);

console.log("\n✨ DERIVED ADDRESSES (TypeScript):");
console.log(`  Vault PDA: ${vaultPDA.toBase58()}`);

// Derive token accounts (Associated Token Accounts)
const vaultTokenAccount = anchor.utils.token.associatedAddress({
  mint: USDC_MINT,
  owner: vaultPDA,
});

const employeeTokenAccount = anchor.utils.token.associatedAddress({
  mint: USDC_MINT,
  owner: EMPLOYEE,
});

console.log(`  Vault Token Account:    ${vaultTokenAccount.toBase58()}`);
console.log(`  Employee Token Account: ${employeeTokenAccount.toBase58()}`);

console.log("\n" + "=".repeat(70));
console.log("✅ NOW RUN PYTHON TEST AND COMPARE:");
console.log("=".repeat(70));
console.log(`
python3 -c "
from loggerheads.blockchain import derive_all_vault_addresses
result = derive_all_vault_addresses(
    '${EMPLOYEE.toBase58()}',
    '${ADMIN.toBase58()}'
)
print('✨ DERIVED ADDRESSES (Python):')
print(f'  Vault PDA: {result[\\"vault_pda\\"]}')
print(f'  Vault Token Account:    {result[\\"vault_token_account\\"]}')
print(f'  Employee Token Account: {result[\\"employee_token_account\\"]}')
"
`);

console.log("\n💡 If addresses match = SUCCESS! Both sides derive same addresses.\n");
