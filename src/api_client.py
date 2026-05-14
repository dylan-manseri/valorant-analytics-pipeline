"""
api_client.py
-----
Fonctions de récupérations du flux des 5 derniers matchs via l'API Henrik.
Auteur : Dylan Manseri
"""
import requests
from config import API_KEY

BASE_URL = "https://api.henrikdev.xyz/valorant"
HEADERS = {
    "Authorization": API_KEY,
    "accept": "application/json",
}

def get_puuid(name, tag):
    """
    Récupère le PUUID d'un joueur Valorant.
    :param name: Le pseudo in-game du joueur.
    :param tag: Le tag du joueur.
    :return: L'identifiant unique du joueur.
    """
    url = f"{BASE_URL}/v1/account/{name}/{tag}"
    response = requests.get(url, headers=HEADERS)
    return response.json()["data"]["puuid"]

def fetch_matches(puuid):
    """
    Récupère les données des cinq derniers matchs d'un joueur.
    :param puuid: Identifiant unique du joueur.
    :return: La donnée au format json.
    """
    url = f"{BASE_URL}/v3/by-puuid/matches/eu/{puuid}"
    response = requests.get(url, headers=HEADERS)
    return response.json()
