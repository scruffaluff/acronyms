"""Application runtime settings."""


import functools
from pathlib import Path
import sys
from typing import Any, cast, Dict, Optional, Tuple

from pydantic import AnyUrl, BaseSettings, SecretStr
from pydantic.env_settings import SettingsSourceCallable
import yaml


def secrets_directory() -> Optional[str]:
    """Find operating system specific folder for application secrets."""
    if sys.platform == "linux":
        path = "/run/secrets"
        return path if Path(path).exists() else None
    elif sys.platform == "win32":
        path = r"C:\ProgramData\Docker\secrets"
        return path if Path(path).exists() else None
    else:
        return None


def yaml_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    """Load application settings from YAML file."""
    try:
        text = Path("config.yaml").read_text()
        return cast(Dict[str, Any], yaml.safe_load(text))
    except FileNotFoundError:
        return {}


class DatabaseUrl(AnyUrl):
    """Custom validator for database connections."""

    host_required = False


class Settings(BaseSettings):
    """Application settings."""

    database: DatabaseUrl = DatabaseUrl(
        "sqlite+aiosqlite:///./acronyms.db", scheme="sqlite"
    )
    page_size: int = 10
    port: int = 8000
    reset_token: SecretStr
    smtp_host: str
    smtp_password: SecretStr
    smtp_port: int = 25
    smtp_tls: bool = True
    smtp_username: str
    verification_token: SecretStr

    class Config:
        """Pydantic specific configuration."""

        env_nested_delimiter = "__"
        env_prefix = "acronyms_"
        secrets_dir = secrets_directory()

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            """Append YAML file as source of configuration."""
            return (
                init_settings,
                env_settings,
                file_secret_settings,
                yaml_config_settings_source,
            )


@functools.lru_cache(maxsize=1)
def settings() -> Settings:
    """Load application settings."""
    return Settings()
