-- Nombre total de parties jouées par le joueur.
-- Source : `compose` (1 ligne par (joueur, équipe, agent)) remontée jusqu'à `partie`.
-- COUNT(DISTINCT party_id) protège contre un éventuel switch d'agent en cours de
-- partie qui produirait plusieurs lignes `compose` pour une même `partie`.
SELECT COUNT(DISTINCT partie.party_id) AS party_count
FROM partie
    JOIN equipe  ON partie.party_id = equipe.party_id
    JOIN compose ON equipe.team_id  = compose.team_id
WHERE compose.puuid = '08993ff7-ffe1-58b9-b42c-b4e68b6ebd4e';
