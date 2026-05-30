CREATE TABLE carte
(
    map_id SERIAL PRIMARY KEY,
    map_name VARCHAR(20) UNIQUE NOT NULL
);

CREATE TABLE partie
(
    party_id CHAR(36) PRIMARY KEY,
    map_id INT REFERENCES carte(map_id),
    match_date DATE NOT NULL,
    mode VARCHAR(20) NOT NULL,
    server VARCHAR(9) NOT NULL,
    patch FLOAT NOT NULL
);

CREATE TABLE equipe
(
    team_id SERIAL PRIMARY KEY,
    party_id CHAR(36) REFERENCES partie(party_id),
    color VARCHAR(4) NOT NULL CHECK ( color in ('red', 'blue') ),
    has_won BOOLEAN NOT NULL,
    round_won INT NOT NULL,
    round_lost INT NOT NULL,
    first_side VARCHAR(7) CHECK ( first_side IN ('attack', 'defense'))
);

CREATE TABLE agent
(
    agent_id SERIAL PRIMARY KEY,
    agent_name VARCHAR(20) UNIQUE NOT NULL,
    asset_agent VARCHAR(255)
);

CREATE TABLE joueur
(
    puuid CHAR(36) PRIMARY KEY,
    username VARCHAR(16) NOT NULL,
    tag VARCHAR(5) NOT NULL,
    account_level INT NOT NULL,
    rank VARCHAR(10) NOT NULL,
    card VARCHAR(255) NOT NULL
);

CREATE TABLE compose
(
    puuid CHAR(36) REFERENCES joueur(puuid),
    team_id INT REFERENCES equipe(team_id),
    agent_id INT REFERENCES agent(agent_id),
    kills INT NOT NULL,
    deaths INT NOT NULL,
    assists INT NOT NULL,
    PRIMARY KEY (puuid, team_id, agent_id)
);

CREATE TABLE armure
(
    armor_id CHAR(36) PRIMARY KEY,
    armor_name VARCHAR(20) UNIQUE NOT NULL,
    asset_armor VARCHAR(255)
);

CREATE TABLE arme
(
    weapon_id CHAR(36) PRIMARY KEY,
    weapon_name VARCHAR(20) UNIQUE NOT NULL,
    asset_weapon VARCHAR(255)
);

CREATE TABLE round
(
    round_id SERIAL PRIMARY KEY,
    number INT NOT NULL,
    winning_team_id INT REFERENCES equipe(team_id),
    end_type VARCHAR(20) NOT NULL,
    bomb_planted BOOLEAN NOT NULL,
    bomb_defused BOOLEAN NOT NULL,
    plant_site CHAR(1),
    plant_time_in_round INT,
    plant_coord_x FLOAT,
    plant_coord_y FLOAT
);

CREATE TABLE joue
(
    puuid CHAR(36) REFERENCES joueur(puuid),
    armor_id CHAR(36) REFERENCES armure(armor_id),
    weapon_id CHAR(36) REFERENCES arme(weapon_id),
    round_id INT REFERENCES round(round_id),
    ability_cast_x INT,
    ability_cast_e INT,
    ability_cast_q INT,
    ability_cast_c INT,
    score INT NOT NULL,
    loadout_value INT NOT NULL,
    spent INT NOT NULL,
    remaining INT NOT NULL,
    PRIMARY KEY(puuid, armor_id, weapon_id, round_id)
);

CREATE TABLE evenement_joueur
(
    id_event_player SERIAL PRIMARY KEY,
    round_id INT REFERENCES round(round_id),
    victim CHAR(36) REFERENCES joueur(puuid),
    author CHAR(36) REFERENCES joueur(puuid)
);

CREATE TABLE elimination
(
    kill_id INT REFERENCES evenement_joueur(id_event_player),
    damage_weapon CHAR(36) REFERENCES arme(weapon_id),
    kill_time_in_round INT NOT NULL,
    kill_time_in_match INT NOT NULL,
    PRIMARY KEY (kill_id)
);

CREATE TABLE degat
(
    damage_id INT REFERENCES evenement_joueur(id_event_player),
    damage_count INT,
    headshots INT NOT NULL,
    bodyshots INT NOT NULL,
    legshots INT NOT NULL,
    PRIMARY KEY (damage_id)
);

CREATE TABLE localisation_joueur
(
    location_id SERIAL PRIMARY KEY,
    player_id CHAR(36) REFERENCES joueur(puuid),
    kill_id INT REFERENCES elimination(kill_id),
    x FLOAT NOT NULL,
    y FLOAT NOT NULL,
    view_radiant DOUBLE PRECISION NOT NULL
);