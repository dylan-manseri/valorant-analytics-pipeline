# Valorant Stats Tracker

Projet personnel d'initiation à la récupération, au traitement et à l'affichage de données avec des outils concrets (Python, PostgreSQL, pandas, Streamlit). Les données sont issues de mes propres matchs Valorant via l'API Henrik.

---

## Roadmap *(non exhaustive, amenée à évoluer)*

## 1. Trouver l'API
- [x] Tentative avec l'API Riot officielle (réservée aux partenaires) → abandon.
- [x] Découverte de l'API Henrik → choix retenu (gratuite, non officielle).
- [x] Lecture de la documentation Henrik.

## 2. Fetch l'API
- [x] Récupération du PUUID d'un joueur à partir de son nom et tag.
- [x] Récupération des 5 derniers matchs via le PUUID.
- [x] Stockage des données brutes dans un fichier `matches.json`.

## 3. Schéma MCD
- [x] Analyse de la structure JSON de l'API, sélection des données pertinentes.
- [x] Modélisation des entités et relations (matches, players, match_players, kill_events).
- [x] Création du MCD (cf. fichier docs).

## 4. Script SQL
- [x] Définition de l'ordre de création des tables et des clés étrangères.
- [x] Définition du DDL.
- [x] Exécution du DDL sur la base de données.

## 5. Pipeline d'insertion Python
- [x] Etude de faisabilité avec les librairies existante.
- [x] Fonctions d'insertion des tables à faible dépendance (Carte, Partie, Équipe).
- [ ] Fonctions d'insertion des tables à forte dépendance.

## 6. Tests
- [ ] Vérifier l'intégrité des données insérées.
- [ ] Tester avec plusieurs matchs.

## 7. Requêtes SQL d'analyse
- [ ] Définir les métriques à analyser (KDA, win rate, headshot %).
- [ ] Écrire les requêtes SQL correspondantes.

## 8. Analyse avec pandas
- [ ] À définir

## 9. Tableau de bord
- [ ] À définir
