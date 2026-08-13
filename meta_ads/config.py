"""Configuration loading for the Meta Marketing API client.

All credentials come from environment variables so nothing sensitive ever
lives in the repo. Locally you can put them in a `.env` file (see
`.env.example`); in CI they're injected from GitHub Actions secrets.
"""
from __future__ import annotations

import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover - dotenv is optional at runtime
    pass

# Trade Covenant's ad account. Not sensitive (it's not a credential), so it's
# safe to default here for convenience -- override with META_AD_ACCOUNT_ID.
DEFAULT_AD_ACCOUNT_ID = "1222452979529550"
DEFAULT_API_VERSION = "v21.0"


class ConfigError(Exception):
    """Raised when required configuration is missing or invalid."""


def _normalize_account_id(raw: str) -> str:
    raw = raw.strip()
    return raw if raw.startswith("act_") else f"act_{raw}"


class Config:
    def __init__(self) -> None:
        self.access_token = os.environ.get("META_ACCESS_TOKEN", "").strip()
        self.ad_account_id = _normalize_account_id(
            os.environ.get("META_AD_ACCOUNT_ID", DEFAULT_AD_ACCOUNT_ID)
        )
        self.api_version = os.environ.get("META_API_VERSION", DEFAULT_API_VERSION).strip()

    def validate(self) -> None:
        missing = []
        if not self.access_token:
            missing.append("META_ACCESS_TOKEN")
        if self.ad_account_id in ("act_", ""):
            missing.append("META_AD_ACCOUNT_ID")
        if missing:
            raise ConfigError(
                "Missing required environment variable(s): "
                + ", ".join(missing)
                + ". Set them in your shell, a local .env file, or as GitHub "
                "Actions secrets on this repo."
            )


def load_config() -> Config:
    cfg = Config()
    cfg.validate()
    return cfg
