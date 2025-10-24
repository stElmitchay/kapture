"""
Secure Oracle - Trusted Authority for Loggerheads

SECURITY MODEL:
- Oracle private key MUST be kept secure and NEVER committed to git
- Each deployment should use its own oracle keypair
- Oracle keypair loaded from environment variable or secure file
- Fallback to embedded key only for testing/demo purposes

Production Setup:
1. Generate oracle keypair: python -m loggerheads.oracle_secure --generate
2. Set environment: export ORACLE_KEYPAIR_PATH=/secure/path/oracle-keypair.json
3. Or store in config: ~/.loggerheads/oracle-keypair.json
"""

import os
import json
from pathlib import Path
from solders.keypair import Keypair
from typing import Optional

# Demo oracle for testing ONLY (low security, public knowledge)
_DEMO_ORACLE_SECRET = [
    198, 80, 45, 77, 197, 116, 18, 227, 149, 84, 106, 32, 167, 125, 128, 32,
    194, 168, 45, 238, 219, 215, 16, 134, 180, 47, 21, 131, 51, 170, 248, 43,
    233, 106, 203, 87, 104, 44, 157, 27, 162, 29, 234, 105, 209, 150, 124, 243,
    188, 66, 110, 68, 43, 195, 56, 36, 50, 81, 212, 128, 191, 236, 174, 87
]


def get_oracle_keypair_path() -> Optional[Path]:
    """
    Find oracle keypair in order of precedence:
    1. ORACLE_KEYPAIR_PATH environment variable
    2. ~/.loggerheads/oracle-keypair.json
    3. None (will use demo oracle with warning)
    """
    # Check environment variable
    env_path = os.getenv('ORACLE_KEYPAIR_PATH')
    if env_path:
        path = Path(env_path).expanduser()
        if path.exists():
            return path
        else:
            print(f"⚠️  Warning: ORACLE_KEYPAIR_PATH set but file not found: {path}")
    
    # Check default config location
    default_path = Path.home() / '.loggerheads' / 'oracle-keypair.json'
    if default_path.exists():
        return default_path
    
    return None


def load_oracle_keypair_from_file(path: Path) -> Keypair:
    """Load oracle keypair from JSON file."""
    try:
        with open(path, 'r') as f:
            data = json.load(f)
            return Keypair.from_bytes(bytes(data))
    except Exception as e:
        raise RuntimeError(f"Failed to load oracle keypair from {path}: {e}")


def get_oracle_keypair(allow_demo: bool = False) -> Keypair:
    """
    Returns the oracle keypair with security checks.
    
    Args:
        allow_demo: If True, allows using demo oracle for testing.
                    If False, raises error if no secure keypair found.
    
    Returns:
        Oracle keypair
        
    Raises:
        RuntimeError: If no oracle keypair found and allow_demo=False
    """
    keypair_path = get_oracle_keypair_path()
    
    if keypair_path:
        return load_oracle_keypair_from_file(keypair_path)
    
    # No secure keypair found
    if allow_demo:
        print("\n" + "="*70)
        print("⚠️  WARNING: Using demo oracle keypair (NOT SECURE)")
        print("="*70)
        print("This is for TESTING/DEMO ONLY. Anyone can forge work submissions.")
        print("\nFor production:")
        print("  1. Generate keypair: python -m loggerheads.oracle_secure --generate")
        print("  2. Set path: export ORACLE_KEYPAIR_PATH=/path/to/oracle-keypair.json")
        print("="*70 + "\n")
        return Keypair.from_bytes(_DEMO_ORACLE_SECRET)
    else:
        raise RuntimeError(
            "No oracle keypair found!\n\n"
            "Production requires a secure oracle keypair:\n"
            "  1. Generate: python -m loggerheads.oracle_secure --generate\n"
            "  2. Set: export ORACLE_KEYPAIR_PATH=/path/to/oracle-keypair.json\n"
            "  Or copy to: ~/.loggerheads/oracle-keypair.json\n\n"
            "For testing/demo only, use allow_demo=True"
        )


def get_oracle_pubkey(allow_demo: bool = False) -> str:
    """
    Returns the oracle public key as a string.
    
    Args:
        allow_demo: If True, allows using demo oracle for testing.
    """
    return str(get_oracle_keypair(allow_demo=allow_demo).pubkey())


def generate_oracle_keypair(output_path: Optional[Path] = None) -> Keypair:
    """
    Generate a new oracle keypair and save to file.
    
    Args:
        output_path: Where to save keypair. Defaults to ~/.loggerheads/oracle-keypair.json
        
    Returns:
        Generated keypair
    """
    if output_path is None:
        output_path = Path.home() / '.loggerheads' / 'oracle-keypair.json'
    
    # Generate new keypair
    keypair = Keypair()
    
    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to file (secure permissions)
    keypair_bytes = bytes(keypair)
    with open(output_path, 'w') as f:
        json.dump(list(keypair_bytes), f)
    
    # Set secure file permissions (owner read/write only)
    os.chmod(output_path, 0o600)
    
    print(f"✅ Oracle keypair generated: {output_path}")
    print(f"🔑 Public key: {keypair.pubkey()}")
    print(f"\n⚠️  IMPORTANT: Keep this file secure and NEVER commit to git!")
    print(f"\nTo use this oracle:")
    print(f"  export ORACLE_KEYPAIR_PATH={output_path}")
    print(f"\nOr add to ~/.bashrc or ~/.zshrc for persistence")
    
    return keypair


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--generate':
        # Generate new oracle keypair
        if len(sys.argv) > 2:
            output_path = Path(sys.argv[2])
        else:
            output_path = None
        generate_oracle_keypair(output_path)
    elif len(sys.argv) > 1 and sys.argv[1] == '--pubkey':
        # Show current oracle pubkey
        try:
            pubkey = get_oracle_pubkey(allow_demo=True)
            print(f"Current Oracle Public Key: {pubkey}")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        print("Loggerheads Oracle Key Management")
        print("\nUsage:")
        print("  python -m loggerheads.oracle_secure --generate [output_path]")
        print("  python -m loggerheads.oracle_secure --pubkey")
        print("\nExamples:")
        print("  # Generate in default location (~/.loggerheads/oracle-keypair.json)")
        print("  python -m loggerheads.oracle_secure --generate")
        print("\n  # Generate in custom location")
        print("  python -m loggerheads.oracle_secure --generate /secure/oracle-keypair.json")
        print("\n  # Show current oracle public key")
        print("  python -m loggerheads.oracle_secure --pubkey")
