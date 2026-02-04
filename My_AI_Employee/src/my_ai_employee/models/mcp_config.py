"""
MCP Config data model for Silver Tier AI Employee.

Defines the schema for MCP server configuration (endpoints, credentials, retry policies).
"""

from dataclasses import dataclass, field
from typing import Literal, Dict, Any, Optional


@dataclass
class MCPConfigSchema:
    """
    MCP Config entity schema.

    Storage location: .env file (loaded as environment variables)
    """

    server_name: Literal["email", "linkedin", "browser"]
    enabled: bool = True

    # Endpoint configuration
    host: str = "localhost"
    port: int = 8000

    # Retry policy
    max_retries: int = 3
    backoff_seconds: list[int] = field(default_factory=lambda: [1, 2, 4])

    # Rate limits (per day)
    rate_limit_daily: Optional[int] = None

    # Dry-run mode
    dry_run: bool = True

    # Authentication (references to env vars, not actual credentials)
    auth_type: Literal["oauth2", "api_key", "session_cookie"] = "oauth2"
    credential_env_vars: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Validate MCP config data."""
        if not self.server_name:
            raise ValueError("server_name is required")
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if len(self.backoff_seconds) != self.max_retries:
            raise ValueError("backoff_seconds length must equal max_retries")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "server_name": self.server_name,
            "enabled": self.enabled,
            "host": self.host,
            "port": self.port,
            "max_retries": self.max_retries,
            "backoff_seconds": self.backoff_seconds,
            "rate_limit_daily": self.rate_limit_daily,
            "dry_run": self.dry_run,
            "auth_type": self.auth_type,
            "credential_env_vars": self.credential_env_vars,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MCPConfigSchema":
        """Create MCPConfigSchema from dictionary."""
        return cls(
            server_name=data["server_name"],
            enabled=data.get("enabled", True),
            host=data.get("host", "localhost"),
            port=data.get("port", 8000),
            max_retries=data.get("max_retries", 3),
            backoff_seconds=data.get("backoff_seconds", [1, 2, 4]),
            rate_limit_daily=data.get("rate_limit_daily"),
            dry_run=data.get("dry_run", True),
            auth_type=data.get("auth_type", "oauth2"),
            credential_env_vars=data.get("credential_env_vars", {}),
        )

    @classmethod
    def create_email_config(cls) -> "MCPConfigSchema":
        """Create default configuration for email MCP server."""
        return cls(
            server_name="email",
            credential_env_vars={
                "credentials_file": "GMAIL_CREDENTIALS_FILE",
                "token_file": "GMAIL_TOKEN_FILE",
                "scopes": "GMAIL_SCOPES",
            },
        )

    @classmethod
    def create_linkedin_config(cls) -> "MCPConfigSchema":
        """Create default configuration for LinkedIn MCP server."""
        return cls(
            server_name="linkedin",
            rate_limit_daily=100,
            credential_env_vars={
                "access_token": "LINKEDIN_ACCESS_TOKEN",
                "person_urn": "LINKEDIN_PERSON_URN",
            },
        )

    @classmethod
    def create_browser_config(cls) -> "MCPConfigSchema":
        """Create default configuration for browser automation MCP server."""
        return cls(
            server_name="browser",
            auth_type="session_cookie",
            credential_env_vars={
                "session_dir": "WHATSAPP_SESSION_DIR",
                "cdp_port": "WHATSAPP_CDP_PORT",
            },
        )
