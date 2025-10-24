"""
Custom exceptions for Loggerheads with helpful error messages.
"""


class LoggerheadsError(Exception):
    """Base exception for all Loggerheads errors."""
    def __init__(self, message: str, fix: str = None):
        self.message = message
        self.fix = fix
        super().__init__(message)


class ConfigurationError(LoggerheadsError):
    """Configuration or setup related errors."""
    pass


class WalletError(LoggerheadsError):
    """Wallet loading or balance errors."""
    pass


class VaultError(LoggerheadsError):
    """Vault creation or interaction errors."""
    pass


class BlockchainError(LoggerheadsError):
    """Blockchain transaction errors."""
    pass


class TrackingError(LoggerheadsError):
    """Work tracking related errors."""
    pass


class OracleError(LoggerheadsError):
    """Oracle keypair or signing errors."""
    pass


class InsufficientFundsError(WalletError):
    """Insufficient funds in wallet."""
    def __init__(self, required: float, available: float):
        self.required = required
        self.available = available
        message = f"Insufficient funds: need {required:.2f} USDC, have {available:.2f} USDC"
        fix = (
            "Get more USDC:\n"
            f"  • Need additional: {required - available:.2f} USDC\n"
            "  • On devnet: solana airdrop 2 && spl-token mint USDC_MINT 1000\n"
            "  • On mainnet: purchase USDC from an exchange"
        )
        super().__init__(message, fix)


class VaultNotFoundError(VaultError):
    """Vault configuration not found."""
    def __init__(self):
        message = "No vault configured"
        fix = (
            "Setup required:\n"
            "  • Employees: Run 'loggerheads' and choose Employee\n"
            "  • Employers: Run 'loggerheads' and choose Employer"
        )
        super().__init__(message, fix)


class TrackerNotRunningError(TrackingError):
    """Tracker is not running."""
    def __init__(self):
        message = "Work tracker is not running"
        fix = "Start tracking: loggerheads start"
        super().__init__(message, fix)


class NoWorkToSubmitError(TrackingError):
    """No work hours to submit."""
    def __init__(self):
        message = "No work tracked today (0 hours)"
        fix = (
            "Track work first:\n"
            "  • Start tracker: loggerheads start\n"
            "  • Or generate demo data: loggerheads demo --hours 8"
        )
        super().__init__(message, fix)


class OracleKeypairNotFoundError(OracleError):
    """Oracle keypair not found (production mode)."""
    def __init__(self):
        message = "No secure oracle keypair found"
        fix = (
            "Production setup required:\n"
            "  1. Generate keypair: python3 -m loggerheads.oracle_secure --generate\n"
            "  2. Set environment: export ORACLE_KEYPAIR_PATH=~/.loggerheads/oracle-keypair.json\n"
            "  3. Add to shell config for persistence\n\n"
            "For testing/demo only, set: LOGGERHEADS_ALLOW_DEMO_ORACLE=true"
        )
        super().__init__(message, fix)
