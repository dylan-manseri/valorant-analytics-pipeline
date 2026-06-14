-- Agent le plus joué par le joueur.
-- `compose` enregistre l'agent choisi par le joueur pour chaque (joueur, équipe).
SELECT agent_name, COUNT(*) AS played_count
FROM compose
    JOIN agent ON compose.agent_id = agent.agent_id
WHERE compose.puuid = '08993ff7-ffe1-58b9-b42c-b4e68b6ebd4e'
GROUP BY agent_name
ORDER BY played_count DESC
LIMIT 1;
