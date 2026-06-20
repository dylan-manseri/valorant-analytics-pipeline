-- ───────────────────────────────────────────────────────────────────────────
-- Winrate de duel (échange Vandal/Phantom confirmé, sans assist d'aucun côté)
--
-- ─── Définition retenue pour "duel" ─────────────────────────────────────────
-- Un duel valide doit respecter TROIS conditions cumulées :
--   1. Les deux joueurs ont Vandal/Phantom (ou la même arme), pour ne comparer
--      que des confrontations à armes comparables.
--   2. Échange de dégâts réciproque confirmé dans le même round (la victime a
--      elle aussi touché le tueur) → exclut les kills surprise / backstabs,
--      qui ne génèrent aucun dégât retour.
--   3. Aucun tiers n'a infligé plus de 50 dégâts ni au tueur ni à la victime
--      dans ce round → exclut les kills/morts assistés (1v1 isolé uniquement).
--
-- ─── Pourquoi la condition d'assist est symétrique ─────────────────────────
-- Un filtre asymétrique (vérifier l'assist seulement côté victime) biaise le
-- ratio : statistiquement, les morts impliquent plus souvent un tiers (trade
-- côté adverse) que les kills (souvent un engagement seul). Filtrer un seul
-- côté retire alors plus de défaites que de victoires et gonfle le ratio
-- artificiellement. D'où les deux NOT EXISTS, un par rôle.
--
-- ⚠ Limite connue : `all_damage` est filtré sur Vandal/Phantom. Un tiers
-- jouant une autre arme (Sheriff, Spectre...) n'apparaît pas dans cette CTE et
-- ne sera donc pas détecté comme assist. Le filtre d'assist n'est donc fiable
-- que pour les tiers eux-mêmes en Vandal/Phantom.
-- ───────────────────────────────────────────────────────────────────────────

WITH all_damage AS (
    -- Tous les échanges de dégâts (kill ou non) impliquant le joueur, où les
    -- deux protagonistes ont une arme comparable (même arme, ou Vandal/Phantom
    -- des deux côtés). Sert à la fois à confirmer la réciprocité du duel et
    -- à détecter d'éventuels assists.
    SELECT
        evenement_joueur.author AS auteur,
        evenement_joueur.victim AS victime,
        author_weapon.weapon_name AS arme_auteur,
        victim_weapon.weapon_name AS arme_victime,
        round.round_id,
        damage_count
    FROM degat
        JOIN evenement_joueur ON evenement_joueur.id_event_player = degat.damage_id
        JOIN round ON evenement_joueur.round_id = round.round_id
        -- Arme du tueur au moment du round (loadout, cf. limite connue sur `joue`)
        JOIN joue AS author_joue ON round.round_id = author_joue.round_id
                                 AND evenement_joueur.author = author_joue.puuid
        JOIN arme AS author_weapon ON author_joue.weapon_id = author_weapon.weapon_id
        -- Arme de la victime au même round
        JOIN joue AS victim_joue ON round.round_id = victim_joue.round_id
                                 AND evenement_joueur.victim = victim_joue.puuid
        JOIN arme AS victim_weapon ON victim_joue.weapon_id = victim_weapon.weapon_id
    WHERE (evenement_joueur.author = %(puuid)s OR evenement_joueur.victim = %(puuid)s)
      AND (
          author_weapon.weapon_name = victim_weapon.weapon_name
          OR (author_weapon.weapon_name IN ('Vandal', 'Phantom')
              AND victim_weapon.weapon_name IN ('Vandal', 'Phantom'))
      )
),
all_elimination AS (
    -- Les kills uniquement, même filtre d'armes que all_damage, pour identifier
    -- les duels candidats (avant application des conditions de réciprocité et
    -- d'absence d'assist).
    SELECT
        evenement_joueur.author AS auteur,
        evenement_joueur.victim AS victime,
        author_weapon.weapon_name AS arme_auteur,
        victim_weapon.weapon_name AS arme_victime,
        round.round_id
    FROM elimination
        JOIN evenement_joueur ON elimination.kill_id = evenement_joueur.id_event_player
        JOIN round ON evenement_joueur.round_id = round.round_id
        -- Arme effective du kill, directement depuis `elimination`
        JOIN arme AS author_weapon ON elimination.damage_weapon = author_weapon.weapon_id
        -- Arme de la victime au round (loadout)
        JOIN joue AS victim_joue ON round.round_id = victim_joue.round_id
                                 AND evenement_joueur.victim = victim_joue.puuid
        JOIN arme AS victim_weapon ON victim_joue.weapon_id = victim_weapon.weapon_id
    WHERE (evenement_joueur.author = %(puuid)s OR evenement_joueur.victim = %(puuid)s)
      AND (
          author_weapon.weapon_name = victim_weapon.weapon_name
          OR (author_weapon.weapon_name IN ('Vandal', 'Phantom')
              AND victim_weapon.weapon_name IN ('Vandal', 'Phantom'))
      )
)
SELECT
    ROUND(duels_gagnes::numeric / NULLIF(duels_gagnes + duels_perdus, 0), 2) AS duel_ratio
FROM (
    SELECT
        -- Duels gagnés : le joueur est l'auteur du kill
        COUNT(*) FILTER (WHERE auteur = %(puuid)s) AS duels_gagnes,
        -- Duels perdus : le joueur est la victime du kill
        COUNT(*) FILTER (WHERE victime = %(puuid)s) AS duels_perdus
    FROM all_elimination
    WHERE
        -- Condition 1 : réciprocité confirmée (la victime a aussi touché l'auteur
        -- dans ce même round)
        EXISTS (
            SELECT 1 FROM all_damage
            WHERE victime = all_elimination.auteur
              AND auteur = all_elimination.victime
              AND round_id = all_elimination.round_id
        )
        -- Condition 2 : pas d'assist côté victime (aucun tiers n'a fait plus de
        -- 50 dégâts à la victime dans ce round)
        AND NOT EXISTS (
            SELECT 1 FROM all_damage
            WHERE victime = all_elimination.victime
              AND auteur != all_elimination.auteur
              AND round_id = all_elimination.round_id
              AND damage_count > 50
        )
        -- Condition 3 (symétrique) : pas d'assist côté auteur (aucun tiers n'a
        -- fait plus de 50 dégâts à l'auteur dans ce round)
        AND NOT EXISTS (
            SELECT 1 FROM all_damage
            WHERE victime = all_elimination.auteur
              AND auteur != all_elimination.victime
              AND round_id = all_elimination.round_id
              AND damage_count > 50
        )
) AS total;