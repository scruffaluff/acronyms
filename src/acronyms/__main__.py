"""Command line interface for acronyms."""


import sys

from pydantic import ValidationError
import uvicorn

import acronyms
from acronyms import settings


def main() -> None:
    """Pass command line arguments to uvicorn."""
    arguments = sys.argv[1:]
    if "--help" in arguments:
        uvicorn.main(["acronyms.main:app", *arguments])
    elif "--version" in arguments:
        print(f"Acronyms {acronyms.__version__}")
        sys.exit(0)

    try:
        settings_ = settings.settings()
    except ValidationError as exception:
        print("Acronyms settings failed validation", file=sys.stderr)
        print(exception, file=sys.stderr)
        sys.exit(2)

    if "--host" not in arguments:
        arguments += ["--host", str(settings_.host)]
    if "--log-level" not in arguments:
        arguments += ["--log-level", str(settings_.log_level)]
    if "--port" not in arguments:
        arguments += ["--port", str(settings_.port)]
    if "--ssl-certfile" not in arguments and settings_.ssl_certfile is not None:
        arguments += ["--ssl-certfile", str(settings_.ssl_certfile)]
    if "--ssl-keyfile" not in arguments and settings_.ssl_keyfile is not None:
        arguments += ["--ssl-keyfile", str(settings_.ssl_keyfile)]

    uvicorn.main(["acronyms.main:app", *arguments])


if __name__ == "__main__":
    main()
