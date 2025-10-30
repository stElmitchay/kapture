"""
Vault creation module - Python implementation.
Replaces TypeScript scripts with menu-driven Python flow.
"""

import os
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
from solders.transaction import Transaction
from solders.message import Message
from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TxOpts
import struct
from .blockchain import (
    load_keypair,
    derive_vault_pda,
    get_associated_token_address,
    ensure_token_accounts_exist,
    PROGRAM_ID,
    TOKEN_PROGRAM_ID,
    USDC_MINT,
    DEFAULT_RPC_URL
)
from .oracle_client import get_oracle_client
from .idl_utils import get_discriminator
from .token_utils import check_vault_funding_requirements


def create_vault_interactive():
    """
    Interactive vault creation - Y/N prompts only.

    This replaces the TypeScript create-vault.ts script with a simple
    menu-driven Python flow that any employer can use.
    """
    print("\n" + "="*70)
    print("🏦 CREATE VAULT FOR EMPLOYEE")
    print("="*70)

    # Step 1: Get employee wallet
    print("\n📝 STEP 1: Employee Information")
    print("-"*70)
    print("\nYou need your employee's Solana wallet address.")
    print("They can get this by running: solana address")
    print("")

    employee_pubkey_str = input("Employee wallet address: ").strip()
    if not employee_pubkey_str:
        print("\n❌ Employee wallet is required!")
        return None

    try:
        employee_pubkey = Pubkey.from_string(employee_pubkey_str)
    except:
        print("\n❌ Invalid wallet address!")
        return None

    # Step 2: Get admin wallet (uses saved default or prompts first time)
    print("\n📝 STEP 2: Your Wallet (Employer)")
    print("-"*70)

    try:
        admin_keypair = load_keypair()  # This will auto-save on first use
        print(f"\n   ✓ Using wallet: {admin_keypair.pubkey()}")
    except Exception as e:
        print(f"\n❌ Could not load wallet")
        print(f"   Error: {e}")
        return None

    # Step 3: Vault funding and rules
    print("\n📝 STEP 3: Vault Rules")
    print("-"*70)

    print("\nHow much USDC do you want to lock in the vault?")
    print("(Example: 3000 for one month at $100/day)")
    amount_str = input("Amount in USDC: ").strip() or "3000"
    try:
        locked_amount = float(amount_str)
    except:
        print("\n❌ Invalid amount!")
        return None

    print("\nDaily work target in hours?")
    print("(Example: 8 hours)")
    hours_str = input("Hours per day: ").strip() or "8"
    try:
        daily_target_hours = int(hours_str)
    except:
        print("\n❌ Invalid hours!")
        return None

    print("\nHow much USDC unlocks when target is met?")
    print("(Example: 100 for $100/day)")
    unlock_str = input("Daily unlock amount: ").strip() or "100"
    try:
        daily_unlock = float(unlock_str)
    except:
        print("\n❌ Invalid amount!")
        return None

    # Check balances before confirming
    print("\n" + "="*70)
    print("💰 CHECKING BALANCES")
    print("="*70)

    funding_check = check_vault_funding_requirements(admin_keypair.pubkey(), locked_amount)

    print(f"\n  Your USDC Balance: {funding_check['usdc_balance']:.2f} USDC")
    print(f"  Your SOL Balance:  {funding_check['sol_balance']:.4f} SOL")
    print(f"  Required USDC:     {locked_amount:.2f} USDC")

    if not funding_check['ready']:
        print("\n" + "="*70)
        print("⚠️  INSUFFICIENT FUNDS")
        print("="*70)

        if not funding_check['sol_sufficient']:
            print(f"\n  ❌ Not enough SOL for transaction fees")
            print(f"     You have: {funding_check['sol_balance']:.4f} SOL")
            print(f"     You need: ~0.01 SOL")
            print("\n  Get devnet SOL:")
            print("     solana airdrop 2")

        if not funding_check['can_fund_vault']:
            print(f"\n  ❌ Not enough USDC to lock in vault")
            print(f"     You have: {funding_check['usdc_balance']:.2f} USDC")
            print(f"     You need: {locked_amount:.2f} USDC")
            print(f"     Missing: {funding_check['usdc_needed']:.2f} USDC")
            print("\n  Get devnet USDC:")
            print(f"     Visit: https://spl-token-faucet.com/?token-name=USDC-Dev")
            print(f"     Or use: spl-token mint {USDC_MINT} {locked_amount}")
            print(f"     (if you control the mint authority)")

        print("\n" + "="*70)
        return None

    # Confirmation
    print("\n" + "="*70)
    print("📋 CONFIRMATION")
    print("="*70)
    print(f"\n  Employee: {employee_pubkey}")
    print(f"  Admin (you): {admin_keypair.pubkey()}")
    print(f"  Total locked: {locked_amount} USDC")
    print(f"  Daily target: {daily_target_hours} hours")
    print(f"  Daily unlock: {daily_unlock} USDC")
    print(f"\n  → Employee earns {daily_unlock} USDC per day when they work {daily_target_hours}+ hours")

    confirm = input("\n✅ Create this vault? (y/n): ").strip().lower()
    if confirm != 'y':
        print("\n❌ Vault creation cancelled")
        return None

    # Create vault
    print("\n" + "="*70)
    print("🔧 CREATING VAULT...")
    print("="*70)

    try:
        result = create_vault_on_chain(
            admin_keypair,
            employee_pubkey,
            locked_amount,
            daily_target_hours,
            daily_unlock
        )

        if result:
            print("\n" + "="*70)
            print("✅ VAULT CREATED SUCCESSFULLY!")
            print("="*70)

            print("\n📤 SEND THIS TO YOUR EMPLOYEE:")
            print("-"*70)
            print(f"\n  Admin Wallet: {admin_keypair.pubkey()}")
            print("\n  That's all they need! Tell them to:")
            print("  1. Run: loggerheads")
            print("  2. Choose: Employee")
            print("  3. Paste your admin wallet when asked")
            print("\n" + "="*70)

            return result
        else:
            print("\n❌ Vault creation failed!")
            return None

    except Exception as e:
        print(f"\n❌ Error creating vault: {e}")
        return None


def create_vault_on_chain(
    admin_keypair: Keypair,
    employee_pubkey: Pubkey,
    locked_amount: float,
    daily_target_hours: int,
    daily_unlock: float,
    rpc_url: str = DEFAULT_RPC_URL
) -> dict:
    """
    Create vault on Solana blockchain.

    Args:
        admin_keypair: Admin's keypair (pays fees, funds vault)
        employee_pubkey: Employee's wallet address
        locked_amount: Total USDC to lock
        daily_target_hours: Hours needed per day
        daily_unlock: USDC unlocked when target met
        rpc_url: Solana RPC endpoint

    Returns:
        Dict with vault addresses or None on failure
    """
    client = Client(rpc_url)

    # Get oracle public key from oracle service
    print("\n🔮 Connecting to oracle service...")
    try:
        oracle = get_oracle_client()
        oracle_pubkey_str = oracle.get_oracle_pubkey()
        oracle_pubkey = Pubkey.from_string(oracle_pubkey_str)
        print(f"   ✓ Oracle: {oracle_pubkey_str[:16]}...{oracle_pubkey_str[-8:]}")
    except ConnectionError as e:
        print(f"\n❌ Cannot reach oracle service!")
        print(f"   Error: {e}")
        print(f"\n   The system operator must start the oracle:")
        print(f"   python3 oracle_service/app.py")
        return None
    except Exception as e:
        print(f"\n❌ Error connecting to oracle: {e}")
        return None

    print("\n1️⃣  Deriving vault PDA...")
    vault_pda, vault_bump = derive_vault_pda(employee_pubkey, admin_keypair.pubkey())
    print(f"   ✓ Vault PDA: {vault_pda}")

    print("\n2️⃣  Deriving token accounts...")
    admin_token_account = get_associated_token_address(admin_keypair.pubkey())
    vault_token_account = get_associated_token_address(vault_pda)
    employee_token_account = get_associated_token_address(employee_pubkey)
    print(f"   ✓ Admin token: {admin_token_account}")
    print(f"   ✓ Vault token: {vault_token_account}")
    print(f"   ✓ Employee token: {employee_token_account}")

    print("\n3️⃣  Checking token accounts...")
    # Check which token accounts need to be created
    accounts_to_check = [
        (admin_keypair.pubkey(), admin_token_account),
        (vault_pda, vault_token_account),
        (employee_pubkey, employee_token_account),
    ]

    create_ata_instructions = ensure_token_accounts_exist(
        accounts_to_check,
        admin_keypair,
        client,
        USDC_MINT
    )

    print("\n4️⃣  Building initialize_vault instruction...")

    # Convert amounts to lamports (6 decimals for USDC)
    locked_lamports = int(locked_amount * 1_000_000)
    unlock_lamports = int(daily_unlock * 1_000_000)

    # Instruction discriminator for initialize_vault - loaded from IDL
    try:
        discriminator = get_discriminator('initialize_vault')
        print(f"   ✓ Loaded discriminator from IDL: {list(discriminator)}")
    except Exception as e:
        print(f"   ⚠️  Could not load discriminator from IDL: {e}")
        print(f"   ℹ️  Using hardcoded discriminator")
        discriminator = bytes([48, 191, 163, 44, 71, 129, 63, 164])

    # Instruction data: discriminator + locked_amount (u64) + daily_target_hours (u8) + daily_unlock (u64)
    data = discriminator + struct.pack('<Q', locked_lamports) + struct.pack('<B', daily_target_hours) + struct.pack('<Q', unlock_lamports)

    # Build accounts
    accounts = [
        AccountMeta(pubkey=vault_pda, is_signer=False, is_writable=True),
        AccountMeta(pubkey=admin_keypair.pubkey(), is_signer=True, is_writable=True),
        AccountMeta(pubkey=employee_pubkey, is_signer=False, is_writable=False),
        AccountMeta(pubkey=oracle_pubkey, is_signer=False, is_writable=False),
        AccountMeta(pubkey=admin_token_account, is_signer=False, is_writable=True),
        AccountMeta(pubkey=vault_token_account, is_signer=False, is_writable=True),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]

    vault_instruction = Instruction(
        program_id=PROGRAM_ID,
        accounts=accounts,
        data=data
    )

    print("\n5️⃣  Sending transaction...")

    # Get recent blockhash
    blockhash_resp = client.get_latest_blockhash(Confirmed)
    recent_blockhash = blockhash_resp.value.blockhash

    # Combine all instructions: create token accounts first, then initialize vault
    all_instructions = create_ata_instructions + [vault_instruction]

    if create_ata_instructions:
        print(f"   ℹ️  Transaction will create {len(create_ata_instructions)} token account(s)")

    # Create and sign transaction
    message = Message.new_with_blockhash(all_instructions, admin_keypair.pubkey(), recent_blockhash)
    transaction = Transaction([admin_keypair], message, recent_blockhash)

    # Send transaction
    opts = TxOpts(skip_preflight=False, preflight_commitment=Confirmed)
    result = client.send_transaction(transaction, opts)

    signature = str(result.value)
    print(f"   ✓ Transaction sent: {signature[:20]}...")

    print("\n6️⃣  Confirming transaction...")
    client.confirm_transaction(result.value, Confirmed)
    print(f"   ✓ Confirmed!")

    print(f"\n🔍 View on explorer:")
    print(f"   https://explorer.solana.com/tx/{signature}?cluster=devnet")

    return {
        'admin_pubkey': str(admin_keypair.pubkey()),
        'employee_pubkey': str(employee_pubkey),
        'oracle_pubkey': oracle_pubkey_str,
        'vault_pda': str(vault_pda),
        'vault_token_account': str(vault_token_account),
        'employee_token_account': str(employee_token_account),
        'transaction': signature
    }
