"""
config.py
-----
Fichier de configuration des différents services utilisé par le projet.
Auteur : Dylan Manseri
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# ============================================================
# CONFIGURATION BASE DE DONNEES
# ============================================================

_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_PATH)

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

# ============================================================
# CONFIGURATION API
# ============================================================

API_KEY = os.getenv("HENRIK_API_KEY")
RIOT_USERNAME = os.getenv("RIOT_USERNAME")
RIOT_TAG = os.getenv("RIOT_TAG")