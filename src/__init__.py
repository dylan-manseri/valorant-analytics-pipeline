"""
__init.py__
-----
Programme principal du projet.
Auteur : Dylan Manseri
"""
from api_client import *
from insert_db import insert_data



id = get_puuid('little elephant', '270')
matches_json = fetch_matches(id)

insert_data(matches_json)