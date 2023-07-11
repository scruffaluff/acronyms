"""Authentication management."""


from typing import AsyncIterator, Optional
from uuid import UUID

from fastapi import Depends, FastAPI, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
)
from fastapi_users.authentication.strategy.db import (
    AccessTokenDatabase,
    DatabaseStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase

from acronyms import email, models, settings
from acronyms.models import AccessToken, User
from acronyms.schemas import UserCreate, UserRead, UserUpdate


class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    """User database manager."""

    reset_password_token_secret = settings.settings().reset_token
    verification_token_secret = settings.settings().verification_token

    async def on_after_register(
        self, user: User, request: Optional[Request] = None
    ) -> None:
        text = f"""
        Dear {user.email},

        You have created or updated your Acronyms account. Please confirm this
        email by clicking the link below:

        https://notareallink.com/verify?user=fjdskj
        """
        email.sender().send(
            subject="Welcome to Acronyms",
            sender=settings.settings().smtp_username,
            receivers=[user.email],
            text=text,
        )


def get_database_strategy(
    access_token_db: AccessTokenDatabase[AccessToken] = Depends(
        models.get_tokens
    ),
) -> DatabaseStrategy:
    """Load authentication strategy."""
    return DatabaseStrategy(access_token_db, lifetime_seconds=3600)


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(models.get_users),
) -> AsyncIterator[UserManager]:
    """Load user manager."""
    yield UserManager(user_db)


def include_routes(app: FastAPI) -> None:
    """Add authentication routes to application."""
    app.include_router(
        users.get_auth_router(backend),
        prefix="/auth",
    )
    app.include_router(
        users.get_register_router(UserRead, UserCreate),
        prefix="/auth",
    )
    app.include_router(
        users.get_reset_password_router(),
        prefix="/auth",
    )
    app.include_router(
        users.get_verify_router(UserRead),
        prefix="/auth",
    )
    app.include_router(
        users.get_users_router(UserRead, UserUpdate),
        prefix="/users",
    )


transport = BearerTransport(tokenUrl="auth/login")
backend = AuthenticationBackend(
    name="database",
    transport=transport,
    get_strategy=get_database_strategy,
)
users = FastAPIUsers[User, UUID](get_user_manager, [backend])
current_user = users.current_user(active=True)
