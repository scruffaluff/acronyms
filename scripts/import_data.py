"""Import acronyms data to backend for easier manual frontend interaction."""


from argparse import ArgumentParser
import json
from pathlib import Path
import secrets

from requests import Session


parser = ArgumentParser()
parser.add_argument("endpoint", help="Location of Acronyms server.")
arguments = parser.parse_args()

data_path = Path(__file__).parents[1] / "tests/data/acronyms.json"
acronyms = json.loads(data_path.read_text())

users = [
    {"email": "oodriebum@mail.com", "password": secrets.token_urlsafe(16)},
    {"email": "scruffaluff@mail.com", "password": secrets.token_urlsafe(16)},
]

with Session() as session:
    for acronym in acronyms:
        response = session.post(
            f"{arguments.endpoint}/api/acronym", json=acronym
        )
        response.raise_for_status()

    for user in users:
        register_response = session.post(
            f"{arguments.endpoint}/auth/register", json=user
        )
        register_response.raise_for_status()
        login_response = session.post(
            f"{arguments.endpoint}/auth/login",
            data={"username": user["email"], "password": user["password"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        login_response.raise_for_status()
