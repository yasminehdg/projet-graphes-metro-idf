"""
=====================================================================
  PROJET GRAPHES & OPENDATA - Réseau Métro & RER IDF
  4 Graphes utiles et informatifs avec Pyvis
=====================================================================
  Installation : pip install pyvis networkx pandas
  Lancer       : python graphes_utiles.py
  Résultat     : 4 fichiers HTML qui s'ouvrent automatiquement
=====================================================================

  Graphe 1 - Carte de chaleur : stations les plus surchargées
  Graphe 2 - Vulnérabilité    : points d'articulation en rouge
  Graphe 3 - Perturbation     : avant/après fermeture Saint-Lazare
  Graphe 4 - Plus court chemin: trajet visualisé sur le graphe
"""

import pandas as pd
import networkx as nx
from pyvis.network import Network
from collections import deque
import webbrowser
import os

# ============================================================
# CHARGEMENT ET CONSTRUCTION DU GRAPHE
# ============================================================

print("=" * 60)
print("  4 GRAPHES INFORMATIFS - METRO & RER IDF")
print("=" * 60)

CHEMIN_CSV = r'metro_rer_idf.csv'  # modifie si besoin

print("\n[1/5] Chargement des données...")
df = pd.read_csv(CHEMIN_CSV)

def get_ligne_nom(ligne):
    parts = ligne.split()
    if parts[-1].isdigit():
        return ' '.join(parts[:-1])
    return ligne

df['ligne_nom'] = df['ligne'].apply(get_ligne_nom)

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
            lat1, lon1 = coords[s1]
            lat2, lon2 = coords[s2]
            dist = ((lat2 - lat1)**2 + (lon2 - lon1)**2)**0.5 * 111
            G.add_edge(s1, s2, ligne=ligne_nom, poids=round(dist, 3))

degrees = dict(G.degree())
max_deg = max(degrees.values())

print(f"      OK - {G.number_of_nodes()} sommets, {G.number_of_edges()} aretes")

print("\n[2/5] Calcul des points d'articulation (peut prendre 10s)...")
articulations = set(nx.articulation_points(G))
print(f"      OK - {len(articulations)} points d'articulation détectés")

COULEURS = {
    'RER A': '#E3051B', 'RER B': '#4E9BD4', 'RER C': '#FFCD00',
    'RER D': '#00814F', 'RER E': '#A0006E', 'METRO': '#4488FF',
    'METRO 7': '#FA9ABA', 'METRO 7BIS': '#83C491',
    'METRO 10': '#E3B32A', 'METRO 13': '#98D4E2', 'METRO 3BIS': '#98D4E2',
}

def get_couleur_station(station):
    lignes = df[df['station'] == station]['ligne_nom'].unique().tolist()
    return COULEURS.get(lignes[0] if lignes else '', '#888888')

def get_lignes_station(station):
    return df[df['station'] == station]['ligne_nom'].unique().tolist()

def bfs_chemin(start, end):
    visited = {start}
    q = deque([[start]])
    while q:
        path = q.popleft()
        if path[-1] == end:
            return path
        for nb in G.neighbors(path[-1]):
            if nb not in visited:
                visited.add(nb)
                q.append(path + [nb])
    return None

print("\n[3/5] Génération des 4 graphes...")

OPTS_BASE = """
{
  "physics": {
    "enabled": true,
    "barnesHut": {
      "gravitationalConstant": -8000,
      "centralGravity": 0.3,
      "springLength": 100,
      "springConstant": 0.04,
      "damping": 0.09
    },
    "stabilization": {"enabled": true, "iterations": 200}
  },
  "nodes": {
    "shape": "dot",
    "shadow": true,
    "font": {"color": "white", "size": 11}
  },
  "edges": {
    "shadow": true,
    "smooth": {"type": "continuous"}
  },
  "interaction": {
    "hover": true,
    "navigationButtons": true,
    "keyboard": true
  }
}
"""

# ============================================================
# GRAPHE 1 - CARTE DE CHALEUR
# Info : quelles stations sont les plus surchargées ?
# Taille du noeud = degré, couleur = intensité de charge
# ============================================================

print("\n  --> Graphe 1 : Carte de chaleur des stations...")

net1 = Network(
    height='820px', width='100%',
    bgcolor='#07090f', font_color='white',
    notebook=False,
    heading='[CHALEUR] Carte de Chaleur - Stations les plus surchargées du réseau'
)
net1.set_options(OPTS_BASE)

def degre_vers_couleur(deg, max_d):
    """Rouge si très chargé, vert si peu chargé"""
    ratio = deg / max_d
    if ratio >= 0.7:
        return '#E3051B'   # rouge foncé = très chargé
    elif ratio >= 0.5:
        return '#FF6600'   # orange = chargé
    elif ratio >= 0.3:
        return '#FFCD00'   # jaune = moyen
    elif ratio >= 0.15:
        return '#88CC44'   # vert clair = peu chargé
    else:
        return '#224422'   # vert foncé = faible

for station in G.nodes():
    deg = degrees[station]
    lignes = get_lignes_station(station)
    couleur = degre_vers_couleur(deg, max_deg)
    taille = max(6, deg * 6)
    label = station if deg >= 4 else ''
    tooltip = (
        f"<b>{station}</b><br>"
        f"[CHALEUR] Degré (charge) : <b>{deg}</b><br>"
        f"Lignes : {', '.join(lignes)}<br>"
        f"{'[ATTENTION] Station très chargée !' if deg >= 6 else '[OK] Station normale'}"
    )
    net1.add_node(
        station,
        label=label,
        title=tooltip,
        color=couleur,
        size=taille,
        borderWidth=3 if deg >= 6 else 1,
        borderWidthSelected=5
    )

for s1, s2, data in G.edges(data=True):
    ligne = data.get('ligne', '')
    deg_moy = (degrees[s1] + degrees[s2]) / 2
    couleur_arete = degre_vers_couleur(deg_moy, max_deg)
    net1.add_edge(s1, s2, color=couleur_arete, width=1.5, title=ligne)

# Légende dans le titre
net1.html = net1.html if hasattr(net1, 'html') else ''

f1 = 'graphe1_carte_chaleur.html'
net1.save_graph(f1)

# Ajouter légende
with open(f1, 'r', encoding='cp1252', errors='replace') as file:
    content = file.read()

legende = """
<div style="position:fixed;top:15px;left:15px;background:rgba(7,9,15,0.92);
border:1px solid #1e3554;border-radius:10px;padding:16px 20px;z-index:9999;
font-family:Arial;color:white;min-width:220px;">
  <div style="font-size:1rem;font-weight:800;margin-bottom:12px;color:#ffcd00">
    [CHALEUR] Carte de Chaleur du Réseau
  </div>
  <div style="font-size:.75rem;color:#aaa;margin-bottom:10px">
    Taille & couleur = degré de la station<br>(nombre de connexions directes)
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
    <div style="width:14px;height:14px;border-radius:50%;background:#E3051B"></div>
    <span style="font-size:.72rem">Très chargée (deg >= 7)</span>
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
    <div style="width:12px;height:12px;border-radius:50%;background:#FF6600"></div>
    <span style="font-size:.72rem">Chargée (deg 5-6)</span>
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
    <div style="width:10px;height:10px;border-radius:50%;background:#FFCD00"></div>
    <span style="font-size:.72rem">Moyenne (deg 3-4)</span>
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
    <div style="width:8px;height:8px;border-radius:50%;background:#88CC44"></div>
    <span style="font-size:.72rem">Peu chargée (deg 2)</span>
  </div>
  <div style="display:flex;align-items:center;gap:8px">
    <div style="width:6px;height:6px;border-radius:50%;background:#224422"></div>
    <span style="font-size:.72rem">Faible (deg 1 - terminale)</span>
  </div>
  <div style="margin-top:12px;padding-top:10px;border-top:1px solid #1e3554;font-size:.68rem;color:#aaa">
    [INFO] Cliquez sur un noeud pour ses détails<br>
    [SOURIS] Déplacez, zoomez librement
  </div>
</div>
"""
content = content.replace('<body>', '<body>' + legende)
with open(f1, 'w', encoding='utf-8', errors='replace') as file:
    file.write(content)

print(f"      OK - '{f1}'")

# ============================================================
# GRAPHE 2 - VULNERABILITE (Points d'articulation)
# Info : quelles stations sont critiques pour le réseau ?
# Rouge = critique, vert = normale
# ============================================================

print("\n  --> Graphe 2 : Vulnérabilité du réseau...")

net2 = Network(
    height='820px', width='100%',
    bgcolor='#0a0005', font_color='white',
    notebook=False,
    heading='[ATTENTION] Vulnérabilité du Réseau - Points d\'Articulation Critiques'
)
net2.set_options(OPTS_BASE)

for station in G.nodes():
    deg = degrees[station]
    lignes = get_lignes_station(station)
    est_critique = station in articulations

    if est_critique:
        couleur = '#E3051B'      # rouge = critique
        taille = max(14, deg * 5)
        bordure = '#FF6600'
        epaisseur = 3
        label = station
        tooltip = (
            f"<b>[ATTENTION] STATION CRITIQUE</b><br>"
            f"<b>{station}</b><br>"
            f"Sa fermeture déconnecte le réseau !<br>"
            f"Degré : {deg}<br>"
            f"Lignes : {', '.join(lignes)}"
        )
    else:
        couleur = '#1a5c1a'      # vert foncé = normale
        taille = max(6, deg * 3)
        bordure = '#2a8c2a'
        epaisseur = 1
        label = station if deg >= 5 else ''
        tooltip = (
            f"<b>[OK] Station normale</b><br>"
            f"{station}<br>"
            f"Degré : {deg}<br>"
            f"Lignes : {', '.join(lignes)}"
        )

    net2.add_node(
        station,
        label=label,
        title=tooltip,
        color={'background': couleur, 'border': bordure,
               'highlight': {'background': '#ffcd00', 'border': 'white'}},
        size=taille,
        borderWidth=epaisseur
    )

for s1, s2, data in G.edges(data=True):
    s1_crit = s1 in articulations
    s2_crit = s2 in articulations
    if s1_crit and s2_crit:
        couleur_arete = '#FF4400'
        width = 3
    elif s1_crit or s2_crit:
        couleur_arete = '#FF8800'
        width = 2
    else:
        couleur_arete = '#1a4a1a'
        width = 1
    net2.add_edge(s1, s2, color=couleur_arete, width=width,
                  title=data.get('ligne', ''))

f2 = 'graphe2_vulnerabilite.html'
net2.save_graph(f2)

with open(f2, 'r', encoding='cp1252', errors='replace') as file:
    content = file.read()

legende2 = f"""
<div style="position:fixed;top:15px;left:15px;background:rgba(10,0,5,0.92);
border:1px solid #3a1020;border-radius:10px;padding:16px 20px;z-index:9999;
font-family:Arial;color:white;min-width:240px;">
  <div style="font-size:1rem;font-weight:800;margin-bottom:12px;color:#ffcd00">
    [ATTENTION] Vulnérabilité du Réseau
  </div>
  <div style="font-size:.75rem;color:#aaa;margin-bottom:10px">
    Un <b>point d'articulation</b> est une station dont<br>
    la suppression déconnecte le graphe.
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
    <div style="width:14px;height:14px;border-radius:50%;background:#E3051B"></div>
    <span style="font-size:.72rem"><b>Station CRITIQUE</b> (point d'articulation)</span>
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
    <div style="width:10px;height:10px;border-radius:50%;background:#1a5c1a"></div>
    <span style="font-size:.72rem">Station normale (remplaçable)</span>
  </div>
  <div style="margin-top:10px;padding-top:10px;border-top:1px solid #3a1020;
    font-size:.72rem;color:#ffcd00">
    [STATS] {len(articulations)} stations critiques sur {G.number_of_nodes()}
    ({len(articulations)/G.number_of_nodes()*100:.1f}% du réseau)
  </div>
  <div style="margin-top:6px;font-size:.68rem;color:#aaa">
    [INFO] Cliquez sur un noeud rouge pour voir<br>pourquoi il est critique
  </div>
</div>
"""
content = content.replace('<body>', '<body>' + legende2)
with open(f2, 'w', encoding='utf-8', errors='replace') as file:
    file.write(content)

print(f"      OK - '{f2}'")

# ============================================================
# GRAPHE 3 - AVANT / APRES PERTURBATION
# Info : impact réel de la fermeture de Saint-Lazare
# Gris = station inaccessible après fermeture
# ============================================================

print("\n  --> Graphe 3 : Avant/Après fermeture de Saint-Lazare...")

STATION_FERMEE = 'Saint-Lazare'

# Calculer les stations encore accessibles après fermeture
G_perturbe = G.copy()
G_perturbe.remove_node(STATION_FERMEE)

# BFS depuis une station de référence
station_ref = 'Châtelet - Les Halles'
accessibles = set()
q = deque([station_ref])
visited = {station_ref}
while q:
    n = q.popleft()
    accessibles.add(n)
    for nb in G_perturbe.neighbors(n):
        if nb not in visited:
            visited.add(nb)
            q.append(nb)

inaccessibles = set(G.nodes()) - accessibles - {STATION_FERMEE}

print(f"      Stations inaccessibles après fermeture : {len(inaccessibles)}")

net3 = Network(
    height='820px', width='100%',
    bgcolor='#05050f', font_color='white',
    notebook=False,
    heading=f'[FERME] Simulation : Fermeture de {STATION_FERMEE} - Impact sur le réseau'
)
net3.set_options(OPTS_BASE)

for station in G.nodes():
    deg = degrees[station]
    lignes = get_lignes_station(station)

    if station == STATION_FERMEE:
        couleur = '#E3051B'
        taille = 25
        label = f"[FERME] {station}"
        tooltip = (
            f"<b>[FERME] STATION FERMÉE</b><br>"
            f"<b>{station}</b><br>"
            f"Toutes les connexions sont coupées.<br>"
            f"Degré : {deg} - {deg} arêtes supprimées"
        )
        bordure = '#FF0000'
    elif station in inaccessibles:
        couleur = '#333333'
        taille = max(5, deg * 3)
        label = station if deg >= 5 else ''
        tooltip = (
            f"<b>[NON] Station inaccessible</b><br>"
            f"{station}<br>"
            f"Non joignable depuis le reste du réseau<br>"
            f"après fermeture de {STATION_FERMEE}"
        )
        bordure = '#555555'
    else:
        couleur = get_couleur_station(station)
        taille = max(7, deg * 4)
        label = station if deg >= 5 else ''
        tooltip = (
            f"<b>[OK] Station accessible</b><br>"
            f"{station}<br>"
            f"Lignes : {', '.join(lignes)}<br>"
            f"Degré : {deg}"
        )
        bordure = 'white'

    net3.add_node(
        station,
        label=label,
        title=tooltip,
        color={'background': couleur, 'border': bordure},
        size=taille,
        borderWidth=3 if station == STATION_FERMEE else 1
    )

for s1, s2, data in G.edges(data=True):
    if s1 == STATION_FERMEE or s2 == STATION_FERMEE:
        couleur_arete = '#660000'
        width = 1
        dashes = True
    elif s1 in inaccessibles or s2 in inaccessibles:
        couleur_arete = '#333333'
        width = 1
        dashes = False
    else:
        ligne = data.get('ligne', '')
        couleur_arete = COULEURS.get(ligne, '#444')
        width = 2
        dashes = False

    net3.add_edge(s1, s2, color=couleur_arete, width=width,
                  title=data.get('ligne', ''), dashes=dashes)

f3 = 'graphe3_perturbation.html'
net3.save_graph(f3)

with open(f3, 'r', encoding='cp1252', errors='replace') as file:
    content = file.read()

legende3 = f"""
<div style="position:fixed;top:15px;left:15px;background:rgba(5,5,15,0.92);
border:1px solid #1e3554;border-radius:10px;padding:16px 20px;z-index:9999;
font-family:Arial;color:white;min-width:250px;">
  <div style="font-size:1rem;font-weight:800;margin-bottom:12px;color:#E3051B">
    [FERME] Fermeture de {STATION_FERMEE}
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:7px">
    <div style="width:16px;height:16px;border-radius:50%;background:#E3051B;border:2px solid red"></div>
    <span style="font-size:.72rem"><b>Station fermée</b></span>
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:7px">
    <div style="width:10px;height:10px;border-radius:50%;background:#333333;border:1px solid #555"></div>
    <span style="font-size:.72rem">Station inaccessible ({len(inaccessibles)} stations)</span>
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:7px">
    <div style="width:10px;height:10px;border-radius:50%;background:#4e9bd4"></div>
    <span style="font-size:.72rem">Station encore accessible</span>
  </div>
  <div style="margin-top:10px;padding-top:10px;border-top:1px solid #1e3554;font-size:.72rem">
    <span style="color:#ffcd00">[STATS] Impact :</span><br>
    [OK] Accessibles : <b>{len(accessibles)}</b> stations<br>
    [NON] Inaccessibles : <b>{len(inaccessibles)}</b> stations<br>
    [CONNEXION] Arêtes supprimées : <b>{G.degree(STATION_FERMEE)}</b>
  </div>
</div>
"""
content = content.replace('<body>', '<body>' + legende3)
with open(f3, 'w', encoding='utf-8', errors='replace') as file:
    file.write(content)

print(f"      OK - '{f3}'")

# ============================================================
# GRAPHE 4 - PLUS COURT CHEMIN VISUALISE
# Info : trajet optimal entre deux stations
# Jaune = chemin, gris = reste du réseau
# ============================================================

print("\n  --> Graphe 4 : Plus court chemin visualisé...")

DEPART  = "Châtelet - Les Halles"
ARRIVEE = "Versailles Château Rive Gauche"

chemin = bfs_chemin(DEPART, ARRIVEE)
chemin_set = set(chemin)
chemin_aretes = set()
for i in range(len(chemin) - 1):
    chemin_aretes.add((chemin[i], chemin[i+1]))
    chemin_aretes.add((chemin[i+1], chemin[i]))

print(f"      Chemin trouvé : {len(chemin)-1} arrêts")

net4 = Network(
    height='820px', width='100%',
    bgcolor='#050a05', font_color='white',
    notebook=False,
    heading=f'[CARTE] Plus Court Chemin : {DEPART} -> {ARRIVEE} ({len(chemin)-1} arrêts)'
)
net4.set_options(OPTS_BASE)

for station in G.nodes():
    deg = degrees[station]
    lignes = get_lignes_station(station)

    if station == DEPART:
        couleur = '#00c853'
        taille = 22
        label = f"[DEPART] {station}"
        tooltip = f"<b>[DEPART] DÉPART</b><br>{station}<br>Degré : {deg}"
    elif station == ARRIVEE:
        couleur = '#E3051B'
        taille = 22
        label = f"[ARRIVEE] {station}"
        tooltip = f"<b>[ARRIVEE] ARRIVÉE</b><br>{station}<br>Degré : {deg}"
    elif station in chemin_set:
        # Station intermédiaire du chemin
        pos = chemin.index(station) + 1
        couleur = '#ffcd00'
        taille = 16
        label = station
        tooltip = (
            f"<b>[ETAPE] Étape {pos}/{len(chemin)-1}</b><br>"
            f"{station}<br>"
            f"Lignes : {', '.join(lignes)}<br>"
            f"Degré : {deg}"
        )
    else:
        couleur = '#1a1a2a'
        taille = max(4, deg * 2)
        label = ''
        tooltip = f"{station}<br>Degré : {deg}"

    net4.add_node(
        station,
        label=label,
        title=tooltip,
        color=couleur,
        size=taille,
        borderWidth=3 if station in chemin_set else 1,
        borderWidthSelected=4
    )

for s1, s2, data in G.edges(data=True):
    if (s1, s2) in chemin_aretes:
        couleur_arete = '#ffcd00'
        width = 5
        titre = f"[OK] Sur le chemin optimal\n{data.get('ligne', '')}"
    else:
        couleur_arete = '#1a1a2a'
        width = 1
        titre = data.get('ligne', '')
    net4.add_edge(s1, s2, color=couleur_arete, width=width, title=titre)

f4 = 'graphe4_plus_court_chemin.html'
net4.save_graph(f4)

with open(f4, 'r', encoding='cp1252', errors='replace') as file:
    content = file.read()

legende4 = f"""
<div style="position:fixed;top:15px;left:15px;background:rgba(5,10,5,0.92);
border:1px solid #1e4a1e;border-radius:10px;padding:16px 20px;z-index:9999;
font-family:Arial;color:white;min-width:260px;">
  <div style="font-size:1rem;font-weight:800;margin-bottom:12px;color:#ffcd00">
    [CARTE] Plus Court Chemin (BFS)
  </div>
  <div style="font-size:.73rem;color:#aaa;margin-bottom:10px">
    Algorithme BFS - minimise le nombre d'arrêts
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:7px">
    <div style="width:14px;height:14px;border-radius:50%;background:#00c853"></div>
    <span style="font-size:.72rem"><b>Départ :</b> {DEPART}</span>
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:7px">
    <div style="width:14px;height:14px;border-radius:50%;background:#E3051B"></div>
    <span style="font-size:.72rem"><b>Arrivée :</b> {ARRIVEE}</span>
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:7px">
    <div style="width:12px;height:12px;border-radius:50%;background:#ffcd00"></div>
    <span style="font-size:.72rem">Stations intermédiaires du chemin</span>
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:7px">
    <div style="width:8px;height:8px;border-radius:50%;background:#1a1a2a;border:1px solid #333"></div>
    <span style="font-size:.72rem">Stations non utilisées</span>
  </div>
  <div style="margin-top:10px;padding-top:10px;border-top:1px solid #1e4a1e;font-size:.72rem">
    <span style="color:#ffcd00">[STATS] Résultat :</span><br>
    [STATION] <b>{len(chemin)-1} arrêts</b> pour ce trajet<br>
    [POSITION] <b>{len(chemin)}</b> stations traversées<br>
    [CONNEXION] Chemin élémentaire (sans doublon)
  </div>
  <div style="margin-top:8px;font-size:.68rem;color:#aaa">
    [INFO] Les traits jaunes = le chemin optimal
  </div>
</div>
"""
content = content.replace('<body>', '<body>' + legende4)
with open(f4, 'w', encoding='utf-8', errors='replace') as file:
    file.write(content)

print(f"      OK - '{f4}'")

# ============================================================
# OUVERTURE AUTOMATIQUE
# ============================================================

print("\n[5/5] Ouverture dans le navigateur...")
fichiers = [f1, f2, f3, f4]
for f in fichiers:
    chemin_abs = os.path.abspath(f)
    webbrowser.open(f'file:///{chemin_abs}')
    print(f"      Ouvert : {f}")

print("\n" + "=" * 60)
print("  [OK] 4 GRAPHES GÉNÉRÉS ET OUVERTS !")
print("=" * 60)
print(f"\n  [STATS] Graphe 1 : {f1}")
print( "     -> Carte de chaleur : stations surchargées en rouge")
print(f"\n  [ATTENTION]  Graphe 2 : {f2}")
print( "     -> Vulnérabilité : points d'articulation en rouge")
print(f"\n  [FERME] Graphe 3 : {f3}")
print( "     -> Perturbation Saint-Lazare : stations grises = inaccessibles")
print(f"\n  [CARTE]  Graphe 4 : {f4}")
print(f"     -> Plus court chemin : {DEPART} -> {ARRIVEE}")
print("\n  Dans chaque graphe :")
print("  - Cliquez sur un noeud pour ses infos")
print("  - Zoomez avec la molette")
print("  - Déplacez les noeuds librement")
print("=" * 60)
