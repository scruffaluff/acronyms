"""Import acronyms to backend for easier manual frontend interaction."""


from argparse import ArgumentParser
import json
from pathlib import Path

from requests import Session


parser = ArgumentParser()
parser.add_argument("endpoint", help="Location of Acronyms server.")
arguments = parser.parse_args()

data_path = Path(__file__).parents[1] / "tests/data/acronyms.json"
acronyms = json.loads(data_path.read_text())

with Session() as session:
    for acronym in acronyms:
        response = session.post(
            f"{arguments.endpoint}/api/acronym", json=acronym
        )
        response.raise_for_status()
