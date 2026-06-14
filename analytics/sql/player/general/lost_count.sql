-- Nombre de parties perdues par le joueur.
-- Miroir de `win_count.sql` : filtre `has_won = false` côté `equipe`.
-- COUNT(DISTINCT team_id) protège contre les doublons éventuels dans `compose`.
SELECT COUNT(DISTINCT equipe.team_id) AS lost_count
FROM equipe
    JOIN compose ON equipe.team_id = compose.team_id
WHERE compose.puuid = '08993ff7-ffe1-58b9-b42c-b4e68b6ebd4e'
  AND equipe.has_won = false;
