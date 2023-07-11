"""Application email logic."""


import functools

from redmail import EmailSender

from acronyms import settings


@functools.lru_cache(maxsize=1)
def sender() -> EmailSender:
    """Load email configuration once."""
    settings_ = settings.settings()
    return EmailSender(
        host=settings_.smtp_host,
        password=settings_.smtp_password.get_secret_value(),
        port=settings_.smtp_port,
        use_starttls=settings_.smtp_tls,
        username=settings_.smtp_username,
    )
