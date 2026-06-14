-- Arme avec laquelle le joueur a fait le plus de kills.
-- Source : `elimination` (1 ligne par kill) avec `damage_weapon` = arme du tueur.
--
-- `author != victim` exclut les éventuels événements où le joueur figure comme
-- tueur ET victime (suicide / dégâts de zone), qui n'ont pas de sens en duel.
SELECT weapon_name, COUNT(*) AS kill_count
FROM elimination
    JOIN arme             ON elimination.damage_weapon = arme.weapon_id
    JOIN evenement_joueur ON elimination.kill_id      = evenement_joueur.id_event_player
WHERE evenement_joueur.author = '08993ff7-ffe1-58b9-b42c-b4e68b6ebd4e'
  AND evenement_joueur.author != evenement_joueur.victim
GROUP BY weapon_name
ORDER BY kill_count DESC
LIMIT 1;
