-- Site le plus planté en début de demi-temps (round 0 = attaque, round 11 =
-- défense après switch de côté), par carte.
--
-- On ne regarde que les rounds 0 et 11 car ce sont les seuls rounds joués
-- sans aucune information préalable sur le style de jeu de l'adversaire dans
-- cette demi-temps : le choix de site y est donc le plus "pur", non influencé
-- par les rounds précédents.
--
-- DISTINCT ON (map_name) + ORDER BY map_name, COUNT(*) DESC : ne garde qu'une
-- seule ligne par carte, celle du site le plus fréquemment planté.
SELECT DISTINCT ON (map_name)
    map_name,
    plant_site,
    COUNT(*)
FROM round
    JOIN equipe AS equipe_gagnante ON round.winning_team_id = equipe_gagnante.team_id
    JOIN partie ON equipe_gagnante.party_id = partie.party_id
    JOIN carte ON partie.map_id = carte.map_id
WHERE (number = 0 OR number = 11)   -- premier round de chaque demi-temps
  AND plant_site IS NOT NULL         -- exclut les rounds gagnés sans plant
GROUP BY map_name, plant_site
ORDER BY map_name, COUNT(*) DESC;