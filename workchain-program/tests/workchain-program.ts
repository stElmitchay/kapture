import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { WorkchainProgram } from "../target/types/workchain_program";
import { PublicKey, Keypair } from "@solana/web3.js";
import { TOKEN_PROGRAM_ID, createMint, createAccount, mintTo } from "@solana/spl-token";
import { assert } from "chai";

describe("workchain-program", () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);

  const program = anchor.workspace.WorkchainProgram as Program<WorkchainProgram>;

  // Wallets
  let admin: Keypair;
  let employee: Keypair;
  let oracle: Keypair;

  // Token accounts
  let usdcMint: PublicKey;
  let adminTokenAccount: PublicKey;
  let vaultTokenAccount: PublicKey;
  let employeeTokenAccount: PublicKey;

  // Vault PDA
  let vaultPDA: PublicKey;
  let vaultBump: number;

  before(async () => {
    // Generate keypairs
    admin = Keypair.generate();
    employee = Keypair.generate();
    oracle = Keypair.generate();

    // Airdrop SOL to admin for fees
    const airdropSig = await provider.connection.requestAirdrop(
      admin.publicKey,
      2 * anchor.web3.LAMPORTS_PER_SOL
    );
    await provider.connection.confirmTransaction(airdropSig);

    // Create USDC mint (6 decimals like real USDC)
    usdcMint = await createMint(
      provider.connection,
      admin,
      admin.publicKey,
      null,
      6 // decimals
    );

    // Create token accounts
    adminTokenAccount = await createAccount(
      provider.connection,
      admin,
      usdcMint,
      admin.publicKey
    );

    vaultTokenAccount = await createAccount(
      provider.connection,
      admin,
      usdcMint,
      admin.publicKey // Temporary, will be owned by vault PDA
    );

    employeeTokenAccount = await createAccount(
      provider.connection,
      admin,
      usdcMint,
      employee.publicKey
    );

    // Mint 3000 USDC to admin
    await mintTo(
      provider.connection,
      admin,
      usdcMint,
      adminTokenAccount,
      admin,
      3000 * 1_000_000 // 3000 USDC
    );

    // Derive vault PDA
    [vaultPDA, vaultBump] = PublicKey.findProgramAddressSync(
      [Buffer.from("vault"), employee.publicKey.toBuffer(), admin.publicKey.toBuffer()],
      program.programId
    );

    console.log("Setup complete!");
    console.log("Admin:", admin.publicKey.toString());
    console.log("Employee:", employee.publicKey.toString());
    console.log("Oracle:", oracle.publicKey.toString());
    console.log("Vault PDA:", vaultPDA.toString());
  });

  it("Initializes vault and locks USDC", async () => {
    const lockedAmount = new anchor.BN(3000 * 1_000_000); // 3000 USDC
    const dailyTargetHours = 6;
    const dailyUnlock = new anchor.BN(150 * 1_000_000); // 150 USDC

    const tx = await program.methods
      .initializeVault(lockedAmount, dailyTargetHours, dailyUnlock)
      .accounts({
        vault: vaultPDA,
        admin: admin.publicKey,
        owner: employee.publicKey,
        oracle: oracle.publicKey,
        adminTokenAccount: adminTokenAccount,
        vaultTokenAccount: vaultTokenAccount,
        tokenProgram: TOKEN_PROGRAM_ID,
        systemProgram: anchor.web3.SystemProgram.programId,
      })
      .signers([admin])
      .rpc();

    console.log("Vault initialized:", tx);

    // Fetch vault account
    const vault = await program.account.vault.fetch(vaultPDA);

    assert.equal(vault.owner.toString(), employee.publicKey.toString());
    assert.equal(vault.admin.toString(), admin.publicKey.toString());
    assert.equal(vault.lockedAmount.toNumber(), 3000 * 1_000_000);
    assert.equal(vault.unlockedAmount.toNumber(), 0);
    assert.equal(vault.dailyTargetHours, 6);
  });

  it("Submits 7 hours → unlocks 150 USDC", async () => {
    const hoursWorked = 7;

    const tx = await program.methods
      .submitHours(hoursWorked)
      .accounts({
        vault: vaultPDA,
        oracle: oracle.publicKey,
      })
      .signers([oracle])
      .rpc();

    console.log("Hours submitted:", tx);

    // Fetch vault
    const vault = await program.account.vault.fetch(vaultPDA);

    assert.equal(vault.unlockedAmount.toNumber(), 150 * 1_000_000);
    console.log("✅ Unlocked 150 USDC");
  });

  it("Submits 4 hours → no unlock (forfeited)", async () => {
    const hoursWorked = 4;

    const tx = await program.methods
      .submitHours(hoursWorked)
      .accounts({
        vault: vaultPDA,
        oracle: oracle.publicKey,
      })
      .signers([oracle])
      .rpc();

    console.log("Hours submitted:", tx);

    // Fetch vault (should still be 150 USDC unlocked, not 300)
    const vault = await program.account.vault.fetch(vaultPDA);

    assert.equal(vault.unlockedAmount.toNumber(), 150 * 1_000_000);
    console.log("❌ No unlock (threshold not met)");
  });

  it("Employee withdraws 150 USDC", async () => {
    const withdrawAmount = new anchor.BN(150 * 1_000_000);

    const tx = await program.methods
      .withdraw(withdrawAmount)
      .accounts({
        vault: vaultPDA,
        owner: employee.publicKey,
        vaultTokenAccount: vaultTokenAccount,
        ownerTokenAccount: employeeTokenAccount,
        tokenProgram: TOKEN_PROGRAM_ID,
      })
      .signers([employee])
      .rpc();

    console.log("Withdrawn:", tx);

    // Check vault balance
    const vault = await program.account.vault.fetch(vaultPDA);
    assert.equal(vault.unlockedAmount.toNumber(), 0);

    console.log("💸 Withdrawn 150 USDC");
  });
});
