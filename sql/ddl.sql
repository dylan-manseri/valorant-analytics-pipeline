CREATE TABLE Carte
(
    map_id SERIAL PRIMARY KEY,
    name VARCHAR(20) UNIQUE NOT NULL,
    version FLOAT NOT NULL
)

CREATE TABLE Partie
(
    match_id SERIAL PRIMARY KEY,
    map_id INT REFERENCES Carte(map_id),
    match_date DATE NOT NULL,
    mode VARCHAR(20) NOT NULL,
    server CHAR(3) NOT NULL,
    patch FLOAT NOT NULL
)

CREATE TABLE Equipe
(
    team_id SERAIL PRIMARY KEY,
    match_id INT REFERENCES Partie(match_id),
    has_won BOOLEAN,
    round_won INT NOT NULL,
    round_loss INT NOT NULL,
    color VARCHAR(4) NOT NULL
)

CREATE TABLE Agent
(
    agent_id SERIAL PRIMARY KEY,
    name VARCHAR(20) UNIQUE NOT NULL,
    asset_agent VARCHAR(100) NULLABLE
)

CREATE TABLE Joueur
(
    puuid SERIAL PRIMARY KEY,
    username VARCHAR(16) NOT NULL,
    tag VARCHAR(5) NOT NULL,
    level INT NOT NULL,
    rank VARCHAR(10) NOT NULL
)

CREATE TABLE Compose
(
    puuid INT REFERENCES Joueur(puuid),
    team_id INT REFERENCES Equipe(team_id),
    agent_id INT REFERENCES Agent(agent_id),
    PRIMARY KEY (puuid, team_id, agenti_id)
)

CREATE TABLE Armure
(
    armor_id SERIAL PRIMARY KEY,
    armor_name VARCHAR(20) UNIQUE NOT NULL,
    armor_asset VARCHAR(100) NULLABLE
)

CREATE TABLE Arme
(
    weapon_id SERIAL PRIMARY KEY,
    weapon_name VARCHAR(20) UNIQUE NOT NULL,
    weapon_asset VARCHAR(100) NULLABLE
)

CREATE TABLE Round
(
    round_id SERIAL PRIMARY KEY,
    team_won INT REFERENCES Equipe(team_id)
    end_type VARCHAR(20) NOT NULL,
    bomb_planted BOOLEAN NOT NULL,
    bomb_defused BOOLEAN NOT NULL,
    plant_site CHAR(1) NOT NULL,
    plant_time_in_round INT NULLABLE
)

CREATE TABLE Joue
(
    puuid INT REFERENCES Joueur(puuid),
    armor_id INT REFERENCES Armure(armor_id),
    weapon_id INT REFERENCES Arme(weapon_id),
    round_id INT REFERENCES  Round(round_id),
    ability_cast_x INT NOT NULL,
    ability_cast_e INT NOT NULL,
    ability_cast_q INT NOT NULL,
    ability_cast_c INT NOT NULL,
    score INT NOT NULL,
    loadout_value INT NOT NULL,
    spent INT NOT NULL,
    remaining INT NOT NULL,
    PRIMARY KEY(puuid, armor_id, weapon_id, round_id)
)

CREATE TABLE Evenement_joueur
(
    id_event_player SERIAL PRIMARY KEY,
    victim INT REFERENCES Joueur(puuid),
    author INT REFERENCES Joueur(puuid)
)

CREATE TABLE Elimination
(
    kill_id INT REFERENCES Evenement_joueur(id_event_player),
    kill_time_in_round INT NOT NULL,
    kill_time_in_match INT NOT NULL,
    victim_location_x FLOAT NOT NULL,
    victim_location_y FLOAT NOT NULL,
    killer_location_x FLOAT NOT NULL,
    killer_location_y FLOAT NOT NULL,
    PRIMARY KEY (kill_id)
)

CREATE TABLE Degat
(
    damage_id INT REFERENCES Evenement_joueur(id_event_player),
    headshot INT NOT NULL,
    bodyshot INT NOT NULL,
    legshot INT NOT NULL,
    PRIMARY KEY (damage_id)
)

CREATE TABLE Localisation_alliee
(
    teammate_location_id SERIAL PRIMARY KEY,
    player_id INT REFERENCES Joueur(puuid),
    kill_id INT REFERENCES Elimination(kill_id),
    x INT NOT NULL,
    y INT NOT NULL
)