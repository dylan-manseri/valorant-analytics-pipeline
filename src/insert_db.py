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
    """Retourne une connexion psycopg2 configurée depuis les variables d'env."""
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )

def insert_map(cursor, party_info):
    """
    Insère la carte si elle n'est pas déjà présente.
    :param party_info: Données JSON de la partie.
    :return: map_id de la carte (existante ou nouvellement inseree).
    """
    name = party_info["metadata"]["map"]

    cursor.execute("""
        INSERT INTO Carte (name)
        VALUES (%s)
        ON CONFLICT (name) DO NOTHING
        RETURNING map_id
    """, (name,))

    result = cursor.fetchone()
    if result:
        logging.info(f"Carte inseree [OK] : {name}")
        map_id = result[0]
    else:
        # ON CONFLICT DO NOTHING ne retourne rien, SELECT nécessaire
        logging.info(f"Carte deja existante [WARN] : {name}")
        cursor.execute("SELECT map_id FROM Carte WHERE name = %s", (name,))
        map_id = cursor.fetchone()[0]
    return map_id

def insert_party(cursor, party_info, map_id):
    """
    Insère une partie si elle n'est pas déjà présente.
    :param party_info: Données JSON de la partie.
    :param map_id: FK vers la carte jouée.
    :return: ID de la partie si insertion réussie, None si la partie existait déjà.
    """
    party_id = party_info["metadata"]["matchid"]
    timestamp = party_info["metadata"]["game_start"]
    match_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    mode = party_info["metadata"]["mode"]
    server = party_info["metadata"]["cluster"]
    release = party_info["metadata"]["game_version"]
    patch = release.split("-")[1]

    cursor.execute("""
        INSERT INTO Partie (party_id, map_id, match_date, mode, server, patch)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (party_id) DO NOTHING
        """, (party_id, map_id, match_date, mode, server, patch))

    if cursor.rowcount == 1:
        logging.info(f"Match inseree [OK] : {party_id}")
    else:
        logging.warning(f"Match deja existant [ERR] : {party_id}")
        party_id = None
    return party_id

def get_first_attack(party_info):
    """
    Retourne la couleur ('red'/'blue') de l'équipe qui a attaqué en premier.
    Cherche le premier round avec un plant de spike pour déduire le côté attaquant initial.
    :param party_info: Données JSON de la partie.
    :return: 'red' ou 'blue'.
    """
    i = 0
    while i < len(party_info["rounds"]) and party_info["rounds"][i]["plant_events"]["planted_by"] is None:
        i+=1
    if i == len(party_info["rounds"]):
        return None
    return party_info["rounds"][i]["plant_events"]["planted_by"]["team"].lower()

def insert_team(cursor, party_info, party_id):
    """
    Insère les deux équipes (red/blue) pour une partie donnée.
    :param party_info: Données JSON de la partie.
    :param party_id: FK vers la partie.
    :return: Dict {'red': team_id, 'blue': team_id}.
    """
    first_attack = get_first_attack(party_info)
    id_team = {}
    team = {"blue", "red"}
    for color in team:
        has_won = party_info["teams"][color]["has_won"]
        round_won = party_info["teams"][color]["rounds_won"]
        round_lost = party_info["teams"][color]["rounds_lost"]
        if first_attack == color:
            first_side = "attack"
        else:
            first_side = "defense"
        cursor.execute("""
            INSERT INTO Equipe (party_id, color, has_won, round_won, round_lost, first_side)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING team_id
            """, (party_id, color, has_won, round_won, round_lost, first_side))
        result = cursor.fetchone()
        id_team[color] = result[0]
    return id_team

def insertPlayer(cursor, player):
    """
    Insère un joueur ou met à jour son pseudo/rank s'il existe déjà (ON CONFLICT UPDATE).
    :param player: Données JSON du joueur dans la partie.
    :return: puuid du joueur.
    """
    puuid = player["puuid"]
    username = player["name"]
    tag = player["tag"]
    account_level = player["level"]
    rank = player["currenttier_patched"]
    card = player["assets"]["card"]["large"]
    cursor.execute("""
        INSERT INTO Joueur (puuid, username, tag, account_level, rank, card)
                   VALUES (%s, %s, %s, %s, %s, %s)
                   ON CONFLICT (puuid) DO UPDATE SET
                   username = EXCLUDED.username,
                   account_level = EXCLUDED.account_level,
                   rank = EXCLUDED.rank
        """, (puuid, username, tag, account_level, rank, card))
    if cursor.rowcount == 1:
        logging.info(f"Joueur inseree [OK] : {puuid}")
    else:
        logging.warning(f"Erreur d'insertion joueur [ERR] : {puuid}")
    return puuid

def insertAgent(cursor, player):
    """
    Insère un agent s'il n'existe pas déjà.
    :param player: Données JSON du joueur (contient le nom et l'asset de l'agent).
    :return: ID de l'agent (existant ou nouvellement inséré).
    """
    name = player["character"]
    asset_agent = player["assets"]["agent"]["full"]
    cursor.execute("""
        INSERT INTO Agent (name, asset_agent)
                VALUES (%s, %s)
                ON CONFLICT (name) DO NOTHING
                RETURNING agent_id
        """, (name, asset_agent))
    result = cursor.fetchone()
    if result:
        logging.info(f"Agent inseree [OK] : {name}")
        agent_id = result[0]
    else:
        logging.info(f"Agent deja existant [WARN] : {name}")
        cursor.execute("SELECT agent_id FROM Agent WHERE name = %s", (name,))
        agent_id = cursor.fetchone()[0]
    return agent_id

def insert_compose(cursor, party_info, teams_id):
    """
    Insère les lignes de la table ternaire Compose (Joueur + Équipe + Agent + stats).
    :param party_info: Données JSON de la partie.
    :param teams_id: Dict {'red': team_id, 'blue': team_id}.
    """
    players = party_info["players"]["all_players"]
    for player in players:
        team = player["team"].lower()
        team_id = teams_id[team]
        puuid = insertPlayer(cursor, player)
        agent_id = insertAgent(cursor, player)

        kills = player["stats"]["kills"]
        deaths = player["stats"]["deaths"]
        assists = player["stats"]["assists"]
        cursor.execute("""
            INSERT INTO Compose (puuid, team_id, agent_id, kills, deaths, assists)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (puuid, team_id, agent_id, kills, deaths, assists))
        if cursor.rowcount == 1:
            logging.info(f"Compose inseree [OK] : {puuid, team_id, agent_id}")
        else:
            logging.warning(f"Erreur d'insertion compose [ERR] : {puuid, team_id, agent_id}")

def insert_data(matchs_json):
    """
    Point d'entrée principal : insère les 5 derniers matchs en base.
    Gère la connexion, le commit et le rollback en cas d'erreur.
    :param matchs_json: Données JSON retournées par l'API (liste de 5 matchs).
    """
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        for party_info in matchs_json["data"]:
            if party_info["metadata"]["mode_id"] == "competitive" :
                map_id = insert_map(cursor, party_info)
                party_id = insert_party(cursor, party_info, map_id)
                if party_id is not None:
                    teams_id = insert_team(cursor, party_info, party_id)
                    insert_compose(cursor, party_info, teams_id)
    except Exception as e:
        logging.error(f"Erreur : {e}")
        connection.rollback()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.commit()
            connection.close()