"""
__init.py__
-----
Programme principal du projet.
Auteur : Dylan Manseri
"""
from api_client import *
from insert_db import insert_data
from logger import setup_logging

setup_logging()

id = get_puuid('little elephant', '270')
matchs_json = fetch_matches(id)

insert_data(matchs_json)