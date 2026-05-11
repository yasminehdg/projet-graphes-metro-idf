"""
=======================================================
  PROJET GRAPHES & OPENDATA — Réseau Métro & RER IDF
  Génération des graphes animés avec Pyvis
=======================================================
  Avant de lancer : pip install pyvis networkx pandas
  Lancer : python generer_graphes.py
  Résultat : 3 fichiers HTML s'ouvrent automatiquement
"""

import pandas as pd
import networkx as nx
from pyvis.network import Network
import webbrowser
import os

# ============================================================
# ETAPE 1 — Chargement des données
# ============================================================

print("=" * 55)
print("  GENERATION DES GRAPHES ANIME — METRO & RER IDF")
print("=" * 55)

# MODIFIE CE CHEMIN si ton fichier n'est pas dans le même dossier
CHEMIN_CSV = r'metro_rer_idf.csv'

print(f"\n[1/4] Chargement des données : {CHEMIN_CSV}")
df = pd.read_csv(CHEMIN_CSV)

def get_ligne_nom(ligne):
    parts = ligne.split()
    if parts[-1].isdigit():
        return ' '.join(parts[:-1])
    return ligne

df['ligne_nom'] = df['ligne'].apply(get_ligne_nom)
print(f"      OK — {len(df)} lignes chargées")

# ============================================================
# ETAPE 2 — Construction du graphe NetworkX
# ============================================================

print("\n[2/4] Construction du graphe G = (V, E)...")

G = nx.Graph()
coords = {}
for _, row in df.iterrows():
    nom = row['station']
    if nom not in coords:
        coords[nom] = (row['latitude'], row['longitude'])

for station, (lat, lon) in coords.items():
    G.add_node(station, latitude=lat, longitude=lon)

for ligne_id in df['ligne'].unique():
    sous_df = df[df['ligne'] == ligne_id].sort_values('ordre')
    stations = sous_df['station'].tolist()
    ligne_nom = get_ligne_nom(ligne_id)
    for i in range(len(stations) - 1):
        s1, s2 = stations[i], stations[i+1]
        if not G.has_edge(s1, s2):
            G.add_edge(s1, s2, ligne=ligne_nom)

degrees = dict(G.degree())
print(f"      OK — {G.number_of_nodes()} sommets, {G.number_of_edges()} aretes")

# Couleurs officielles des lignes
COULEURS = {
    'RER A': '#E3051B',
    'RER B': '#4E9BD4',
    'RER C': '#FFCD00',
    'RER D': '#00814F',
    'RER E': '#A0006E',
    'METRO': '#4488FF',
    'METRO 7': '#FA9ABA',
    'METRO 7BIS': '#83C491',
    'METRO 10': '#E3B32A',
    'METRO 13': '#98D4E2',
    'METRO 3BIS': '#98D4E2',
}

print("\n[3/4] Génération des 3 graphes animés...")

# ============================================================
# GRAPHE 1 — Réseau complet animé (571 stations)
# ============================================================

print("\n  --> Graphe 1 : Réseau complet (571 stations)...")

net1 = Network(
    height='800px',
    width='100%',
    bgcolor='#07090f',
    font_color='white',
    notebook=False,
    heading='Réseau complet Métro & RER — Île-de-France'
)

net1.set_options("""
{
  "physics": {
    "enabled": true,
    "barnesHut": {
      "gravitationalConstant": -8000,
      "centralGravity": 0.3,
      "springLength": 95,
      "springConstant": 0.04,
      "damping": 0.09
    },
    "stabilization": {
      "enabled": true,
      "iterations": 200,
      "updateInterval": 10
    }
  },
  "nodes": {
    "shape": "dot",
    "font": {"size": 10, "color": "white"},
    "borderWidth": 1.5,
    "shadow": {
      "enabled": true,
      "color": "rgba(0,0,0,0.7)",
      "size": 10
    }
  },
  "edges": {
    "width": 1.5,
    "shadow": true,
    "smooth": {"type": "continuous"}
  },
  "interaction": {
    "hover": true,
    "tooltipDelay": 100,
    "navigationButtons": true,
    "keyboard": true,
    "zoomView": true
  }
}
""")

for station in G.nodes():
    lignes_station = df[df['station'] == station]['ligne_nom'].unique().tolist()
    premiere_ligne = lignes_station[0] if lignes_station else ''
    couleur = COULEURS.get(premiere_ligne, '#888888')
    deg = degrees[station]
    taille = max(8, deg * 5)
    # Label visible seulement pour les grandes stations
    label = station if deg >= 4 else ''
    tooltip = (
        f"<b>{station}</b><br>"
        f"Lignes : {', '.join(lignes_station)}<br>"
        f"Degré : {deg}"
    )
    net1.add_node(
        station,
        label=label,
        title=tooltip,
        color=couleur,
        size=taille,
        borderWidth=2 if deg >= 5 else 1,
        borderWidthSelected=4
    )

for s1, s2, data in G.edges(data=True):
    ligne = data.get('ligne', '')
    couleur_arete = COULEURS.get(ligne, '#444444')
    net1.add_edge(s1, s2, color=couleur_arete, title=ligne)

fichier1 = 'graphe_reseau_complet.html'
net1.save_graph(fichier1)
print(f"      OK — fichier '{fichier1}' créé")

# ============================================================
# GRAPHE 2 — Stations importantes (correspondances)
# ============================================================

print("\n  --> Graphe 2 : Stations avec correspondances (degré >= 3)...")

net2 = Network(
    height='800px',
    width='100%',
    bgcolor='#0a0a1a',
    font_color='white',
    notebook=False,
    heading='Stations stratégiques — Correspondances Métro & RER'
)

net2.set_options("""
{
  "physics": {
    "enabled": true,
    "forceAtlas2Based": {
      "gravitationalConstant": -50,
      "centralGravity": 0.01,
      "springLength": 120,
      "springConstant": 0.08,
      "damping": 0.4
    },
    "solver": "forceAtlas2Based",
    "stabilization": {
      "enabled": true,
      "iterations": 200
    }
  },
  "nodes": {
    "shape": "dot",
    "font": {"size": 14, "color": "white", "bold": true},
    "shadow": {
      "enabled": true,
      "color": "rgba(0,0,0,0.8)",
      "size": 15
    }
  },
  "edges": {
    "width": 2.5,
    "shadow": true,
    "smooth": {"type": "dynamic"}
  },
  "interaction": {
    "hover": true,
    "navigationButtons": true,
    "keyboard": true
  }
}
""")

# Filtrer stations avec degré >= 3
stations_imp = [s for s, d in degrees.items() if d >= 3]
G_imp = G.subgraph(stations_imp)

for station in G_imp.nodes():
    lignes_station = df[df['station'] == station]['ligne_nom'].unique().tolist()
    premiere_ligne = lignes_station[0] if lignes_station else ''
    couleur = COULEURS.get(premiere_ligne, '#888888')
    deg = degrees[station]
    taille = max(15, deg * 8)
    tooltip = (
        f"<b>{station}</b><br>"
        f"Lignes : {', '.join(lignes_station)}<br>"
        f"Degré : {deg}"
    )
    net2.add_node(
        station,
        label=station,
        title=tooltip,
        color={
            'background': couleur,
            'border': 'white',
            'highlight': {'background': '#ffcd00', 'border': 'white'}
        },
        size=taille,
        font={'size': max(11, deg * 2), 'color': 'white'}
    )

for s1, s2, data in G_imp.edges(data=True):
    ligne = data.get('ligne', '')
    couleur_arete = COULEURS.get(ligne, '#444444')
    net2.add_edge(
        s1, s2,
        color={'color': couleur_arete, 'opacity': 0.75},
        title=ligne,
        width=2.5
    )

fichier2 = 'graphe_correspondances.html'
net2.save_graph(fichier2)
print(f"      OK — fichier '{fichier2}' créé")

# ============================================================
# GRAPHE 3 — RER uniquement
# ============================================================

print("\n  --> Graphe 3 : Réseau RER uniquement (5 lignes)...")

net3 = Network(
    height='800px',
    width='100%',
    bgcolor='#050510',
    font_color='white',
    notebook=False,
    heading='Réseau RER — Île-de-France (Lignes A B C D E)'
)

net3.set_options("""
{
  "physics": {
    "enabled": true,
    "repulsion": {
      "centralGravity": 0.2,
      "springLength": 200,
      "springConstant": 0.05,
      "nodeDistance": 100,
      "damping": 0.09
    },
    "solver": "repulsion",
    "stabilization": {"iterations": 150}
  },
  "nodes": {
    "shape": "dot",
    "font": {"size": 12, "color": "white"},
    "shadow": true
  },
  "edges": {
    "width": 3,
    "shadow": true,
    "smooth": {"type": "continuous"}
  },
  "interaction": {
    "hover": true,
    "navigationButtons": true,
    "keyboard": true
  }
}
""")

# Filtrer RER uniquement
rer_lignes = ['RER A', 'RER B', 'RER C', 'RER D', 'RER E']
rer_edges = [
    (s1, s2, d) for s1, s2, d in G.edges(data=True)
    if d.get('ligne', '') in rer_lignes
]
rer_stations = set()
for s1, s2, _ in rer_edges:
    rer_stations.add(s1)
    rer_stations.add(s2)

for station in rer_stations:
    lignes_station = df[df['station'] == station]['ligne_nom'].unique().tolist()
    rer_lignes_station = [l for l in lignes_station if l in rer_lignes]
    premiere = rer_lignes_station[0] if rer_lignes_station else ''
    couleur = COULEURS.get(premiere, '#888888')
    deg = G.degree(station)
    taille = max(10, deg * 6)
    tooltip = (
        f"<b>{station}</b><br>"
        f"Lignes RER : {', '.join(rer_lignes_station)}<br>"
        f"Degré : {deg}"
    )
    net3.add_node(
        station,
        label=station if deg >= 3 else '',
        title=tooltip,
        color=couleur,
        size=taille
    )

for s1, s2, data in rer_edges:
    ligne = data.get('ligne', '')
    couleur_arete = COULEURS.get(ligne, '#555555')
    net3.add_edge(s1, s2, color=couleur_arete, width=3, title=ligne)

fichier3 = 'graphe_rer.html'
net3.save_graph(fichier3)
print(f"      OK — fichier '{fichier3}' créé")

# ============================================================
# ETAPE 4 — Ouvrir automatiquement dans le navigateur
# ============================================================

print("\n[4/4] Ouverture dans le navigateur...")

for f in [fichier1, fichier2, fichier3]:
    chemin_abs = os.path.abspath(f)
    webbrowser.open(f'file:///{chemin_abs}')
    print(f"      Ouvert : {f}")

print("\n" + "=" * 55)
print("  TERMINE ! 3 fichiers HTML créés dans ton dossier :")
print(f"  1. {fichier1}  — Réseau complet animé")
print(f"  2. {fichier2} — Stations avec correspondances")
print(f"  3. {fichier3}              — Réseau RER")
print("\n  Les graphes s'animent automatiquement à l'ouverture.")
print("  Tu peux : zoomer, déplacer les noeuds, cliquer dessus.")
print("=" * 55)
