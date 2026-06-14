-- Meilleure arme du joueur en duel : ratio (duels gagnés / duels perdus) par arme.
--
-- ─── Asymétrie des sources ──────────────────────────────────────────────────
-- Les kills et les morts ne se lisent PAS de la même façon dans le schéma :
--
--   • Duels gagnés  → `elimination.damage_weapon` = arme du tueur (= moi). Direct.
--   • Duels perdus  → `elimination.damage_weapon` = arme de l'adversaire ; pour
--                     retrouver MON arme dans ce round, il faut rejoindre `joue`
--                     (loadout du joueur) sur (puuid, round_id).
--
-- ⚠ Biais accepté : `joue.weapon_id` est l'arme ACHETÉE au début du round, pas
-- l'arme effectivement tenue à la mort. Si je meurs en ayant ramassé un Vandal
-- au sol alors que j'avais acheté un Spectre, ça sera compté sur le Spectre.
-- L'API ne fournit pas l'arme tenue à l'instant de la mort → on s'en accommode.
--
-- ─── Stratégie de la requête ────────────────────────────────────────────────
-- Deux CTE pour les deux côtés du ratio, puis FULL OUTER JOIN pour conserver
-- les armes qui n'apparaissent que d'un seul côté (ex : Sheriff 10 kills / 0 mort).
WITH duels_gagnes AS (
    SELECT weapon_name, COUNT(*) AS win
    FROM evenement_joueur
        JOIN elimination ON evenement_joueur.id_event_player = elimination.kill_id
        JOIN arme        ON elimination.damage_weapon       = arme.weapon_id
    WHERE evenement_joueur.author = '12fb0f7a-d96a-5bce-90ab-2d25beab4c19'
      AND evenement_joueur.author != evenement_joueur.victim   -- exclut les suicides
    GROUP BY weapon_name
),
duels_perdus AS (
    SELECT weapon_name, COUNT(*) AS lost
    FROM evenement_joueur
        JOIN elimination ON evenement_joueur.id_event_player = elimination.kill_id
        -- jointure sur (puuid, round_id) : sans le round_id on ferait un produit
        -- cartésien (toutes les armes jouées par moi × toutes mes morts).
        JOIN joue ON evenement_joueur.victim   = joue.puuid
                 AND evenement_joueur.round_id = joue.round_id
        JOIN arme ON joue.weapon_id = arme.weapon_id
    WHERE evenement_joueur.victim = '12fb0f7a-d96a-5bce-90ab-2d25beab4c19'
      AND evenement_joueur.author != evenement_joueur.victim
    GROUP BY weapon_name
)
-- COALESCE(win, 0)        → transforme "pas de kill" en 0 (ratio 0.00) plutôt
--                           que NULL (qui rendrait la ligne ininterprétable).
-- division par `lost` brut → si `lost` est NULL (jamais mort avec cette arme),
--                           le ratio est NULL = "infini" = arme parfaite. Pas
--                           besoin de NULLIF ici car COUNT(*) sur GROUP BY ne
--                           renvoie jamais 0 — il renvoie NULL via le FULL JOIN.
-- NULLS FIRST              → place les armes parfaites en tête du classement.
SELECT
    weapon_name,
    COALESCE(win,  0)                          AS win,
    COALESCE(lost, 0)                          AS lost,
    ROUND(COALESCE(win, 0)::numeric / lost, 2) AS ratio
FROM duels_gagnes
    FULL OUTER JOIN duels_perdus USING (weapon_name)
ORDER BY ratio DESC NULLS FIRST;
