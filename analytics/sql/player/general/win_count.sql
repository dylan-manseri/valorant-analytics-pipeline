-- Nombre de parties gagnées par le joueur.
-- Le statut de victoire est stocké côté `equipe` (has_won), pas côté joueur :
-- on rejoint donc `equipe` depuis `compose` pour filtrer sur ce booléen.
-- COUNT(DISTINCT team_id) garantit qu'on ne double-compte pas si plusieurs lignes
-- `compose` existent pour la même équipe (cas d'un changement d'agent en partie).
SELECT COUNT(DISTINCT equipe.team_id) AS win_count
FROM equipe
    JOIN compose ON equipe.team_id = compose.team_id
WHERE compose.puuid = '08993ff7-ffe1-58b9-b42c-b4e68b6ebd4e'
  AND equipe.has_won = true;
