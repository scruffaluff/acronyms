"""Command line interface for acronyms."""


import sys

import uvicorn


def main() -> None:
    """Pass command line arguments to uvicorn."""
    uvicorn.main(["acronyms.site:app", *sys.argv[1:]])


if __name__ == "__main__":
    main()
