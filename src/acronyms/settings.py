"""Application runtime settings."""


import functools
import os
from pathlib import Path
import secrets
import sys
from typing import Any, Dict, Literal, Optional, Tuple, Type, Union, cast

from pydantic import SecretStr
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)
import yaml

from acronyms.typing import PostgresDsn, SqliteDsn


def secrets_directory() -> Optional[str]:
    """Find operating system specific folder for application secrets."""
    try:
        return os.environ["ACRONYMS_SECRETS_DIR"]
    except KeyError:
        if sys.platform == "linux":
            path = "/run/secrets"
            return path if Path(path).exists() else None
        elif sys.platform == "win32":
            path = r"C:\ProgramData\Docker\secrets"
            return path if Path(path).exists() else None
        else:
            return None


class Settings(BaseSettings):
    """Application settings."""

    database: Union[PostgresDsn, SqliteDsn] = SqliteDsn(
        "sqlite+aiosqlite:///./acronyms.db"
    )
    host: str = "127.0.0.1"
    log_level: Literal[
        "critical", "error", "warning", "info", "debug", "trace"
    ] = "warning"
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_prefix="ACRONYMS_",
        secrets_dir=secrets_directory(),
    )
    page_size: int = 10
    port: int = 8000
    reset_token: SecretStr = SecretStr(secrets.token_urlsafe(32))
    smtp_enabled: bool = False
    smtp_host: str = ""
    smtp_password: SecretStr = SecretStr("")
    smtp_port: int = 25
    smtp_tls: bool = True
    smtp_username: str = ""
    ssl_certfile: Optional[Path] = None
    ssl_keyfile: Optional[Path] = None
    verification_token: SecretStr = SecretStr(secrets.token_urlsafe(64))

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        """Customise source list for settings."""
        return (
            init_settings,
            env_settings,
            file_secret_settings,
            YamlConfigSettings(settings_cls),
        )


class YamlConfigSettings(PydanticBaseSettingsSource):
    """Provides application settings from YAML file."""

    def __call__(self) -> Dict[str, Any]:
        """Load application settings from YAML file."""
        return self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        if not hasattr(self, "_data"):
            try:
                text = (Path.home() / ".acronyms/config.yaml").read_text()
                self._data = cast(Dict[str, Any], yaml.safe_load(text))
            except FileNotFoundError:
                self._data = {}
        return self._data

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> Tuple[Any, str, bool]:
        """Retrieve field value."""
        return self._load_data()[field_name], field_name, False


@functools.lru_cache(maxsize=1)
def settings() -> Settings:
    """Load application settings."""
    return Settings()
