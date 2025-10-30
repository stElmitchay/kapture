"""
Blockchain integration for WorkChain smart contract on Solana.
Handles vault creation, hours submission, and fund withdrawal.
"""

import os
import json
from pathlib import Path
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
from solders.transaction import Transaction
from solders.message import Message
from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TxOpts
import struct
from .oracle import get_oracle_keypair
from .idl_utils import get_discriminator


# Program ID (deployed on devnet)
PROGRAM_ID = Pubkey.from_string("5BzzMPy2vJx6Spgcy6hsepQsdBdWAe9SmGvTqpssrk2D")

# Token Program ID
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")

# Associated Token Program ID
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")

# USDC Mint Address (Devnet)
USDC_MINT = Pubkey.from_string("4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU")

# Default RPC endpoint
DEFAULT_RPC_URL = "https://api.devnet.solana.com"


def get_keypair_path_from_solana_config() -> str:
    """
    Get the keypair path from Solana CLI config.

    Returns:
        Path to keypair file from solana config

    Raises:
        RuntimeError: If solana config is not set up
    """
    import subprocess
    try:
        result = subprocess.run(
            ["solana", "config", "get"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Parse output to find "Keypair Path:"
            for line in result.stdout.split('\n'):
                if 'Keypair Path:' in line:
                    path = line.split(':', 1)[1].strip()
                    return path
        raise RuntimeError("Could not find Keypair Path in solana config")
    except FileNotFoundError:
        raise RuntimeError(
            "Solana CLI not installed!\n\n"
            "Install it with:\n"
            "  sh -c \"$(curl -sSfL https://release.solana.com/stable/install)\""
        )
    except Exception as e:
        raise RuntimeError(f"Error reading solana config: {e}")


def get_default_keypair_path() -> str:
    """
    Get keypair path - from config first, otherwise prompt user.

    Returns:
        Path to keypair file
    """
    from .vault_config import VaultConfig

    config = VaultConfig()

    # Check if we have a saved keypair path
    if config.has_keypair_path():
        return config.get_keypair_path()

    # First time - need to set it up
    print("\n🔐 FIRST TIME SETUP: Set Your Default Wallet")
    print("="*70)
    print("We need to know which wallet you want to use for Kapture.")
    print("This will be saved and used automatically from now on.")
    print()

    # Try to get from solana config first
    try:
        solana_path = get_keypair_path_from_solana_config()
        print(f"Found keypair in Solana config: {solana_path}")
        use_it = input("\nUse this wallet? (y/n): ").strip().lower()
        if use_it == 'y':
            keypair_path = solana_path
        else:
            keypair_path = None
    except Exception:
        keypair_path = None

    # If not using solana config, ask for path
    if not keypair_path:
        print("\nEnter the path to your keypair file:")
        print("  Example: ~/.config/solana/id.json")
        print("  Example: ~/my-wallet.json")
        print()
        keypair_path = input("Keypair path: ").strip()

        if not keypair_path:
            raise ValueError("Keypair path is required!")

    # Verify the file exists before saving
    expanded_path = os.path.expanduser(keypair_path)
    if not os.path.exists(expanded_path):
        raise FileNotFoundError(
            f"Keypair file not found: {expanded_path}\n\n"
            "To create a new wallet:\n"
            "  solana-keygen new"
        )

    # Save it
    config.set_keypair_path(keypair_path)
    print(f"\n✓ Default wallet saved: {keypair_path}")
    print("  (This will be used automatically from now on)")
    print()

    return keypair_path


def load_keypair(keypair_path: str = None) -> Keypair:
    """
    Load keypair from file.

    Args:
        keypair_path: Path to keypair JSON file. If None, uses saved default.

    Returns:
        Keypair object

    Raises:
        FileNotFoundError: If keypair file doesn't exist
        ValueError: If keypair file is invalid
    """
    if not keypair_path:
        keypair_path = get_default_keypair_path()

    # Expand ~ to home directory
    keypair_path = os.path.expanduser(keypair_path)

    if not os.path.exists(keypair_path):
        raise FileNotFoundError(
            f"Keypair file not found: {keypair_path}\n\n"
            "To create a new wallet:\n"
            "  solana-keygen new --outfile ~/my-wallet.json"
        )

    try:
        with open(keypair_path, 'r') as f:
            secret_key = json.load(f)
        return Keypair.from_bytes(bytes(secret_key))
    except Exception as e:
        raise ValueError(f"Invalid keypair file {keypair_path}: {e}")


def derive_vault_pda(owner: Pubkey, admin: Pubkey) -> tuple[Pubkey, int]:
    """
    Derive the vault PDA address.

    Args:
        owner: Employee wallet public key
        admin: Admin wallet public key

    Returns:
        Tuple of (PDA address, bump seed)
    """
    seeds = [
        b"vault",
        bytes(owner),
        bytes(admin)
    ]

    pda, bump = Pubkey.find_program_address(seeds, PROGRAM_ID)
    return pda, bump


def get_associated_token_address(wallet: Pubkey, mint: Pubkey = USDC_MINT) -> Pubkey:
    """
    Derive the Associated Token Account (ATA) address for a wallet and mint.

    Args:
        wallet: Wallet public key
        mint: Token mint public key (defaults to USDC)

    Returns:
        Associated Token Account address
    """
    seeds = [
        bytes(wallet),
        bytes(TOKEN_PROGRAM_ID),
        bytes(mint)
    ]

    ata, _ = Pubkey.find_program_address(seeds, ASSOCIATED_TOKEN_PROGRAM_ID)
    return ata


def check_token_account_exists(token_account: Pubkey, client: Client) -> bool:
    """
    Check if a token account exists on-chain.

    Args:
        token_account: Token account address to check
        client: Solana RPC client

    Returns:
        True if account exists, False otherwise
    """
    try:
        response = client.get_account_info(token_account, commitment=Confirmed)
        return response.value is not None
    except Exception:
        return False


def create_associated_token_account_instruction(
    payer: Pubkey,
    owner: Pubkey,
    mint: Pubkey = USDC_MINT
) -> Instruction:
    """
    Create instruction to initialize an Associated Token Account.

    Args:
        payer: Account that will pay for the token account creation
        owner: Owner of the token account
        mint: Token mint (defaults to USDC)

    Returns:
        Instruction to create the ATA
    """
    ata = get_associated_token_address(owner, mint)

    # CreateAssociatedTokenAccount instruction has no data
    accounts = [
        AccountMeta(pubkey=payer, is_signer=True, is_writable=True),
        AccountMeta(pubkey=ata, is_signer=False, is_writable=True),
        AccountMeta(pubkey=owner, is_signer=False, is_writable=False),
        AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
    ]

    return Instruction(
        program_id=ASSOCIATED_TOKEN_PROGRAM_ID,
        accounts=accounts,
        data=bytes()  # No instruction data needed
    )


def ensure_token_accounts_exist(
    accounts_to_check: list[tuple[Pubkey, Pubkey]],
    payer: Keypair,
    client: Client,
    mint: Pubkey = USDC_MINT
) -> list[Instruction]:
    """
    Check if token accounts exist and return instructions to create missing ones.

    Args:
        accounts_to_check: List of (owner, token_account) tuples to check
        payer: Keypair that will pay for account creation
        client: Solana RPC client
        mint: Token mint (defaults to USDC)

    Returns:
        List of instructions to create missing token accounts (empty if all exist)
    """
    instructions = []

    for owner, token_account in accounts_to_check:
        if not check_token_account_exists(token_account, client):
            print(f"   ℹ️  Token account {token_account} doesn't exist, will create it")
            instruction = create_associated_token_account_instruction(payer.pubkey(), owner, mint)
            instructions.append(instruction)
        else:
            print(f"   ✓ Token account {token_account} exists")

    return instructions


def derive_all_vault_addresses(employee_pubkey: str, admin_pubkey: str) -> dict:
    """
    Derive all vault-related addresses from just employee and admin wallets.

    This is the magic function that makes employee setup simple!
    Given just 2 wallet addresses, we can deterministically derive:
    - Vault PDA
    - Vault's token account
    - Employee's token account

    Args:
        employee_pubkey: Employee wallet address (string)
        admin_pubkey: Admin wallet address (string)

    Returns:
        Dict with all derived addresses
    """
    employee = Pubkey.from_string(employee_pubkey)
    admin = Pubkey.from_string(admin_pubkey)

    # Derive vault PDA
    vault_pda, bump = derive_vault_pda(employee, admin)

    # Derive token accounts (ATAs for USDC)
    vault_token_account = get_associated_token_address(vault_pda, USDC_MINT)
    employee_token_account = get_associated_token_address(employee, USDC_MINT)

    return {
        'employee_pubkey': employee_pubkey,
        'admin_pubkey': admin_pubkey,
        'vault_pda': str(vault_pda),
        'vault_token_account': str(vault_token_account),
        'employee_token_account': str(employee_token_account),
        'bump': bump
    }


def get_vault_info(vault_pda: Pubkey, rpc_url: str = DEFAULT_RPC_URL) -> dict:
    """
    Fetch vault account data from the blockchain.

    Args:
        vault_pda: Vault PDA address
        rpc_url: Solana RPC endpoint

    Returns:
        Dict with vault information
    """
    client = Client(rpc_url)

    try:
        response = client.get_account_info(vault_pda, encoding="base64", commitment=Confirmed)

        if response.value is None:
            return None

        # Decode account data (skip 8-byte discriminator)
        data = response.value.data

        # Parse vault struct (after 8-byte discriminator)
        # owner (32) + admin (32) + oracle (32) + locked_amount (8) + unlocked_amount (8) +
        # daily_target_hours (1) + daily_unlock (8) + last_submission_day (8) + bump (1)
        offset = 8
        owner = Pubkey.from_bytes(data[offset:offset+32])
        offset += 32
        admin = Pubkey.from_bytes(data[offset:offset+32])
        offset += 32
        oracle = Pubkey.from_bytes(data[offset:offset+32])
        offset += 32
        locked_amount = struct.unpack('<Q', data[offset:offset+8])[0]
        offset += 8
        unlocked_amount = struct.unpack('<Q', data[offset:offset+8])[0]
        offset += 8
        daily_target_hours = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        daily_unlock = struct.unpack('<Q', data[offset:offset+8])[0]
        offset += 8
        last_submission_day = struct.unpack('<q', data[offset:offset+8])[0]  # i64 (signed)
        offset += 8
        bump = struct.unpack('<B', data[offset:offset+1])[0]

        return {
            'owner': str(owner),
            'admin': str(admin),
            'oracle': str(oracle),
            'locked_amount': locked_amount,
            'unlocked_amount': unlocked_amount,
            'daily_target_hours': daily_target_hours,
            'daily_unlock': daily_unlock,
            'last_submission_day': last_submission_day,
            'bump': bump
        }
    except Exception as e:
        print(f"Error fetching vault info: {e}")
        return None


def submit_hours(
    hours_worked: int,
    owner_pubkey: str,
    admin_pubkey: str,
    oracle_keypair_path: str = None,
    rpc_url: str = DEFAULT_RPC_URL
) -> str:
    """
    Submit daily work hours to the blockchain.
    Oracle-only function that triggers auto-unlock if target met.

    Args:
        hours_worked: Number of hours worked (integer)
        owner_pubkey: Employee wallet address (string)
        admin_pubkey: Admin wallet address (string)
        oracle_keypair_path: Path to oracle keypair file (uses embedded oracle if None)
        rpc_url: Solana RPC endpoint

    Returns:
        Transaction signature
    """
    # Load oracle keypair - use embedded oracle by default
    if oracle_keypair_path is None:
        oracle = get_oracle_keypair()
    else:
        oracle = load_keypair(oracle_keypair_path)

    # Derive vault PDA
    owner = Pubkey.from_string(owner_pubkey)
    admin = Pubkey.from_string(admin_pubkey)
    vault_pda, _ = derive_vault_pda(owner, admin)

    # Instruction discriminator for submit_hours - loaded from IDL
    try:
        discriminator = get_discriminator('submit_hours')
    except Exception:
        # Fallback to hardcoded discriminator
        discriminator = bytes([135, 190, 70, 235, 234, 220, 207, 48])

    # Instruction data: discriminator + hours_worked (u8)
    data = discriminator + struct.pack('<B', hours_worked)

    # Build accounts
    accounts = [
        AccountMeta(pubkey=vault_pda, is_signer=False, is_writable=True),
        AccountMeta(pubkey=oracle.pubkey(), is_signer=True, is_writable=False),
    ]

    # Create instruction
    instruction = Instruction(
        program_id=PROGRAM_ID,
        accounts=accounts,
        data=data
    )

    # Send transaction
    client = Client(rpc_url)

    # Get recent blockhash
    blockhash_resp = client.get_latest_blockhash(Confirmed)
    recent_blockhash = blockhash_resp.value.blockhash

    # Create and sign transaction
    message = Message.new_with_blockhash([instruction], oracle.pubkey(), recent_blockhash)
    transaction = Transaction([oracle], message, recent_blockhash)

    # Send transaction
    opts = TxOpts(skip_preflight=False, preflight_commitment=Confirmed)
    result = client.send_transaction(transaction, opts)

    signature = str(result.value)

    # Wait for confirmation
    client.confirm_transaction(result.value, Confirmed)

    return signature


def withdraw(
    amount_usdc: float,
    owner_keypair_path: str = None,
    admin_pubkey: str = None,
    vault_token_account: str = None,
    owner_token_account: str = None,
    rpc_url: str = DEFAULT_RPC_URL
) -> str:
    """
    Withdraw unlocked USDC from the vault.

    Args:
        amount_usdc: Amount to withdraw in USDC (e.g., 150.0)
        owner_keypair_path: Path to employee keypair file (defaults to ~/.config/solana/id.json)
        admin_pubkey: Admin wallet address
        vault_token_account: Vault's token account address
        owner_token_account: Employee's token account address
        rpc_url: Solana RPC endpoint

    Returns:
        Transaction signature
    """
    # Load employee keypair - default to ~/.config/solana/id.json
    owner = load_keypair(owner_keypair_path)

    # Derive vault PDA
    admin = Pubkey.from_string(admin_pubkey)
    vault_pda, _ = derive_vault_pda(owner.pubkey(), admin)

    # Convert USDC to lamports (6 decimals)
    amount_lamports = int(amount_usdc * 1_000_000)

    # Instruction discriminator for withdraw - loaded from IDL
    try:
        discriminator = get_discriminator('withdraw')
    except Exception:
        # Fallback to hardcoded discriminator
        discriminator = bytes([183, 18, 70, 156, 148, 109, 161, 34])

    # Instruction data: discriminator + amount (u64)
    data = discriminator + struct.pack('<Q', amount_lamports)

    # Build accounts
    vault_token_acc = Pubkey.from_string(vault_token_account)
    owner_token_acc = Pubkey.from_string(owner_token_account)

    accounts = [
        AccountMeta(pubkey=vault_pda, is_signer=False, is_writable=True),
        AccountMeta(pubkey=owner.pubkey(), is_signer=True, is_writable=False),
        AccountMeta(pubkey=vault_token_acc, is_signer=False, is_writable=True),
        AccountMeta(pubkey=owner_token_acc, is_signer=False, is_writable=True),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
    ]

    # Create instruction
    instruction = Instruction(
        program_id=PROGRAM_ID,
        accounts=accounts,
        data=data
    )

    # Send transaction
    client = Client(rpc_url)

    # Get recent blockhash
    blockhash_resp = client.get_latest_blockhash(Confirmed)
    recent_blockhash = blockhash_resp.value.blockhash

    # Create and sign transaction
    message = Message.new_with_blockhash([instruction], owner.pubkey(), recent_blockhash)
    transaction = Transaction([owner], message, recent_blockhash)

    # Send transaction
    opts = TxOpts(skip_preflight=False, preflight_commitment=Confirmed)
    result = client.send_transaction(transaction, opts)

    signature = str(result.value)

    # Wait for confirmation
    client.confirm_transaction(result.value, Confirmed)

    return signature


def format_usdc(lamports: int) -> str:
    """Convert lamports to USDC string."""
    return f"{lamports / 1_000_000:.2f}"


# Note: initialize_vault requires creating token accounts and is complex
# For the hackathon, this will be done via the admin using Anchor CLI or TypeScript
# The Python CLI focuses on the employee/oracle workflows: submit and withdraw
