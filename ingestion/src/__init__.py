"""
__init.py__
-----
Programme principal du projet.
Auteur : Dylan Manseri
"""
import json

from api_client import *
from insert_db import insert_data
from logger import setup_logging

setup_logging()

id = get_puuid('little elephant', '270')
matchs_json = fetch_matches(id)

with open("../data/matches.json", "w", encoding="utf-8") as f:
    json.dump(matchs_json, f, indent=2, ensure_ascii=False)


insert_data(matchs_json)