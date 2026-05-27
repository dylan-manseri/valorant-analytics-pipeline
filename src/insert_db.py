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

# =========================
# CACHES APPLICATIFS
# =========================
_CACHE_MAPS: Optional[Dict[str, int]] = None
_CACHE_AGENTS: Optional[Dict[str, int]] = None
_CACHE_ARMES: Optional[Dict[str, str]] = None
_CACHE_ARMURE: Optional[Dict[str, str]] = None

def _init_caches(cursor : PostgresCursor) -> None:
    """
    Remplit les caches en mémoire pour réduire le nombre de requêtes du script.
    :param cursor: Curseur Postgres les requêtes de la base de données.
    :return: None
    """
    global _CACHE_MAPS, _CACHE_ARMES, _CACHE_ARMURE, _CACHE_AGENTS

    if _CACHE_MAPS is None:
        logging.info("Chargement du caches des cartes...")
        cursor.execute("SELECT map_name, map_id FROM Carte")
        # Passage de tuples a un dictionnaire, premier élement ← clé.
        _CACHE_MAPS = dict(cursor.fetchall())

    if _CACHE_ARMES is None:
        logging.info("Chargement du cache des armes...")
        cursor.execute("SELECT weapon_name, weapon_id FROM Arme")
        _CACHE_ARMES = dict(cursor.fetchall())

    if _CACHE_ARMURE is None:
        logging.info("Chargement du cache des armures...")
        cursor.execute("SELECT armor_name, armor_id FROM Armure")
        _CACHE_ARMURE = dict(cursor.fetchall())

    if _CACHE_AGENTS is None:
        logging.info("Chargement du cache des agents...")
        cursor.execute("SELECT agent_name, agent_id FROM Agent")
        _CACHE_AGENTS = dict(cursor.fetchall())

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
    map_name = party_info["metadata"]["map"]

    # Optimisation : pas de requête si la map est déjà dans le cache.
    if map_name in _CACHE_MAPS:
        return _CACHE_MAPS[map_name]

    # Au cas où le cache ne fonctionne pas correctement, ON CONFLICT évite les erreurs
    cursor.execute("""
        INSERT INTO Carte (map_name)
        VALUES (%s)
        ON CONFLICT (map_name) DO NOTHING
        RETURNING map_id
    """, (map_name,))

    result = cursor.fetchone()
    if result:
        logging.info(f"Carte inseree [OK] : {map_name}")
        _CACHE_MAPS[map_name] = result[0]
        return result[0]
    raise Exception(f"Cache désynchronisé : {map_name} absent du cache et déjà en base")

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
        logging.warning(f"Match deja existant [WARN] : {party_id}")
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

def insert_player(cursor: PostgresCursor,
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
        logging.info(f"Joueur mis à jour [OK] : {puuid}")
    return puuid

def insert_agent(cursor: PostgresCursor,
                player: Dict[str, Any]) -> int:
    """
    Insère un agent si absent, retourne son agent_id dans tous les cas.
    :param player: Données JSON d'un joueur dans la partie.
    """
    agent_name = player["character"]
    asset_agent = player["assets"]["agent"]["full"]

    if agent_name in _CACHE_AGENTS:
        return _CACHE_AGENTS[agent_name]

    cursor.execute("""
        INSERT INTO Agent (agent_name, asset_agent)
        VALUES (%s, %s)
        ON CONFLICT (agent_name) DO NOTHING
        RETURNING agent_id
    """, (agent_name, asset_agent))
    result = cursor.fetchone()
    if result:
        logging.info(f"Agent inseree [OK] : {agent_name}")
        agent_id = result[0]
        _CACHE_AGENTS[agent_name] = agent_id
        return agent_id
    raise Exception(f"Cache désynchronisé : {agent_name} absent du cache et déjà en base")

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
        puuid = insert_player(cursor, player)
        agent_id = insert_agent(cursor, player)

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
            raise Exception(f"Erreur d'insertion compose [ERR] : {puuid, team_id, agent_id}")

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
    """, (number, end_type, bomb_planted, plant_site, bomb_defused,
          plant_time_in_round, plant_coord_x, plant_coord_y, winning_team_id))
    result = cursor.fetchone()
    if result:
        logging.info(f"Round inseree [OK] : {result[0]}")
        return result[0]
    raise Exception(f"Erreur d'insertion round [ERR] : round {num}")

def insert_arme(cursor: PostgresCursor,
                weapon_info: Dict[str, Any]) -> str:
    """
    Insère une arme si absente, retourne son weapon_id dans tous les cas.
    :param weapon_info: Données JSON de l'arme.
    """
    if weapon_info["id"]:
        weapon_id = weapon_info["id"]
        weapon_name = weapon_info["name"]
        asset_weapon = weapon_info["asset"]
    else:
        weapon_id = "00000000-0000-0000-0000-000000000001"
        weapon_name = "unknown_weapon"
        asset_weapon = "unknown_weapon"

    if weapon_name in _CACHE_ARMES:
        return _CACHE_ARMES[weapon_name]
    cursor.execute("""
        INSERT INTO Arme (weapon_id, weapon_name, asset_weapon)
        VALUES (%s, %s, %s)
        ON CONFLICT (weapon_id) DO NOTHING
        RETURNING weapon_id
    """, (weapon_id, weapon_name, asset_weapon))
    result = cursor.fetchone()
    if result:
        logging.info(f"Arme inseree [OK] : {weapon_name}")
        _CACHE_ARMES[weapon_name] = result[0]
        return result[0]
    raise Exception(f"Cache désynchronisé : {weapon_id} absent du cache et déjà en base")


def insert_armor(cursor: PostgresCursor,
                 player_stat: Dict[str, Any]) -> str:
    """
    Insère une armure si absente, retourne son armor_id dans tous les cas.
    :param player_stat: Données JSON d'un joueur pour un round.
    """
    armor_info = player_stat["economy"]["armor"]
    armor_id = armor_info["id"] if armor_info["id"] else "00000000-0000-0000-0000-000000000000"
    armor_name = armor_info["name"] if armor_info["name"] else "unknown_armor"
    asset_armor = armor_info["assets"]["display_icon"] if armor_info["assets"] else "unknown_armor"

    if armor_name in _CACHE_ARMURE:
        return _CACHE_ARMURE[armor_name]

    cursor.execute("""
        INSERT INTO Armure (armor_id, armor_name, asset_armor)
        VALUES (%s, %s, %s)
        ON CONFLICT (armor_id) DO NOTHING
        RETURNING armor_id
    """, (armor_id, armor_name, asset_armor))
    result = cursor.fetchone()
    if result:
        logging.info(f"Armure inseree [OK] : {armor_name}")
        _CACHE_ARMURE[armor_name] = result[0]
        return result[0]
    raise Exception(f"Cache désynchronisé : {armor_id} absent du cache et déjà en base")

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


def insert_event(cursor: PostgresCursor,
                victim: str,
                author: str,
                round_id) -> int:
    """
    Insère un événement joueur (kill ou dégât), retourne son id_event_player.
    :param victim: puuid de la victime.
    :param author: puuid de l'auteur.
    :param round_id: FK vers le round.
    :return: id_event_player généré.
    """
    cursor.execute("""
        INSERT INTO Evenement_joueur (victim, author, round_id)
        VALUES (%s, %s, %s)
        RETURNING id_event_player
    """, (victim, author, round_id))
    result = cursor.fetchone()
    if result:
        logging.info(f"Insert Evenement_Joueur [OK] : {result[0]}")
        return result[0]
    raise Exception(f"Insert Evenement_Joueur [ERR]")


def insert_damage(cursor: PostgresCursor,
                  author: str,
                  damages: Dict[int, str],
                  round_id: int) -> None:
    """
    Insère les événements de dégâts d'un joueur pour un round.
    :param author: puuid de l'auteur des dégâts.
    :param damages: Liste des dégâts infligés.
    :param round_id: FK vers le round.
    """
    for damage in damages:
        victim = damage["receiver_puuid"]
        bodyshots = damage["bodyshots"]
        legshots = damage["legshots"]
        headshots = damage["headshots"]
        damage_count = damage["damage"]
        event_id = insert_event(cursor, victim, author, round_id)

        cursor.execute("""
            INSERT INTO Degat (damage_id, damage_count, headshots, bodyshots, legshots)
            VALUES (%s, %s, %s, %s, %s)
        """, (event_id, damage_count, headshots, bodyshots, legshots))
        if cursor.rowcount == 1:
            logging.info(f"Degat insert [OK] : {event_id}")
        else:
            raise Exception(f"Degat insert [ERR] : {event_id}")


def insert_localisation(cursor: PostgresCursor,
                        kill_id: int,
                        kill: Dict[str, Any],) -> None:
    """
    Insère les positions de tous les joueurs au moment d'un kill.
    :param kill_id: FK vers l'élimination.
    :param kill: Données JSON du kill.
    """
    for player_loc in kill["player_locations_on_kill"]:
        puuid = player_loc["player_puuid"]
        x = player_loc["location"]["x"]
        y = player_loc["location"]["y"]
        view_radiants = player_loc["view_radians"]

        cursor.execute("""
            INSERT INTO Localisation_joueur (player_id, kill_id, x, y, view_radiant)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING location_id
        """, (puuid, kill_id, x, y, view_radiants))
        result = cursor.fetchone()

        if result:
            logging.info(f"Localisation insert [OK] : {puuid}")
        else:
            raise Exception(f"Localisation insert [ERR] : {puuid}")

def insert_kill(cursor: PostgresCursor,
                  author: str,
                  kills: Dict[str, Any],
                  round_id: int) -> None:
    """
    Insère les éliminations d'un joueur pour un round.
    :param author: puuid de l'auteur des kills.
    :param kills: Liste des éliminations.
    :param round_id: FK vers le round.
    """
    for kill in kills:
        victim = kill["victim_puuid"]
        id_event = insert_event(cursor, victim, author, round_id)
        kill_time_in_rounds = kill["kill_time_in_round"]
        kill_time_in_match = kill["kill_time_in_match"]
        weapon_info = {"id":kill["damage_weapon_id"], "name":kill["damage_weapon_name"], "asset":kill["damage_weapon_assets"]["display_icon"]}
        damage_weapon_id = insert_arme(cursor, weapon_info)
        cursor.execute("""
            INSERT INTO Elimination (kill_id, kill_time_in_round, kill_time_in_match, damage_weapon)
            VALUES (%s, %s, %s, %s)
            RETURNING kill_id
        """, (id_event, kill_time_in_rounds, kill_time_in_match, damage_weapon_id))
        result = cursor.fetchone()
        if result:
            logging.info(f"Elimination [OK] : {result[0]}")
            insert_localisation(cursor, result[0], kill)
        else:
            raise Exception(f"Erreur d'insertion Elimination [ERR]")

def insert_joue_event(cursor: PostgresCursor,
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
            weapon_info_brut = player_stat["economy"]["weapon"]
            weapon_info = {"id": weapon_info_brut["id"], "name": weapon_info_brut["name"], "asset": weapon_info_brut["assets"]["display_icon"]}
            weapon_id = insert_arme(cursor, weapon_info)
            armor_id = insert_armor(cursor, player_stat)
            attribut = joue_attribut(player_stat, round_id, weapon_id, armor_id)
            cursor.execute("""
                INSERT INTO Joue (puuid, round_id, weapon_id, armor_id,
                                  ability_cast_x, ability_cast_e, ability_cast_q, ability_cast_c,
                                  score, loadout_value, spent, remaining)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, attribut)
            if cursor.rowcount == 1:
                logging.info(f"Joue inseree [OK] : {player_stat["player_puuid"], round_id, weapon_id, armor_id}")

                author = player_stat["player_puuid"]
                damages = player_stat["damage_events"]
                kills = player_stat["kill_events"]
                if len(damages) != 0 : insert_damage(cursor, author, damages, round_id)
                if len(kills)!= 0 : insert_kill(cursor, author, kills, round_id)
            else:
                raise Exception(f"Erreur d'insertion Joue : {player_stat["player_puuid"], round_id, weapon_id, armor_id}")



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
        _init_caches(cursor)
        for party_info in matchs_json["data"]:
            if party_info["metadata"]["mode_id"] == "competitive" :
                map_id = insert_map(cursor, party_info)
                party_id = insert_party(cursor, party_info, map_id)
                if party_id is not None:
                    teams_id = insert_team(cursor, party_info, party_id)
                    insert_compose(cursor, party_info, teams_id)
                    insert_joue_event(cursor, party_info, teams_id)
        connection.commit()
    except Exception as e:
        logging.error(f"Erreur : {e}, trace : {traceback.format_exc()}")
        if connection:
            connection.rollback()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()