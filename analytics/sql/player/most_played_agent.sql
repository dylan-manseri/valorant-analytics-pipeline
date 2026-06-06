SELECT agent_name, COUNT(*) from joueur
    JOIN compose ON joueur.puuid = compose.puuid
    JOIN agent ON compose.agent_id = agent.agent_id
WHERE puuid = %(puuid)s GROUP BY agent_name ORDER BY COUNT(*) DESC LIMIT 1