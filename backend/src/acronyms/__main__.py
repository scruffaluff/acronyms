import sys
import uvicorn


def main():
    uvicorn.main(["acronyms.site:app", *sys.argv[1:]])


if __name__ == "__main__":
    main()
