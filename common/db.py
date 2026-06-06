import psycopg2
from common.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT
from typing import Dict, Any, Tuple, Optional

def get_connection() -> Any:
    """Retourne une connexion psycopg2 configurée depuis les variables d'env."""
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        sslmode="require"
    )