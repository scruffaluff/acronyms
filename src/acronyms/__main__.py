"""Command line interface for acronyms."""


import sys

from pydantic.error_wrappers import ValidationError
import uvicorn

from acronyms import settings


def main() -> None:
    """Pass command line arguments to uvicorn."""
    try:
        settings.settings()
    except ValidationError as exception:
        print(exception, file=sys.stderr)
        sys.exit(2)
    uvicorn.main(["acronyms.main:app", *sys.argv[1:]])


if __name__ == "__main__":
    main()
