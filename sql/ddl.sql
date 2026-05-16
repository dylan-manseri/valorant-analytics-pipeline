CREATE TABLE Carte
(
    map_id SERIAL PRIMARY KEY,
    name VARCHAR(20) UNIQUE NOT NULL
);

CREATE TABLE Partie
(
    party_id CHAR(36) PRIMARY KEY,
    map_id INT REFERENCES Carte(map_id),
    match_date DATE NOT NULL,
    mode VARCHAR(20) NOT NULL,
    server VARCHAR(9) NOT NULL,
    patch FLOAT NOT NULL
);

CREATE TABLE Equipe
(
    team_id SERIAL PRIMARY KEY,
    party_id CHAR(36) REFERENCES Partie(party_id),
    color VARCHAR(4) NOT NULL CHECK ( color in ('red', 'blue') ),
    has_won BOOLEAN NOT NULL,
    round_won INT NOT NULL,
    round_lost INT NOT NULL,
    first_side VARCHAR(7) CHECK ( first_side IN ('attack', 'defense'))
);

CREATE TABLE Agent
(
    agent_id SERIAL PRIMARY KEY,
    name VARCHAR(20) UNIQUE NOT NULL,
    asset_agent VARCHAR(255)
);

CREATE TABLE Joueur
(
    puuid CHAR(36) PRIMARY KEY,
    username VARCHAR(16) NOT NULL,
    tag VARCHAR(5) NOT NULL,
    account_level INT NOT NULL,
    rank VARCHAR(10) NOT NULL,
    card VARCHAR(255) NOT NULL
);

CREATE TABLE Compose
(
    puuid CHAR(36) REFERENCES Joueur(puuid),
    team_id INT REFERENCES Equipe(team_id),
    agent_id INT REFERENCES Agent(agent_id),
    kills INT NOT NULL,
    deaths INT NOT NULL,
    assists INT NOT NULL,
    PRIMARY KEY (puuid, team_id, agent_id)
);

CREATE TABLE Armure
(
    armor_id SERIAL PRIMARY KEY,
    armor_name VARCHAR(20) UNIQUE NOT NULL,
    asset_armor VARCHAR(255)
);

CREATE TABLE Arme
(
    weapon_id SERIAL PRIMARY KEY,
    weapon_name VARCHAR(20) UNIQUE NOT NULL,
    asset_weapon VARCHAR(255)
);

CREATE TABLE Round
(
    round_id SERIAL PRIMARY KEY,
    team_won INT REFERENCES Equipe(team_id),
    end_type VARCHAR(20) NOT NULL,
    bomb_planted BOOLEAN NOT NULL,
    bomb_defused BOOLEAN NOT NULL,
    plant_site CHAR(1) NOT NULL,
    plant_time_in_round INT,
    plant_coord_x FLOAT,
    plant_coord_y FLOAT
);

CREATE TABLE Joue
(
    puuid CHAR(36) REFERENCES Joueur(puuid),
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
);

CREATE TABLE Evenement_joueur
(
    id_event_player SERIAL PRIMARY KEY,
    victim CHAR(36) REFERENCES Joueur(puuid),
    author CHAR(36) REFERENCES Joueur(puuid)
);

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
);

CREATE TABLE Degat
(
    damage_id INT REFERENCES Evenement_joueur(id_event_player),
    headshot INT NOT NULL,
    bodyshot INT NOT NULL,
    legshot INT NOT NULL,
    PRIMARY KEY (damage_id)
);

CREATE TABLE Localisation_alliee
(
    teammate_location_id SERIAL PRIMARY KEY,
    player_id CHAR(36) REFERENCES Joueur(puuid),
    kill_id INT REFERENCES Elimination(kill_id),
    x FLOAT NOT NULL,
    y FLOAT NOT NULL
);