"""
config.py
-----
Fichier de configuration des différents services utilisé par le projet.
Auteur : Dylan Manseri
"""
import os
from dotenv import load_dotenv
from logger import setup_logging

# ============================================================
# CONFIGURATION BASE DE DONNEES
# ============================================================

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# ============================================================
# CONFIGURATION API
# ============================================================

API_KEY = os.getenv("HENRIK_API_KEY")