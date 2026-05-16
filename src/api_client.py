"""
api_client.py
-----
Fonctions de récupérations du flux des 5 derniers matchs via l'API Henrik.
Auteur : Dylan Manseri
"""
import sys
import requests
from config import API_KEY
import logging

BASE_URL = "https://api.henrikdev.xyz/valorant"

HEADERS = {
    "Authorization": API_KEY,
    "accept": "application/json",
}

def request_player(name, tag):
    """
    Récupère le flux de donnée d'un joueur Valorant.
    :param name: Le pseudo in-game du joueur.
    :param tag: Le tag du joueur.
    :return: Le flux de données.
    """
    logging.info("=" * 50)
    logging.info("   NOUVELLE CONNEXION VERS HENRIK API")
    logging.info("=" * 50)
    url = f"{BASE_URL}/v1/account/{name}/{tag}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        logging.info("Connexion etablit [OK]")
        return response
    else:
        logging.fatal("Connexion API echouee [ERR]")
        sys.exit()


def get_puuid(name, tag):
    """
    Récupère l'identifiant du joueur via une requête API.
    :param name: Le pseudo in-game du joueur.
    :param tag: Le tag du joueur.
    :return: L'identifiant du joueur.
    """
    response_json = request_player(name, tag).json()
    return response_json["data"]["puuid"]

def fetch_matches(puuid):
    """
    Récupère les données des cinq derniers matchs d'un joueur.
    :param puuid: Identifiant unique du joueur.
    :return: La donnée au format json.
    """
    url = f"{BASE_URL}/v3/by-puuid/matches/eu/{puuid}"
    response = requests.get(url, headers=HEADERS)
    return response.json()
