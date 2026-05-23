"""
insert_db.py
-----
Fonctions d'insertions dans la base de données.
Auteur : Dylan Manseri
"""
import logging
import traceback
from typing import Dict, Any, Tuple, Optional
import psycopg2
from psycopg2.extensions import cursor as PostgresCursor
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
from datetime import datetime

def get_connection() -> Any:
    """Retourne une connexion psycopg2 configurée depuis les variables d'env."""
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )

def insert_map(cursor: PostgresCursor,
               party_info: Dict[str, Any]
               ) -> int:
    """
    Insère la carte si absente, retourne son map_id dans tous les cas.
    :param party_info: Flux JSON d'une partie (API Henrik).
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

def insert_party(cursor: PostgresCursor,
                 party_info: Dict[str, Any],
                 map_id: int) -> Optional[str]:
    """
    Insère une partie si absente.
    :param party_info: Flux JSON d'une partie (API Henrik).
    :param map_id: FK vers la carte jouée.
    :return: party_id si insertion réussie, None si la partie existait déjà.
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

def get_first_attack(party_info: Dict[str, Any]) -> Optional[str]:
    """
    Déduit l'équipe attaquante initiale en cherchant le premier round avec un plant de spike.
    :return: 'red' ou 'blue', None si aucun plant dans toute la partie.
    """
    i = 0
    while i < len(party_info["rounds"]) and party_info["rounds"][i]["plant_events"]["planted_by"] is None:
        i+=1
    if i == len(party_info["rounds"]):
        return None
    return party_info["rounds"][i]["plant_events"]["planted_by"]["team"].lower()

def insert_team(cursor: PostgresCursor,
                party_info: Dict[str, Any],
                party_id: str) -> Dict[str, int]:
    """
    Insère les deux équipes (red/blue) pour une partie.
    :param party_info: Flux JSON d'une partie (API Henrik).
    :param party_id: FK vers la partie.
    :return: {'red': team_id, 'blue': team_id}
    """
    first_attack = get_first_attack(party_info)
    id_team: Dict[str, int] = {}
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

def insertPlayer(cursor: PostgresCursor,
                 player: Dict[str, Any]) -> str:
    """
    Insère un joueur ou met à jour username/rank/level s'il existe déjà.
    :param player: Données JSON d'un joueur dans la partie (API Henrik).
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

def insertAgent(cursor: PostgresCursor,
                player: Dict[str, Any]) -> int:
    """
    Insère un agent si absent, retourne son agent_id dans tous les cas.
    :param player: Données JSON d'un joueur dans la partie.
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

def insert_compose(cursor: PostgresCursor,
                   party_info: Dict[str, Any],
                   teams_id: Dict[str, int]) -> None:
    """
    Insère les lignes de la table ternaire Compose (Joueur + Équipe + Agent + stats).
    :param party_info: Flux JSON d'une partie.
    :param teams_id: {'red': team_id, 'blue': team_id}.
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

def insert_round(cursor: PostgresCursor,
                 round_info: Dict[str, Any],
                 num: int,
                 teams_id: Dict[str, int]) -> int:
    """
    Insère un round. Les champs plant_* sont nullable si aucun spike posé.
    :param round_info: Données JSON d'un round.
    :param num: Numéro du round (0-indexé).
    :param teams_id: {'red': team_id, 'blue': team_id}.
    :return: round_id généré.
    """
    number = num
    winning_team = round_info["winning_team"].lower()
    winning_team_id = teams_id[winning_team]
    end_type = round_info["end_type"].lower()
    bomb_planted = round_info["bomb_planted"]
    bomb_defused = round_info["bomb_defused"]
    if bomb_planted:
        plant_site = round_info["plant_events"]["plant_site"]
        plant_time_in_round = round_info["plant_events"]["plant_time_in_round"]
        plant_coord_x = round_info["plant_events"]["plant_location"]["x"]
        plant_coord_y = round_info["plant_events"]["plant_location"]["y"]
    else:
        plant_site = None
        plant_time_in_round = None
        plant_coord_x = None
        plant_coord_y = None

    cursor.execute("""
        INSERT INTO Round (number, end_type, bomb_planted, plant_site, bomb_defused,
                           plant_time_in_round, plant_coord_x, plant_coord_y, winning_team_id)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                   RETURNING round_id
                   """, (number, end_type, bomb_planted, plant_site, bomb_defused, plant_time_in_round, plant_coord_x, plant_coord_y, winning_team_id))
    result = cursor.fetchone()
    if result:
        logging.info(f"Round inseree [OK] : {result[0]}")
    else:
        logging.error(f"Erreur d'insertion round [ERR] : {result[0]}")
        raise Exception(f"Erreur d'insertion round [ERR] : {result[0]}")
    return result[0]

def insert_arme(cursor: PostgresCursor,
                player_stat: Dict[str, Any]) -> str:
    """
    Insère une arme si absente, retourne son weapon_id dans tous les cas.
    :param player_stat: Données JSON d'un joueur pour un round.
    """
    weapon_info = player_stat["economy"]["weapon"]
    if weapon_info["id"]:
        weapon_id = weapon_info["id"]
        weapon_name = weapon_info["name"]
        asset_weapon = weapon_info["assets"]["display_icon"]
    else:
        weapon_id = "00000000-0000-0000-0000-000000000001"
        weapon_name = None
        asset_weapon = None
    cursor.execute("""
        INSERT INTO Arme (weapon_id, weapon_name, asset_weapon)
            VALUES (%s, %s, %s)
            ON CONFLICT (weapon_id) DO NOTHING
                   """, (weapon_id, weapon_name, asset_weapon))
    if cursor.rowcount == 1:
        logging.info(f"Arme inseree [OK] : {weapon_name}")
    else:
        logging.info(f"Arme deja existante [INFO] : {weapon_name}")
    return weapon_id


def insert_armor(cursor: PostgresCursor,
                 player_stat: Dict[str, Any]) -> str | Any:
    """
    Insère une armure si absente, retourne son armor_id dans tous les cas.
    :param player_stat: Données JSON d'un joueur pour un round.
    """
    armor_info = player_stat["economy"]["armor"]
    armor_id = armor_info["id"] if armor_info["id"] else "00000000-0000-0000-0000-000000000000"
    armor_name = armor_info["name"]
    asset_armor = armor_info["assets"]["display_icon"]
    cursor.execute("""
                   INSERT INTO Armure (armor_id, armor_name, asset_armor)
                   VALUES (%s, %s, %s) ON CONFLICT (armor_id) DO NOTHING
                   """, (armor_id, armor_name, asset_armor))
    if cursor.rowcount == 1:
        logging.info(f"Armure inseree [OK] : {armor_name}")
    else:
        logging.info(f"Armure deja existante [INFO] : {armor_name}")
    return armor_id

def joue_attribut(player_stat: Dict[str, Any],
                  round_id: int,
                  weapon_id: str,
                  armor_id: str) -> Tuple:
    """
    Construit le tuple ordonné des attributs pour l'INSERT dans Joue.
    :param player_stat: Données JSON d'un joueur pour un round.
    """
    return (
        player_stat["player_puuid"],
        round_id,
        weapon_id,
        armor_id,
        player_stat["ability_casts"]["x_casts"],
        player_stat["ability_casts"]["e_casts"],
        player_stat["ability_casts"]["q_casts"],
        player_stat["ability_casts"]["c_casts"],
        player_stat["score"],
        player_stat["economy"]["loadout_value"],
        player_stat["economy"]["spent"],
        player_stat["economy"]["remaining"]
    )

def insert_joue(cursor: PostgresCursor,
                party_info: Dict[str, Any],
                teams_id: Dict[str, int]) -> None:
    """
    Insère les lignes de la table Joue pour chaque joueur de chaque round.
    :param party_info: Flux JSON d'une partie.
    :param teams_id: {'red': team_id, 'blue': team_id}.
    """
    rounds = party_info["rounds"]
    for num in range(0, len(rounds)):
        r = rounds[num]
        round_id = insert_round(cursor, r, num, teams_id)
        for player_stat in r["player_stats"]:                                       # Un round ← Plusieurs joueurs
            weapon_id = insert_arme(cursor, player_stat)
            armor_id = insert_armor(cursor, player_stat)
            attribut = joue_attribut(player_stat, round_id, weapon_id, armor_id)
            cursor.execute("""
                INSERT INTO Joue (puuid, round_id, weapon_id, armor_id, ability_cast_x, ability_cast_e,
                                  ability_cast_q, ability_cast_c, score, loadout_value, spent, remaining)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                           """, attribut)


def insert_data(matchs_json: Dict[str, Any]) -> None:
    """
    Point d'entrée principal : insère les derniers matchs en base.
    Filtre uniquement les parties compétitives. Rollback en cas d'erreur.
    :param matchs_json: Données du match issu du flux JSON.
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
                    insert_joue(cursor, party_info, teams_id)
    except Exception as e:
        logging.error(f"Erreur : {e}, trace : {traceback.format_exc()}")
        if connection:
            connection.rollback()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.commit()
            connection.close()