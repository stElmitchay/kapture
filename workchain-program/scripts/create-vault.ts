/**
 * Create a real vault with your actual wallets
 *
 * Usage:
 *   npx ts-node scripts/create-vault.ts
 */

import * as anchor from "@coral-xyz/anchor";
import { Program, AnchorProvider, Wallet } from "@coral-xyz/anchor";
import { WorkchainProgram } from "../target/types/workchain_program";
import { PublicKey, Keypair, Connection } from "@solana/web3.js";
import {
  TOKEN_PROGRAM_ID,
  createMint,
  createAccount,
  mintTo,
  getOrCreateAssociatedTokenAccount,
  ASSOCIATED_TOKEN_PROGRAM_ID
} from "@solana/spl-token";
import * as fs from "fs";

async function main() {
  // Connect to devnet
  const connection = new Connection("https://api.devnet.solana.com", "confirmed");

  // Load your actual wallets
  const adminKeypair = Keypair.fromSecretKey(
    Uint8Array.from(JSON.parse(fs.readFileSync(process.env.HOME + "/.config/solana/admin.json", "utf-8")))
  );
  const employeeKeypair = Keypair.fromSecretKey(
    Uint8Array.from(JSON.parse(fs.readFileSync(process.env.HOME + "/.config/solana/employee.json", "utf-8")))
  );
  const oracleKeypair = Keypair.fromSecretKey(
    Uint8Array.from(JSON.parse(fs.readFileSync(process.env.HOME + "/.config/solana/oracle.json", "utf-8")))
  );

  console.log("\n" + "=".repeat(70));
  console.log("👔 EMPLOYER: Creating Vault for Employee");
  console.log("=".repeat(70));

  console.log("\n📋 Wallet Addresses:");
  console.log("  Admin (you):    ", adminKeypair.publicKey.toString());
  console.log("  Employee:       ", employeeKeypair.publicKey.toString());
  console.log("  Oracle:         ", oracleKeypair.publicKey.toString());
  console.log("                  ↑ This is the embedded oracle in loggerheads");
  console.log("");

  // Set up provider
  const wallet = new Wallet(adminKeypair);
  const provider = new AnchorProvider(connection, wallet, { commitment: "confirmed" });
  anchor.setProvider(provider);

  // Load program
  const programId = new PublicKey("5BzzMPy2vJx6Spgcy6hsepQsdBdWAe9SmGvTqpssrk2D");
  const idl = JSON.parse(fs.readFileSync("./target/idl/workchain_program.json", "utf-8"));
  const program = new Program(idl, provider) as Program<WorkchainProgram>;

  console.log("💰 Creating test USDC mint...");

  // Create test USDC mint (6 decimals)
  const usdcMint = await createMint(
    connection,
    adminKeypair,
    adminKeypair.publicKey,
    null,
    6
  );
  console.log("  Mint address:", usdcMint.toString());

  console.log("\n🔐 Deriving vault PDA...");

  // Derive vault PDA FIRST (we need it for the vault token account)
  const [vaultPDA, vaultBump] = PublicKey.findProgramAddressSync(
    [Buffer.from("vault"), employeeKeypair.publicKey.toBuffer(), adminKeypair.publicKey.toBuffer()],
    programId
  );
  console.log("  Vault PDA:", vaultPDA.toString());

  console.log("\n🏦 Creating token accounts...");

  // Create admin token account (ATA)
  const adminTokenAccountInfo = await getOrCreateAssociatedTokenAccount(
    connection,
    adminKeypair,
    usdcMint,
    adminKeypair.publicKey
  );
  const adminTokenAccount = adminTokenAccountInfo.address;
  console.log("  Admin token account:", adminTokenAccount.toString());

  // Create vault token account (ATA) - OWNED BY VAULT PDA
  const vaultTokenAccountInfo = await getOrCreateAssociatedTokenAccount(
    connection,
    adminKeypair,
    usdcMint,
    vaultPDA,
    true  // allowOwnerOffCurve - vault PDA is not on the ed25519 curve
  );
  const vaultTokenAccount = vaultTokenAccountInfo.address;
  console.log("  Vault token account:", vaultTokenAccount.toString());

  // Create employee token account (ATA)
  const employeeTokenAccountInfo = await getOrCreateAssociatedTokenAccount(
    connection,
    adminKeypair,
    usdcMint,
    employeeKeypair.publicKey
  );
  const employeeTokenAccount = employeeTokenAccountInfo.address;
  console.log("  Employee token account:", employeeTokenAccount.toString());

  console.log("\n💵 Minting 3000 test USDC to admin...");
  console.log("  (In production, admin would already have real USDC)");

  // Mint 3000 USDC to admin
  // NOTE: In production, this step doesn't exist - admin already has USDC!
  await mintTo(
    connection,
    adminKeypair,
    usdcMint,
    adminTokenAccount,
    adminKeypair,
    3000 * 1_000_000
  );
  console.log("  ✅ Minted 3000 USDC to admin's wallet");

  console.log("\n🔐 Creating vault...");
  console.log("  This will transfer admin's 3000 USDC to the vault");

  // Initialize vault (PDA already derived above)
  const lockedAmount = new anchor.BN(3000 * 1_000_000); // 3000 USDC
  const dailyTargetHours = 6;
  const dailyUnlock = new anchor.BN(150 * 1_000_000); // 150 USDC per day

  try {
    // This instruction will:
    // 1. Create the vault account
    // 2. Transfer 3000 USDC from admin's wallet to vault's wallet
    // 3. Store the rules (6 hours/day, 150 USDC unlock)
    const tx = await program.methods
      .initializeVault(lockedAmount, dailyTargetHours, dailyUnlock)
      .accountsStrict({
        vault: vaultPDA,
        admin: adminKeypair.publicKey,
        owner: employeeKeypair.publicKey,
        oracle: oracleKeypair.publicKey,
        adminTokenAccount: adminTokenAccount,
        vaultTokenAccount: vaultTokenAccount,
        tokenProgram: TOKEN_PROGRAM_ID,
        systemProgram: anchor.web3.SystemProgram.programId,
      })
      .signers([adminKeypair])
      .rpc();

    console.log("  ✅ Vault created!");
    console.log("  Transaction:", tx);
    console.log("  Explorer: https://explorer.solana.com/tx/" + tx + "?cluster=devnet");
  } catch (error: any) {
    console.error("❌ Error creating vault:", error.message);
    if (error.logs) {
      console.error("Program logs:", error.logs);
    }
    process.exit(1);
  }

  console.log("\n" + "=".repeat(70));
  console.log("✅ VAULT SETUP COMPLETE!");
  console.log("=".repeat(70));

  console.log("\n📝 FOR YOUR RECORDS (All addresses):");
  console.log("-".repeat(70));
  console.log("ADMIN_PUBKEY=" + adminKeypair.publicKey.toString());
  console.log("EMPLOYEE_PUBKEY=" + employeeKeypair.publicKey.toString());
  console.log("ORACLE_PUBKEY=" + oracleKeypair.publicKey.toString());
  console.log("VAULT_PDA=" + vaultPDA.toString());
  console.log("VAULT_TOKEN_ACCOUNT=" + vaultTokenAccount.toString());
  console.log("EMPLOYEE_TOKEN_ACCOUNT=" + employeeTokenAccount.toString());

  console.log("\n📤 TO ONBOARD YOUR EMPLOYEE:");
  console.log("-".repeat(70));
  console.log("\n1️⃣  Send them ONLY your admin wallet address:");
  console.log("    " + adminKeypair.publicKey.toString());
  console.log("");
  console.log("2️⃣  Tell them to run:");
  console.log("    pip install loggerheads");
  console.log("    loggerheads setup-vault");
  console.log("    loggerheads install");
  console.log("    loggerheads start");
  console.log("");
  console.log("3️⃣  That's it! They'll earn automatically by working.");

  console.log("\n💡 TO TEST THE VAULT:");
  console.log("-".repeat(70));
  console.log("\n• Check vault status:");
  console.log("  loggerheads vault-info");
  console.log("");
  console.log("• Submit hours manually:");
  console.log("  loggerheads submit");
  console.log("");
  console.log("• Withdraw funds:");
  console.log("  loggerheads withdraw");
  console.log("");
  console.log("(Note: Auto-derivation is enabled - no need to provide addresses!)");
  console.log("");
}

main()
  .then(() => process.exit(0))
  .catch((err) => {
    console.error(err);
    process.exit(1);
  });
