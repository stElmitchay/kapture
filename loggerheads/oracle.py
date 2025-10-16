"""
Embedded Oracle - The Trusted Authority for Loggerheads

This oracle keypair is embedded in the loggerheads software itself.
When an employee submits their hours, this oracle signs the transaction,
acting as the trusted verification mechanism.

Security Model:
- Oracle is part of the software (like a built-in certificate)
- Employees cannot easily fake hours without reverse-engineering the entire app
- Admin creates vaults trusting THIS specific oracle public key
- Similar to how Time Doctor, Hubstaff, etc. have embedded authentication
"""

from solders.keypair import Keypair

# Embedded oracle keypair (DO NOT MODIFY)
# This is the trusted authority for all WorkChain installations
_ORACLE_SECRET = [
    198, 80, 45, 77, 197, 116, 18, 227, 149, 84, 106, 32, 167, 125, 128, 32,
    194, 168, 45, 238, 219, 215, 16, 134, 180, 47, 21, 131, 51, 170, 248, 43,
    233, 106, 203, 87, 104, 44, 157, 27, 162, 29, 234, 105, 209, 150, 124, 243,
    188, 66, 110, 68, 43, 195, 56, 36, 50, 81, 212, 128, 191, 236, 174, 87
]


def get_oracle_keypair() -> Keypair:
    """
    Returns the embedded oracle keypair.

    This oracle acts as the trusted authority for work verification.
    All work submissions are signed by this oracle to prove legitimacy.
    """
    return Keypair.from_bytes(_ORACLE_SECRET)


def get_oracle_pubkey() -> str:
    """
    Returns the oracle public key as a string.

    Admins use this when creating vaults to specify which oracle they trust.
    """
    return str(get_oracle_keypair().pubkey())


# Print oracle pubkey for admin reference
if __name__ == "__main__":
    print("Loggerheads Oracle Public Key:")
    print(get_oracle_pubkey())
    print("\nAdmins: Use this public key when creating vaults.")
