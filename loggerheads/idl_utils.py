"""
IDL utilities for extracting instruction discriminators and other metadata.
This ensures Python code stays in sync with the deployed Anchor program.
"""

import json
from pathlib import Path
from typing import Dict, List


def load_idl(idl_path: str = None) -> dict:
    """
    Load the IDL JSON file.

    Args:
        idl_path: Path to the IDL file. Defaults to workchain-program IDL.

    Returns:
        IDL dictionary
    """
    if idl_path is None:
        # Default to the workchain-program IDL
        project_root = Path(__file__).parent.parent
        idl_path = project_root / "workchain-program" / "target" / "idl" / "workchain_program.json"

    with open(idl_path, 'r') as f:
        return json.load(f)


def get_instruction_discriminators(idl: dict = None) -> Dict[str, bytes]:
    """
    Extract all instruction discriminators from the IDL.

    Args:
        idl: IDL dictionary (loads default if None)

    Returns:
        Dictionary mapping instruction names to discriminator bytes
    """
    if idl is None:
        idl = load_idl()

    discriminators = {}

    for instruction in idl.get('instructions', []):
        name = instruction['name']
        disc_list = instruction['discriminator']
        discriminators[name] = bytes(disc_list)

    return discriminators


def get_discriminator(instruction_name: str, idl: dict = None) -> bytes:
    """
    Get the discriminator for a specific instruction.

    Args:
        instruction_name: Name of the instruction (e.g., "initialize_vault")
        idl: IDL dictionary (loads default if None)

    Returns:
        Discriminator bytes

    Raises:
        KeyError: If instruction not found in IDL
    """
    discriminators = get_instruction_discriminators(idl)

    if instruction_name not in discriminators:
        available = ', '.join(discriminators.keys())
        raise KeyError(f"Instruction '{instruction_name}' not found in IDL. Available: {available}")

    return discriminators[instruction_name]


def verify_program_id(expected_program_id: str, idl: dict = None) -> bool:
    """
    Verify that the program ID matches the IDL.

    Args:
        expected_program_id: The program ID string to verify
        idl: IDL dictionary (loads default if None)

    Returns:
        True if program IDs match, False otherwise
    """
    if idl is None:
        idl = load_idl()

    idl_program_id = idl.get('address')
    return idl_program_id == expected_program_id


def get_program_id(idl: dict = None) -> str:
    """
    Get the program ID from the IDL.

    Args:
        idl: IDL dictionary (loads default if None)

    Returns:
        Program ID string
    """
    if idl is None:
        idl = load_idl()

    return idl.get('address')


def print_instruction_info():
    """Print all instruction discriminators for debugging."""
    idl = load_idl()
    discriminators = get_instruction_discriminators(idl)

    print("\n" + "="*70)
    print("INSTRUCTION DISCRIMINATORS")
    print("="*70)
    print(f"\nProgram ID: {idl.get('address')}")
    print(f"\nInstructions:")

    for name, disc in discriminators.items():
        disc_list = list(disc)
        print(f"  {name:20} -> bytes({disc_list})")
    print()


if __name__ == "__main__":
    # When run directly, print instruction info for debugging
    print_instruction_info()
