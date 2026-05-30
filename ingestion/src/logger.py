"""
logger.py
-----
Configuration du système de logs (formatage coloré, filtres console/fichier).
Auteur : Dylan Manseri
"""
import logging
import sys
import os
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

_LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
_DEFAULT_LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "pipeline.log"


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
    _KEYWORDS = ("connexion etablie", "connexion fermee", "carte detectee", "match detecte", "agent detectee", "arme detectee")

    def filter(self, record: logging.LogRecord) -> bool:
        if record.levelno >= logging.ERROR:
            return True
        return any(kw in record.getMessage() for kw in self._KEYWORDS)


def setup_logging(log_path: Path = _DEFAULT_LOG_PATH) -> None:
    """
    Configure le logger racine avec deux handlers :
    - Fichier : tout, sans couleurs.
    - Console  : insertions clés + erreurs, avec couleurs.
    :param log_path: Chemin vers le fichier de log.
    """
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    file_handler.stream.reconfigure(line_buffering=True)

    sys.stdout.reconfigure(line_buffering=True)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(_ColoredFormatter(_LOG_FORMAT))
    console_handler.addFilter(_ConsoleFilter())

    logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, console_handler])