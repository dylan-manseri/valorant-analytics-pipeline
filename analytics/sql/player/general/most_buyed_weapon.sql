-- Arme la plus achetée par le joueur (loadout de début de round).
-- ⚠ `joue.weapon_id` correspond à l'arme ACHETÉE en début de round, pas à celle
-- éventuellement ramassée au sol pendant le round. C'est une limite des données :
-- les armes ramassées sont invisibles ici.
SELECT weapon_name, COUNT(*) AS buy_count
FROM arme
    JOIN joue ON arme.weapon_id = joue.weapon_id
WHERE joue.puuid = '08993ff7-ffe1-58b9-b42c-b4e68b6ebd4e'
GROUP BY weapon_name
ORDER BY buy_count DESC
LIMIT 1;
