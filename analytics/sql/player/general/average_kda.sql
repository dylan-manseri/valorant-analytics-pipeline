-- KDA cumulé du joueur sur l'ensemble de ses parties.
--
-- Formule retenue : SUM(K + A) / SUM(D)
--   → convention "officielle" Riot / tracker.gg ; chaque round pèse à proportion
--     de son volume d'actions (vs. AVG((K+A)/D) qui pondère chaque partie pareil
--     et est très sensible aux petites parties avec peu de morts).
--
-- Choix techniques :
--   ::numeric    → force une division décimale exacte ; sans cast, INT/INT ferait
--                  une division entière tronquée (29/25 = 1 au lieu de 1.16).
--   NULLIF(.,0)  → si le joueur n'est jamais mort, on évite la division par zéro
--                  (NULLIF transforme 0 en NULL, et NULL/x = NULL → pas de crash).
--   ROUND(.,2)   → arrondi à 2 décimales pour un affichage propre, comme en jeu.
SELECT ROUND(
           SUM(kills + assists)::numeric / NULLIF(SUM(deaths), 0),
           2
       ) AS kda_avg
FROM compose
WHERE puuid = '08993ff7-ffe1-58b9-b42c-b4e68b6ebd4e';
