"""
logger.py
-----
Configuration du système de logs (formatage coloré, filtres console/fichier).
Auteur : Dylan Manseri
"""
import logging

_LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"


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


def setup_logging(log_path: str = "../logs/pipeline.log") -> None:
    """
    Configure le logger racine avec deux handlers :
    - Fichier : tout, sans couleurs.
    - Console  : insertions clés + erreurs, avec couleurs.
    :param log_path: Chemin vers le fichier de log.
    """
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(_LOG_FORMAT))

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(_ColoredFormatter(_LOG_FORMAT))
    console_handler.addFilter(_ConsoleFilter())

    logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, console_handler])