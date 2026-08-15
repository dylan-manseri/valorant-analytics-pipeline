-- % de "bonne intention de site" en défense : parmi les rounds défendus avec
-- spike planté, proportion où le joueur a un kill proche du plant (< 3000
-- unités) et dans une fenêtre de 20000 ms autour du plant.
-- Côté défense déterminé via first_side + numéro de round.

WITH my_rounds AS (
    -- Recherche de tous mes rounds fais sur toutes mes parties
    SELECT round.round_id, number, end_type, bomb_planted, plant_site,
           bomb_defused, plant_time_in_round, plant_coord_x, plant_coord_y,
           partie.party_id AS num_partie
    FROM joueur
        JOIN joue ON joueur.puuid = joue.puuid
        JOIN round ON joue.round_id = round.round_id
        JOIN equipe ON round.winning_team_id = equipe.team_id
        JOIN partie ON equipe.party_id = partie.party_id
    WHERE joueur.puuid = '08993ff7-ffe1-58b9-b42c-b4e68b6ebd4e'
),
my_teams AS (
    -- Recherche de toutes mes équipes sur toutes mes parties, afin d'obtenir les rounds défenses
    SELECT joueur.puuid, equipe.team_id, color, has_won, first_side, partie.party_id
    FROM joueur
        JOIN compose ON joueur.puuid = compose.puuid
        JOIN equipe ON compose.team_id = equipe.team_id
        JOIN partie ON equipe.party_id = partie.party_id
    WHERE joueur.puuid = '08993ff7-ffe1-58b9-b42c-b4e68b6ebd4e'
),
my_defense_rounds AS (
    -- Recherche de tous mes rounds défenses à partir des deux dernières tables.
    SELECT *
    FROM my_rounds
        JOIN my_teams ON my_rounds.num_partie = my_teams.party_id
    WHERE (
              (first_side = 'attack' AND number > 11)
              OR (first_side = 'defense' AND number <= 11)
          )
      AND my_rounds.bomb_planted = true
      AND my_rounds.plant_coord_x IS NOT NULL
      AND my_rounds.plant_coord_y IS NOT NULL
)
SELECT
    COUNT(DISTINCT my_defense_rounds.round_id) AS round_defended,
    -- Sous requête scalaire pour calculer le nombre total de rounds.
    -- C'est néccessaire car l'info ne se trouve dans aucune colonne mais dans la table my_defense_rounds.
    (SELECT COUNT(DISTINCT round_id) FROM my_defense_rounds) AS total_round,
    COUNT(DISTINCT my_defense_rounds.round_id)::numeric
        / (SELECT COUNT(DISTINCT round_id) FROM my_defense_rounds) * 100 AS pourcentage
FROM my_defense_rounds
    JOIN my_teams ON my_teams.party_id = my_defense_rounds.party_id
    JOIN evenement_joueur ON my_defense_rounds.round_id = evenement_joueur.round_id
                          AND evenement_joueur.author = '08993ff7-ffe1-58b9-b42c-b4e68b6ebd4e'
    JOIN elimination ON evenement_joueur.id_event_player = elimination.kill_id
    JOIN localisation_joueur ON elimination.kill_id = localisation_joueur.kill_id
                             AND evenement_joueur.author = localisation_joueur.player_id
WHERE ABS(kill_time_in_round - my_defense_rounds.plant_time_in_round) < 20000
  AND SQRT(
          POWER(localisation_joueur.x - my_defense_rounds.plant_coord_x, 2)
          + POWER(localisation_joueur.y - my_defense_rounds.plant_coord_y, 2)
      ) < 3000;