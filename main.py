import requests
import json
import os
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

API_KEY = os.getenv("HENRIK_API_KEY")
BASE_URL = "https://api.henrikdev.xyz/valorant"

HEADER = {
    "Authorization": API_KEY,
    "accept": "application/json",
}

def get_puuid(name, tag):
    """
    Récupère le PUUID d'un joueur Valorant
    :param name: Le pseudo in-game du joueur.
    :param tag: Le tag du joueur.
    :return: L'identifiant du joueur.
    """

    url = f"{BASE_URL}/v1/account/{name}/{tag}"
    response = requests.get(url, headers=HEADER)
    data = response.json()
    return data["data"]["puuid"]

def fetch_data(puuid):
    """
    Récupère les données des cinq derniers matches d'un joueur.
    :param puuid: Identifiant du joueur.
    :return: La donnée au format json
    """

    url = f"{BASE_URL}/v3/by-puuid/matches/eu/{puuid}"
    response = requests.get(url, headers=HEADER)
    data = response.json()
    return data

if __name__ == "__main__":
    name = "little elephant"
    tag = "270"
    puuid = get_puuid(quote(name), tag)         # quote encode le texte au format URL
    matches_info = fetch_data(puuid)

    with open("matches.json", "w") as f:        # Écrit le json resultant dans un fichier
        json.dump(matches_info, f, indent=2)