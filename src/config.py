"""
config.py
-----
Fichier de configuration des différents services utilisé par le projet.
Auteur : Dylan Manseri
"""
import logging
import os
from dotenv import load_dotenv

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

# ============================================================
# CONFIGURATION DES LOGS
# ============================================================

# On paramètre les logs fichier
file_handler = logging.FileHandler("../logs/pipeline.log")
file_handler.setLevel(logging.DEBUG)

# On paramètre les logs console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)

# On configure les logs
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[file_handler, console_handler]
)