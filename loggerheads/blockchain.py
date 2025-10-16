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


def load_keypair(keypair_path: str = None) -> Keypair:
    """
    Load keypair from file.

    Args:
        keypair_path: Path to keypair JSON file. Defaults to ~/.config/solana/id.json

    Returns:
        Keypair object
    """
    if keypair_path is None:
        keypair_path = os.path.expanduser("~/.config/solana/id.json")

    with open(keypair_path, 'r') as f:
        secret_key = json.load(f)

    return Keypair.from_bytes(bytes(secret_key))


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
        # daily_target_hours (1) + daily_unlock (8) + bump (1)
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
        bump = struct.unpack('<B', data[offset:offset+1])[0]

        return {
            'owner': str(owner),
            'admin': str(admin),
            'oracle': str(oracle),
            'locked_amount': locked_amount,
            'unlocked_amount': unlocked_amount,
            'daily_target_hours': daily_target_hours,
            'daily_unlock': daily_unlock,
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

    # Instruction discriminator for submit_hours
    # sha256("global:submit_hours")[:8]
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

    # Instruction discriminator for withdraw
    # sha256("global:withdraw")[:8]
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
