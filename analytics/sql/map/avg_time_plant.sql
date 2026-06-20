-- Temps moyen avant le plant du spike, par carte.
--
-- Sert d'indicateur indirect pour estimer le rythme de jeu (rapide/direct vs
-- lent/avec rotations) : un round qui rote avant de planter prend forcément
-- plus de temps qu'une exécution directe. La métrique ne permet toutefois pas
-- de distinguer "rotation" de "jeu simplement lent" — c'est une limite
-- assumée, pas une mesure directe de rotation.
--
-- plant_time_in_round est stocké en millisecondes (vérifié empiriquement,
-- valeurs ~30000-45000) → conversion en secondes avant moyenne.
SELECT
    map_name,
    ROUND(AVG(round.plant_time_in_round / 1000), 1) AS avg_plant_time_seconds
FROM round
    JOIN equipe ON round.winning_team_id = equipe.team_id
    JOIN partie ON equipe.party_id = partie.party_id
    JOIN carte ON partie.map_id = carte.map_id
WHERE plant_time_in_round IS NOT NULL
GROUP BY map_name;