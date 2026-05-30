"""
__init.py__
-----
Programme principal du projet.
Auteur : Dylan Manseri
"""
import json
from pathlib import Path

from api_client import *
from insert_db import insert_data
from logger import setup_logging
from config import RIOT_USERNAME, RIOT_TAG

setup_logging()

id = get_puuid(RIOT_USERNAME, RIOT_TAG)
matchs_json = fetch_matches(id)

_MATCHES_PATH = Path(__file__).resolve().parent.parent / "data" / "matches.json"

with open(_MATCHES_PATH, "w", encoding="utf-8") as f:
    json.dump(matchs_json, f, indent=2, ensure_ascii=False)

insert_data(matchs_json)