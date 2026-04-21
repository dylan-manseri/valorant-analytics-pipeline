# Valorant Stats Tracker

Projet personnel d'initiation à la récupération, au traitement et à l'affichage de données avec des outils concrets (Python, PostgreSQL, pandas, Streamlit). Les données sont issues de mes propres matchs Valorant via l'API Henrik.

---

## Roadmap *(non exhaustive, amenée à évoluer)*

## 1. Trouver l'API
- [x] Tentative avec l'API Riot officielle (réservée aux partenaires) → abandon
- [x] Découverte de l'API Henrik → choix retenu (gratuite, non officielle)
- [x] Lecture de la documentation Henrik

## 2. Fetch l'API
- [x] Récupération du PUUID d'un joueur à partir de son nom et tag
- [x] Récupération des 5 derniers matchs via le PUUID
- [x] Stockage des données brutes dans un fichier `matches.json`

## 3. Schéma MCD
- [ ] Analyse de la structure JSON de l'API, sélection des données pertinentes
- [ ] Modélisation des entités et relations (matches, players, match_players, kill_events)
- [ ] Création du MCD

## 4. Script SQL
- [ ] À définir

## 5. Pipeline Python
- [ ] À définir

## 6. Analyse avec pandas
- [ ] À définir

## 7. Tableau de bord
- [ ] À définir
