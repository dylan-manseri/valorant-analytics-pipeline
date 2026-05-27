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

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"


class _ColoredFormatter(logging.Formatter):
    _COLORS = {
        logging.INFO:    "\033[32m",  # vert  — insertion réussie
        logging.WARNING: "\033[33m",  # jaune — doublon attendu
        logging.ERROR:   "\033[31m",  # rouge — erreur
    }
    _RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self._COLORS.get(record.levelno, "")
        record.msg = f"{color}{record.msg}{self._RESET}"
        return super().format(record)


class _ConsoleFilter(logging.Filter):
    """Laisse passer uniquement les insertions clés et les erreurs."""
    _KEYWORDS = ("Carte inseree", "Agent inseree", "Arme inseree", "Match inseree")

    def filter(self, record: logging.LogRecord) -> bool:
        if record.levelno >= logging.ERROR:
            return True
        return any(kw in record.getMessage() for kw in self._KEYWORDS)


# Fichier : tout, sans couleurs
file_handler = logging.FileHandler("../logs/pipeline.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Console : insertions clés + erreurs, avec couleurs
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(_ColoredFormatter(LOG_FORMAT))
console_handler.addFilter(_ConsoleFilter())

logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, console_handler])