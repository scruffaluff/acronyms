"""Custom types for Acronyms."""


from typing import Annotated

from pydantic.networks import MultiHostUrl, Url, UrlConstraints


PostgresDsn = Annotated[
    MultiHostUrl,
    UrlConstraints(
        host_required=True,
        allowed_schemes=[
            "postgres",
            "postgresql",
            "postgresql+asyncpg",
        ],
    ),
]

SqliteDsn = Annotated[
    Url, UrlConstraints(allowed_schemes=["sqlite", "sqlite+aiosqlite"])
]
