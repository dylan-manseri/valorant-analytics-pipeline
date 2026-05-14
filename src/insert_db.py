"""
insert_db.py
-----
Fonctions d'insertions dans la base de données.
Auteur : Dylan Manseri
"""
import logging
import psycopg2
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
from datetime import datetime

def get_connection():
    """
    Initie la connexion vers la base de données.
    :return: La variable permettant à utiliser la base de données où l'on s'est connecté.
    """
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )

def insert_map(cursor, party_info):
    """
    Insère la carte si elle n'est pas déjà présente.
    :param cursor: Curseur pour écrire dans la base de donnée.
    :param party_info: Le tableau Json des données de la partie.
    :return: L'ID de la map inséré ou rien si elle était déjà inséré
    """
    name = party_info["metadata"]["map"]

    cursor.execute("""
        INSERT INTO Carte (name, version)
        VALUES (%s, %s)
        ON CONFLICT (name) DO NOTHING
        RETURNING map_id
    """, name)                              # RETURNING renvoi l'ID de ligne inséré

    result = cursor.fetchone()              # On récupère la donnée de l'ID
    if result:
        logging.info(f"Carte insérée ✅ : {name}")
        map_id = result[0]
    else:
        logging.info(f"Carte déjà existante ⚠️ : {name}")
        cursor.execute("SELECT map_id FROM Carte WHERE name = %s", name)
        map_id = cursor.fetchone()[0]
    return map_id

def insert_party(cursor, party_info, map_id):
    """
    Insert une partie dans la table Partie si elle n'est pas déjà présente.
    :param cursor: Curseur pour écrire dans la base de donnée.
    :param party_info: Le tableau Json des données de la partie
    :param map_id: ID de la map de la carte, nécessaire, car c'est une fKey
    :return: L'ID du match ou None si le match est déjà dans la BD
    """
    party_id = party_info["metadata"]["match_id"]
    timestamp = party_info["metadata"]["game_start"]
    match_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    mode = party_info["metadata"]["mode"]
    server = party_info["metadata"]["cluster"]
    release = party_info["metadata"]["game_version"]
    patch = release.split("-")[1]

    cursor.execute("""
        INSERT INTO Partie (party_id, map_id, match_date, mode, server, patch)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (match_id) DO NOTHING
        """, (party_id, map_id, match_date, mode, server, patch))

    if cursor.rowcount == 1:
        logging.info(f"Match insérée ✅ : {party_id}")
    else:
        logging.warning(f"Match déjà existant ❌ : {party_id}")
        party_id = None
    return party_id

def get_first_attack(party_info):
    """
    Cherche la couleur de l'équipe qui a attaqué en première.
    Parcours les rounds et renvoie la première équipe à avoir planté le spike.
    :param party_info: Flux Json des données de la partie.
    :return: La couleur de l'équipe qui a attaqué en première.
    """
    i = 0
    while party_info["rounds"][i]["planted_by"] is "null":
        i+=1
    return party_info["rounds"][i]["planted_by"]["team"].lower()

def insert_team(cursor, party_info, party_id):
    """
    Insère les deux équipes dans la table Équipe avec leurs informations.
    :param cursor: Curseur pour écrire dans la base de donnée.
    :param party_info: Flux Json des données de la partie.
    :param party_id: ID de la partie, à insérer, car fKey.
    :return: Tableau de l'id des deux équipes.
    """
    first_attack = get_first_attack(party_info)
    id_team = {}
    team = {"blue", "red"}
    for color in team:
        has_won = party_info["teams"][color]["has_won"]
        rounds_won = party_info["teams"][color]["rounds_won"]
        rounds_loss = party_info["teams"][color]["rounds_loss"]
        if first_attack == color:
            first_side = "attack"
        else:
            first_side = "defense"
        cursor.execute("""
            INSERT INTO Equipe (party_id, color, has_won, rounds_won, rounds_loss, first_side)
                VALUES (%s, %s, %s, %s)
                RETURNING team_id
            """, (party_id, color, has_won, rounds_won, rounds_loss, first_side))
        result = cursor.fetchone()
        id_team[color] = result[0]
    return id_team

def insert_data(matches_json):
    """
    Fonction centralisant les insertions dans la base de données.
    :param matches_json: Flux de données des 5 derniers matches.
    :return:
    """
    connection = get_connection()
    cursor = connection.cursor()
    id_table = {}
    for i in range(5):
        party_info = matches_json["data"][i]
        id_table["map"] = insert_map(cursor, party_info)
        id_table["party"] = insert_party(cursor, party_info, id_table["map"])
        if id_table["party"] is not None:
            id_table["equipe"] = insert_team(cursor, party_info, id_table["party"])