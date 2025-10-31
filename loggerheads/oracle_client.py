"""
Oracle API Client

Communicates with the independent oracle service to submit work hours.
"""

import requests
from typing import Optional


class OracleClient:
    """Client for interacting with Kapture Oracle API."""

    def __init__(self, oracle_url: str = None):
        """
        Initialize oracle client.

        Args:
            oracle_url: Base URL of oracle service (default: http://localhost:5001)
        """
        if oracle_url is None:
            oracle_url = self._get_default_oracle_url()

        self.base_url = oracle_url.rstrip('/')

    def _get_default_oracle_url(self) -> str:
        """Get oracle URL from environment or use default."""
        import os
        return os.getenv('KAPTURE_ORACLE_URL', 'https://kapture-oracle.onrender.com')

    def health_check(self) -> dict:
        """
        Check if oracle service is running.

        Returns:
            Dict with status, oracle_pubkey, timestamp

        Raises:
            ConnectionError: If oracle is unreachable
        """
        try:
            # 60 second timeout to handle Render free tier cold starts (can take 30-60s)
            response = requests.get(f"{self.base_url}/health", timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Cannot reach oracle service at {self.base_url}: {e}")

    def get_oracle_pubkey(self) -> str:
        """
        Get oracle public key.

        Returns:
            Oracle public key as string

        Raises:
            ConnectionError: If oracle is unreachable
        """
        try:
            # 60 second timeout to handle Render free tier cold starts (can take 30-60s)
            response = requests.get(f"{self.base_url}/oracle-pubkey", timeout=60)
            response.raise_for_status()
            data = response.json()
            return data['oracle_pubkey']
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Cannot reach oracle service: {e}")

    def submit_hours(
        self,
        employee_wallet: str,
        admin_wallet: str,
        hours: float,
        proof: Optional[dict] = None
    ) -> dict:
        """
        Submit work hours to oracle for verification and blockchain submission.

        Args:
            employee_wallet: Employee wallet address
            admin_wallet: Admin/employer wallet address
            hours: Hours worked (can be decimal, will be rounded)
            proof: Optional work proof (screenshots, timestamps, etc.)

        Returns:
            Dict with:
            - success: bool
            - transaction_signature: str
            - vault_status: dict with balances
            - explorer_url: str

        Raises:
            ConnectionError: If oracle is unreachable
            ValueError: If submission is rejected by oracle
        """
        if proof is None:
            proof = {}

        payload = {
            'employee_wallet': employee_wallet,
            'admin_wallet': admin_wallet,
            'hours': hours,
            'proof': proof
        }

        try:
            response = requests.post(
                f"{self.base_url}/submit-hours",
                json=payload,
                timeout=30  # Blockchain submission can take time
            )

            data = response.json()

            if response.status_code == 200 and data.get('success'):
                return data
            else:
                error_msg = data.get('error', 'Unknown error')
                raise ValueError(f"Oracle rejected submission: {error_msg}")

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to submit to oracle: {e}")

    def get_vault_status(self, employee_wallet: str, admin_wallet: str) -> dict:
        """
        Get vault status from oracle.

        Args:
            employee_wallet: Employee wallet address
            admin_wallet: Admin wallet address

        Returns:
            Dict with vault information

        Raises:
            ConnectionError: If oracle is unreachable
            ValueError: If vault not found
        """
        payload = {
            'employee_wallet': employee_wallet,
            'admin_wallet': admin_wallet
        }

        try:
            # 60 second timeout to handle Render free tier cold starts
            response = requests.post(
                f"{self.base_url}/vault-status",
                json=payload,
                timeout=60
            )

            data = response.json()

            if response.status_code == 200 and data.get('success'):
                return data['vault']
            else:
                error_msg = data.get('error', 'Unknown error')
                raise ValueError(f"Failed to get vault status: {error_msg}")

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to reach oracle: {e}")


def get_oracle_client(oracle_url: Optional[str] = None) -> OracleClient:
    """
    Get oracle client instance.

    Args:
        oracle_url: Optional oracle URL override

    Returns:
        Configured OracleClient
    """
    return OracleClient(oracle_url)
