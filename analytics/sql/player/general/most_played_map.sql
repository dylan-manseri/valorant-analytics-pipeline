-- Map la plus jouée par le joueur.
-- Chemin de jointure : carte → partie (map_id) → equipe (party_id) → compose (team_id).
-- On compte les participations (`compose`) groupées par map.
SELECT map_name, COUNT(*) AS played_count
FROM carte
    JOIN partie  ON carte.map_id    = partie.map_id
    JOIN equipe  ON partie.party_id = equipe.party_id
    JOIN compose ON equipe.team_id  = compose.team_id
WHERE compose.puuid = '08993ff7-ffe1-58b9-b42c-b4e68b6ebd4e'
GROUP BY map_name
ORDER BY played_count DESC
LIMIT 1;
