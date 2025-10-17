"""
Vault configuration management.
Stores vault addresses so users don't have to type them repeatedly.

SIMPLIFIED: Now only stores employee + admin wallets!
Everything else (vault PDA, token accounts) is derived automatically.
"""

import json
import os
from pathlib import Path
from .blockchain import derive_all_vault_addresses


class VaultConfig:
    """Manages vault configuration."""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.expanduser("~/.loggerheads_vault.json")
        self.config_path = config_path
        self.config = self.load()

    def load(self) -> dict:
        """Load configuration from file."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {}

    def save(self):
        """Save configuration to file."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def set_vault(self, employee_pubkey: str, admin_pubkey: str):
        """
        Store vault configuration - SIMPLIFIED!

        Now only requires 2 addresses. Everything else is derived automatically.

        Args:
            employee_pubkey: Employee wallet address
            admin_pubkey: Admin wallet address
        """
        self.config['vault'] = {
            'employee_pubkey': employee_pubkey,
            'admin_pubkey': admin_pubkey
        }
        self.save()

    def get_vault(self) -> dict:
        """
        Get vault configuration with ALL addresses derived automatically.

        Returns:
            Dict with employee_pubkey, admin_pubkey, vault_pda,
            vault_token_account, employee_token_account (all derived!)
        """
        stored = self.config.get('vault', {})

        if not stored:
            return {}

        # Derive all addresses from just the 2 stored addresses
        return derive_all_vault_addresses(
            stored['employee_pubkey'],
            stored['admin_pubkey']
        )

    def has_vault(self) -> bool:
        """Check if vault is configured."""
        return 'vault' in self.config and bool(self.config['vault'])

    def enable_auto_submit(self, enabled: bool = True, time: str = "18:00"):
        """Enable/disable automatic submission."""
        self.config['auto_submit'] = {
            'enabled': enabled,
            'time': time
        }
        self.save()

    def is_auto_submit_enabled(self) -> bool:
        """Check if auto-submit is enabled."""
        return self.config.get('auto_submit', {}).get('enabled', False)

    def get_auto_submit_time(self) -> str:
        """Get auto-submit time."""
        return self.config.get('auto_submit', {}).get('time', '18:00')

    def clear(self):
        """Clear all configuration."""
        self.config = {}
        self.save()

    def print_config(self, show_technical=False):
        """
        Print current configuration.

        Args:
            show_technical: If True, show technical blockchain details (PDAs, token accounts)
                          Default False - users don't need to see these!
        """
        if not self.has_vault():
            print("\n❌ No work account set up yet")
            print("\n💡 Get started: loggerheads setup-vault")
            return

        vault = self.get_vault()
        print("\n" + "="*60)
        print("📋 Your Work Account")
        print("="*60)

        # Show user-friendly info only
        print(f"\n👤 Your Wallet:")
        print(f"   {vault['employee_pubkey'][:16]}...{vault['employee_pubkey'][-8:]}")

        print(f"\n👔 Employer:")
        print(f"   {vault['admin_pubkey'][:16]}...{vault['admin_pubkey'][-8:]}")

        if self.is_auto_submit_enabled():
            print(f"\n⏰ Auto-Submit: ✅ Enabled")
            print(f"   Your hours are automatically submitted at {self.get_auto_submit_time()}")
        else:
            print(f"\n⏰ Auto-Submit: ❌ Disabled")
            print(f"   Remember to run 'loggerheads submit' daily")

        # Only show technical details if explicitly requested (for debugging)
        if show_technical:
            print(f"\n" + "-"*60)
            print(f"🔧 Technical Details (for debugging):")
            print(f"-"*60)
            print(f"   Vault PDA:      {vault['vault_pda'][:20]}...")
            print(f"   Vault Token:    {vault['vault_token_account'][:20]}...")
            print(f"   Employee Token: {vault['employee_token_account'][:20]}...")
            print(f"   Config file:    {self.config_path}")

        print("\n" + "="*60 + "\n")
