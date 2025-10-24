"""
Oracle - The Trusted Authority for Loggerheads

DEPRECATED: This file now imports from oracle_secure.py
See docs/ORACLE_SECURITY.md for security best practices.

This module provides backwards compatibility while defaulting to secure oracle loading.
"""

from solders.keypair import Keypair
from .oracle_secure import (
    get_oracle_keypair as get_secure_oracle_keypair,
    get_oracle_pubkey as get_secure_oracle_pubkey,
)


def get_oracle_keypair() -> Keypair:
    """
    Returns the oracle keypair (allows demo for backwards compatibility).
    
    See oracle_secure.py for secure production usage.
    """
    return get_secure_oracle_keypair(allow_demo=True)


def get_oracle_pubkey() -> str:
    """
    Returns the oracle public key as a string.
    
    Admins use this when creating vaults to specify which oracle they trust.
    """
    return get_secure_oracle_pubkey(allow_demo=True)


# Print oracle pubkey for admin reference
if __name__ == "__main__":
    print("Loggerheads Oracle Public Key:")
    print(get_oracle_pubkey())
    print("\n⚠️  For production setup, see: docs/ORACLE_SECURITY.md")
    print("Generate secure keypair: python -m loggerheads.oracle_secure --generate")
