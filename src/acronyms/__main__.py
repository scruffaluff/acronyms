"""Command line interface for acronyms."""


import sys

from pydantic.error_wrappers import ValidationError
import uvicorn

from acronyms import settings


def main() -> None:
    """Pass command line arguments to uvicorn."""
    if "-h" in sys.argv[1:] or "--help" in sys.argv[1:]:
        uvicorn.main(["acronyms.main:app", *sys.argv[1:]])
    else:
        try:
            settings.settings()
        except ValidationError as exception:
            print("Acronyms settings failed validation", file=sys.stderr)
            print(exception, file=sys.stderr)
            sys.exit(2)

        uvicorn.main(["acronyms.main:app", *sys.argv[1:]])


if __name__ == "__main__":
    main()
