WITH ev_author AS (
    SELECT joueur.puuid, agent_name, id_event_player, eq_total.party_id FROM joueur
        JOIN evenement_joueur ON joueur.puuid = evenement_joueur.author
        JOIN round ON evenement_joueur.round_id = round.round_id
        JOIN equipe AS eq_gagnante ON round.winning_team_id = eq_gagnante.team_id
        JOIN partie ON eq_gagnante.party_id = partie.party_id
        JOIN equipe AS eq_total ON partie.party_id = eq_total.party_id
        JOIN compose ON joueur.puuid = compose.puuid AND eq_total.team_id = compose.team_id
        JOIN agent ON compose.agent_id = agent.agent_id

        JOIN elimination ON evenement_joueur.id_event_player = elimination.kill_id
),
ev_victim AS (
    SELECT joueur.puuid, agent_name, id_event_player, eq_total.party_id FROM joueur
        JOIN evenement_joueur ON joueur.puuid = evenement_joueur.victim
        JOIN round ON evenement_joueur.round_id = round.round_id
        JOIN equipe AS eq_gagnante ON round.winning_team_id = eq_gagnante.team_id
        JOIN partie ON eq_gagnante.party_id = partie.party_id
        JOIN equipe AS eq_total ON partie.party_id = eq_total.party_id
        JOIN compose ON joueur.puuid = compose.puuid AND eq_total.team_id = compose.team_id
        JOIN agent ON compose.agent_id = agent.agent_id

        JOIN elimination ON evenement_joueur.id_event_player = elimination.kill_id
        WHERE victim = '08993ff7-ffe1-58b9-b42c-b4e68b6ebd4e'
)
SELECT ev_author.agent_name, COUNT(*) AS total_death, COUNT(DISTINCT ev_author.party_id) AS count_party,
       ROUND(COUNT(*)::numeric / NULLIF(COUNT(DISTINCT ev_author.party_id), 0), 2) AS morts_par_partie
FROM ev_author
    JOIN ev_victim ON ev_author.id_event_player = ev_victim.id_event_player AND ev_author.party_id = ev_victim.party_id
    GROUP BY ev_author.agent_name
    ORDER BY morts_par_partie DESC;