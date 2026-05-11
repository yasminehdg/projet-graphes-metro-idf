# Analyse du Réseau Métro & RER — Île-de-France
### Projet Graphes & OpenData — MIAGE Université Paris Nanterre

Modélisation, analyse et visualisation du réseau de transport en commun
d'Île-de-France par la théorie des graphes.

---

## Structure du projet

```
Projet-Graphes-OpenData/
├── metro_rer_idf.csv          <- Base de données OpenData (Kaggle)
├── metro_graphe.py            <- Script principal : stats + carte + images
├── generer_graphes.py         <- 3 graphes visuels animés du réseau
├── graphes_utiles.py          <- 4 graphes analytiques et informatifs
├── metro_final.html           <- Dashboard interactif complet (11 onglets)
├── graphique_stats.png        <- Graphique statistiques (PNG)
├── graphe_visualisation.png   <- Visualisation géographique (PNG)
└── README.md                  <- Ce fichier
```

---

## Installation

### 1. Cloner le projet
```bash
git clone https://github.com/VOTRE_NOM/projet-graphes-opendata.git
cd projet-graphes-opendata
```

### 2. Installer les dépendances Python
```bash
pip install networkx pandas matplotlib folium pyvis
```

---

## Lancer le projet

### Script 1 — Statistiques + Carte + Images PNG
```bash
python metro_graphe.py
```
Produit :
- Affiche les statistiques dans le terminal
- `graphique_stats.png` — distribution des degrés et centralité
- `graphe_visualisation.png` — graphe géographique du réseau
- `carte_interactive.html` — carte Folium interactive

---

### Script 2 — Graphes visuels animés du réseau
```bash
python generer_graphes.py
```
Produit :
- `graphe_reseau_complet.html` — les 571 stations animées
- `graphe_correspondances.html` — stations avec correspondances
- `graphe_rer.html` — réseau RER uniquement (5 lignes)

---

### Script 3 — Graphes analytiques et informatifs
```bash
python graphes_utiles.py
```
Produit :
- `graphe1_carte_chaleur.html` — stations surchargées en rouge
- `graphe2_vulnerabilite.html` — points d'articulation critiques
- `graphe3_perturbation.html` — impact fermeture Saint-Lazare
- `graphe4_plus_court_chemin.html` — trajet Chatelet -> Versailles

---

### Dashboard interactif
```
Ouvrir metro_final.html avec Google Chrome ou Microsoft Edge
```
Aucune installation nécessaire — le fichier est autonome.

---

## Résultats principaux

| Propriété | Valeur |
|---|---|
| Sommets (stations) | 571 |
| Arêtes (connexions) | 634 |
| Graphe connexe | Oui |
| Degré moyen | 2,22 |
| Degré maximum | 10 (Saint-Lazare) |
| Points d'articulation | 287 (50,3% des stations) |
| Diamètre du graphe | 61 |
| Distance moyenne | 17,47 arrêts |

---

## Fonctionnalités du Dashboard (11 onglets)

| Onglet | Description |
|---|---|
| Stats | Statistiques globales + Top 10 degré et centralité |
| Carte | Graphe géographique filtrable par ligne |
| Chemin | Plus court chemin entre 2 stations (BFS) |
| Perturbation | Fermeture d'une station + animation |
| Stations Critiques | Points d'articulation du réseau |
| Zone de Couverture | Stations accessibles en N arrêts |
| Comparaison | BFS (arrêts) vs Dijkstra (kilometres) |
| Greve | Impact fermeture d'une ligne entière |
| Stations Isolées | Excentricité — stations les plus éloignées |
| Petit Monde | Distance moyenne et diamètre du graphe |
| Analyse | Distribution des degrés + propriétés formelles |

---

## Concepts de théorie des graphes utilisés

- G = (V, E) — graphe non orienté, simple, sans boucle, pondéré
- Degré d'un sommet — nombre de connexions directes
- Connexité — existence d'un chemin entre toute paire de stations
- BFS (Breadth-First Search) — plus court chemin non pondéré
- Dijkstra — plus court chemin pondéré (distance km)
- Centralité d'intermédiarité — stations les plus stratégiques
- Points d'articulation — stations critiques dont la suppression déconnecte le graphe
- Excentricité — distance maximale d'une station aux autres
- Diamètre — plus longue des plus courtes distances
- Petit monde — analyse de la distance moyenne du réseau

---

## Bibliothèques utilisées

| Bibliothèque | Utilisation |
|---|---|
| NetworkX | Construction et analyse du graphe |
| Pandas | Chargement des données CSV |
| Matplotlib | Graphiques statistiques |
| Folium | Carte interactive géographique |
| Pyvis | Graphes interactifs et animés |

---

## Auteur

Yasmine HADDAG et Nesrine MELAHI — MIAGE, Université Paris Nanterre
Module : Théorie des Graphes & OpenData
Enseignant : François Delbot
Année : 2025-2026
