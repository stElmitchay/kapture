"""
Token utility functions for checking balances and minting devnet tokens.
"""

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
from .blockchain import (
    get_associated_token_address,
    create_associated_token_account_instruction,
    check_token_account_exists,
    TOKEN_PROGRAM_ID,
    USDC_MINT,
    DEFAULT_RPC_URL,
    load_keypair
)


def get_token_balance(owner: Pubkey, mint: Pubkey = USDC_MINT, rpc_url: str = DEFAULT_RPC_URL) -> float:
    """
    Get the token balance for a wallet.

    Args:
        owner: Wallet public key
        mint: Token mint (defaults to USDC)
        rpc_url: Solana RPC endpoint

    Returns:
        Balance in USDC (human-readable, e.g., 1000.50)
    """
    client = Client(rpc_url)
    token_account = get_associated_token_address(owner, mint)

    # Check if token account exists
    if not check_token_account_exists(token_account, client):
        return 0.0

    try:
        response = client.get_token_account_balance(token_account, commitment=Confirmed)
        if response.value:
            # Convert from lamports to USDC (6 decimals)
            lamports = int(response.value.amount)
            return lamports / 1_000_000
        return 0.0
    except Exception as e:
        print(f"Error fetching balance: {e}")
        return 0.0


def get_sol_balance(pubkey: Pubkey, rpc_url: str = DEFAULT_RPC_URL) -> float:
    """
    Get SOL balance for a wallet.

    Args:
        pubkey: Wallet public key
        rpc_url: Solana RPC endpoint

    Returns:
        Balance in SOL
    """
    client = Client(rpc_url)
    try:
        response = client.get_balance(pubkey, commitment=Confirmed)
        lamports = response.value
        return lamports / 1_000_000_000  # Convert lamports to SOL
    except Exception as e:
        print(f"Error fetching SOL balance: {e}")
        return 0.0


def mint_devnet_usdc(
    recipient: Pubkey,
    amount_usdc: float,
    mint_authority: Keypair,
    rpc_url: str = DEFAULT_RPC_URL
) -> str:
    """
    Mint devnet USDC to a recipient's token account.

    NOTE: This only works if you control the mint authority for the devnet USDC mint.
    For public devnet USDC mints, you'll need to use a faucet instead.

    Args:
        recipient: Recipient's wallet public key
        amount_usdc: Amount of USDC to mint
        mint_authority: Keypair with mint authority
        rpc_url: Solana RPC endpoint

    Returns:
        Transaction signature
    """
    client = Client(rpc_url)
    recipient_token_account = get_associated_token_address(recipient, USDC_MINT)

    instructions = []

    # Create token account if it doesn't exist
    if not check_token_account_exists(recipient_token_account, client):
        print(f"Creating token account for {recipient}...")
        create_ata_ix = create_associated_token_account_instruction(
            mint_authority.pubkey(),
            recipient,
            USDC_MINT
        )
        instructions.append(create_ata_ix)

    # Mint tokens
    amount_lamports = int(amount_usdc * 1_000_000)

    # MintTo instruction: discriminator [7] + amount (u64)
    mint_to_data = bytes([7]) + struct.pack('<Q', amount_lamports)

    mint_to_accounts = [
        AccountMeta(pubkey=USDC_MINT, is_signer=False, is_writable=True),
        AccountMeta(pubkey=recipient_token_account, is_signer=False, is_writable=True),
        AccountMeta(pubkey=mint_authority.pubkey(), is_signer=True, is_writable=False),
    ]

    mint_to_ix = Instruction(
        program_id=TOKEN_PROGRAM_ID,
        accounts=mint_to_accounts,
        data=mint_to_data
    )
    instructions.append(mint_to_ix)

    # Send transaction
    blockhash_resp = client.get_latest_blockhash(Confirmed)
    recent_blockhash = blockhash_resp.value.blockhash

    message = Message.new_with_blockhash(instructions, mint_authority.pubkey(), recent_blockhash)
    transaction = Transaction([mint_authority], message, recent_blockhash)

    opts = TxOpts(skip_preflight=False, preflight_commitment=Confirmed)
    result = client.send_transaction(transaction, opts)

    signature = str(result.value)
    client.confirm_transaction(result.value, Confirmed)

    print(f"✅ Minted {amount_usdc} USDC to {recipient}")
    print(f"   Signature: {signature}")

    return signature


def check_vault_funding_requirements(
    admin_pubkey: Pubkey,
    locked_amount: float,
    rpc_url: str = DEFAULT_RPC_URL
) -> dict:
    """
    Check if admin has sufficient funds to create vault.

    Args:
        admin_pubkey: Admin's wallet public key
        locked_amount: Amount of USDC to lock in vault
        rpc_url: Solana RPC endpoint

    Returns:
        Dict with balance info and whether admin can fund vault
    """
    usdc_balance = get_token_balance(admin_pubkey, USDC_MINT, rpc_url)
    sol_balance = get_sol_balance(admin_pubkey, rpc_url)

    can_fund = usdc_balance >= locked_amount
    sol_sufficient = sol_balance > 0.01  # Need ~0.01 SOL for transaction fees

    return {
        'usdc_balance': usdc_balance,
        'sol_balance': sol_balance,
        'locked_amount': locked_amount,
        'can_fund_vault': can_fund,
        'sol_sufficient': sol_sufficient,
        'usdc_needed': max(0, locked_amount - usdc_balance),
        'ready': can_fund and sol_sufficient
    }


def display_balance_info(wallet_address: str):
    """Display balance information for a wallet."""
    pubkey = Pubkey.from_string(wallet_address)

    print("\n" + "="*70)
    print("WALLET BALANCE")
    print("="*70)
    print(f"\nWallet: {wallet_address}")

    sol_balance = get_sol_balance(pubkey)
    usdc_balance = get_token_balance(pubkey)

    print(f"\nSOL Balance:  {sol_balance:.4f} SOL")
    print(f"USDC Balance: {usdc_balance:.2f} USDC")

    if sol_balance < 0.01:
        print("\n⚠️  Low SOL balance! You may not have enough for transaction fees.")
        print("   Get devnet SOL: solana airdrop 2")

    if usdc_balance == 0:
        print("\n⚠️  No USDC! You need USDC to create a vault.")
        print("   See instructions below to get devnet USDC.")

    print()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        wallet_address = sys.argv[1]
        display_balance_info(wallet_address)
    else:
        # Load default wallet
        try:
            keypair = load_keypair()
            display_balance_info(str(keypair.pubkey()))
        except Exception as e:
            print(f"Error: {e}")
            print("\nUsage: python -m loggerheads.token_utils <wallet_address>")
