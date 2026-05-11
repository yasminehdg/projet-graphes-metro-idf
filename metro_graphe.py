import pandas as pd
import networkx as nx
import folium
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CHARGEMENT DES DONNEES
# ============================================================

df = pd.read_csv(r'C:\Users\yasmi\Desktop\Open Da\metro_rer_idf.csv')

def get_ligne_nom(ligne):
    parts = ligne.split()
    if parts[-1].isdigit():
        return ' '.join(parts[:-1])
    return ligne

df['ligne_nom'] = df['ligne'].apply(get_ligne_nom)

COULEURS = {
    'RER A': '#E3051B', 'RER B': '#4E9BD4', 'RER C': '#FFCD00',
    'RER D': '#00814F', 'RER E': '#A0006E',
    'METRO': '#003DA5', 'METRO 7': '#FA9ABA', 'METRO 7BIS': '#83C491',
    'METRO 10': '#E3B32A', 'METRO 13': '#98D4E2', 'METRO 3BIS': '#98D4E2',
}

# ============================================================
# CONSTRUCTION DU GRAPHE
# ============================================================

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

# ============================================================
# STATISTIQUES
# ============================================================

degrees = dict(G.degree())
deg_sorted = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
avg_deg = sum(degrees.values()) / len(degrees)
terminales = [s for s, d in degrees.items() if d == 1]

print("=" * 55)
print("   STATISTIQUES DU GRAPHE - RESEAU METRO/RER IDF")
print("=" * 55)
print(f"Nombre de sommets (stations)  : {G.number_of_nodes()}")
print(f"Nombre d'aretes (connexions)  : {G.number_of_edges()}")
print(f"Graphe connexe                : {'Oui' if nx.is_connected(G) else 'Non'}")
print(f"Composantes connexes          : {nx.number_connected_components(G)}")
print(f"Degre moyen                   : {avg_deg:.2f}")
print(f"Degre maximum                 : {deg_sorted[0][1]} ({deg_sorted[0][0]})")
print(f"Stations terminales (degre 1) : {len(terminales)}")

print("\nTOP 10 stations les plus connectees :")
for station, deg in deg_sorted[:10]:
    print(f"  {station:<40} degre={deg}")

# ============================================================
# PLUS COURTS CHEMINS
# ============================================================

print("\n" + "=" * 55)
print("   PLUS COURTS CHEMINS")
print("=" * 55)

def trouver_station(mot_cle):
    for n in G.nodes():
        if mot_cle.lower() in n.lower():
            return n
    return None

paires = [
    ("telet - Les Hall", "Orly"),
    ("Cergy le Haut", "Marne la Vall"),
    ("Saint-Denis Universit", "Boissy Saint"),
]

for mot1, mot2 in paires:
    s1 = trouver_station(mot1)
    s2 = trouver_station(mot2)
    if s1 and s2:
        chemin = nx.shortest_path(G, s1, s2)
        lg = len(chemin) - 1
        print(f"\nDe '{s1}' a '{s2}'")
        print(f"  Nb d'aretes traversees : {lg}")
        print(f"  Chemin : {' -> '.join(chemin)}")

# ============================================================
# SIMULATION DE PERTURBATION
# ============================================================

print("\n" + "=" * 55)
print("   SIMULATION DE PERTURBATION")
print("=" * 55)

station_fermee = "Saint-Lazare"
G2 = G.copy()
G2.remove_node(station_fermee)
print(f"Fermeture de '{station_fermee}'")
print(f"Graphe connexe apres : {'Oui' if nx.is_connected(G2) else 'Non'}")
print(f"Composantes connexes : {nx.number_connected_components(G2)}")

chatelet = trouver_station("telet - Les Hall")
if chatelet:
    G3 = G.copy()
    G3.remove_node(chatelet)
    print(f"\nFermeture de '{chatelet}'")
    print(f"Graphe connexe apres : {'Oui' if nx.is_connected(G3) else 'Non'}")
    print(f"Composantes connexes : {nx.number_connected_components(G3)}")
    sizes = sorted([len(c) for c in nx.connected_components(G3)], reverse=True)
    print(f"Tailles composantes  : {sizes[:5]}")

# ============================================================
# CENTRALITE
# ============================================================

print("\n" + "=" * 55)
print("   CENTRALITE D'INTERMEDIARTE (Top 10)")
print("=" * 55)

composante = max(nx.connected_components(G), key=len)
G_sub = G.subgraph(composante)
betweenness = nx.betweenness_centrality(G_sub)
top_between = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:10]
for s, v in top_between:
    print(f"  {s:<40} {v:.4f}")

# ============================================================
# GRAPHIQUE STATISTIQUES
# ============================================================

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.patch.set_facecolor('#0f1117')

ax1 = axes[0]
ax1.set_facecolor('#1a1d27')
deg_values = list(degrees.values())
counts = {}
for d in deg_values:
    counts[d] = counts.get(d, 0) + 1
ax1.bar(list(counts.keys()), list(counts.values()), color='#E3051B', edgecolor='white', linewidth=0.5)
ax1.set_title("Distribution des degres des stations", color='white', fontsize=13, pad=12)
ax1.set_xlabel("Degre", color='white')
ax1.set_ylabel("Nombre de stations", color='white')
ax1.tick_params(colors='white')

ax2 = axes[1]
ax2.set_facecolor('#1a1d27')
noms = [s[:22]+"..." if len(s) > 22 else s for s, _ in top_between]
vals = [v for _, v in top_between]
ax2.barh(noms[::-1], vals[::-1], color='#4E9BD4', edgecolor='white', linewidth=0.5)
ax2.set_title("Top 10 - Centralite d'intermediarte", color='white', fontsize=13, pad=12)
ax2.set_xlabel("Score de centralite", color='white')
ax2.tick_params(colors='white')

plt.tight_layout(pad=3)
plt.savefig(r'C:\Users\yasmi\Desktop\Open Da\graphique_stats.png', dpi=150,
            bbox_inches='tight', facecolor='#0f1117')
plt.close()
print("\nGraphique stats sauvegarde !")

# ============================================================
# VISUALISATION GEOGRAPHIQUE DU GRAPHE
# ============================================================

fig2, ax = plt.subplots(figsize=(16, 14))
fig2.patch.set_facecolor('#0f1117')
ax.set_facecolor('#0f1117')

pos = {station: (lon, lat) for station, (lat, lon) in coords.items()}

for s1, s2, data in G.edges(data=True):
    ligne = data.get('ligne', '')
    couleur = COULEURS.get(ligne, '#555555')
    x1, y1 = pos[s1]
    x2, y2 = pos[s2]
    ax.plot([x1, x2], [y1, y2], color=couleur, linewidth=0.8, alpha=0.6, zorder=1)

xs = [pos[n][0] for n in G.nodes()]
ys = [pos[n][1] for n in G.nodes()]
node_colors = []
node_sizes = []
for station in G.nodes():
    lignes_station = df[df['station'] == station]['ligne_nom'].unique()
    premiere = lignes_station[0] if len(lignes_station) > 0 else ''
    node_colors.append(COULEURS.get(premiere, '#aaaaaa'))
    deg = degrees.get(station, 1)
    node_sizes.append(max(10, deg * 8))

ax.scatter(xs, ys, c=node_colors, s=node_sizes, zorder=2,
           linewidths=0.3, edgecolors='white', alpha=0.95)

for station, deg in deg_sorted[:12]:
    x, y = pos[station]
    ax.annotate(station, (x, y), fontsize=5.5, color='white', alpha=0.9,
                xytext=(3, 3), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#222', alpha=0.6, edgecolor='none'))

patches = [mpatches.Patch(color=COULEURS.get(l, '#888'), label=l)
           for l in ['RER A', 'RER B', 'RER C', 'RER D', 'RER E', 'METRO']]
ax.legend(handles=patches, loc='lower left', fontsize=8,
          facecolor='#1a1d27', edgecolor='#444', labelcolor='white',
          title='Lignes', title_fontsize=8)

ax.set_title("Graphe du Reseau Metro & RER - Ile-de-France", color='white', fontsize=14, pad=15)
ax.set_xlabel("Longitude", color='#aaa', fontsize=9)
ax.set_ylabel("Latitude", color='#aaa', fontsize=9)
ax.tick_params(colors='#aaa')
plt.tight_layout()
plt.savefig(r'C:\Users\yasmi\Desktop\Open Da\graphe_visualisation.png', dpi=150,
            bbox_inches='tight', facecolor='#0f1117')
plt.close()
print("Graphe visualisation sauvegarde !")

# ============================================================
# CARTE INTERACTIVE
# ============================================================

carte = folium.Map(location=[48.856, 2.347], zoom_start=11, tiles='CartoDB dark_matter')

for s1, s2, data in G.edges(data=True):
    lat1, lon1 = coords[s1]
    lat2, lon2 = coords[s2]
    ligne = data.get('ligne', '')
    couleur = COULEURS.get(ligne, '#888888')
    folium.PolyLine(
        [(lat1, lon1), (lat2, lon2)],
        color=couleur, weight=2.5, opacity=0.8,
        tooltip=f"{ligne}: {s1} <-> {s2}"
    ).add_to(carte)

for station, (lat, lon) in coords.items():
    lignes_station = df[df['station'] == station]['ligne_nom'].unique()
    lignes_str = ', '.join(lignes_station)
    deg = degrees.get(station, 0)
    rayon = min(3 + deg * 0.5, 10)
    premiere = lignes_station[0] if len(lignes_station) > 0 else ''
    couleur = COULEURS.get(premiere, '#aaaaaa')
    folium.CircleMarker(
        location=[lat, lon], radius=rayon,
        color='white' if deg >= 5 else couleur,
        weight=1.5 if deg >= 5 else 1,
        fill=True, fill_color=couleur, fill_opacity=1,
        tooltip=f"<b>{station}</b><br>Lignes: {lignes_str}<br>Degre: {deg}",
        popup=folium.Popup(f"<b>{station}</b><br>Lignes: {lignes_str}<br>Degre: {deg}", max_width=220)
    ).add_to(carte)

carte.save(r'C:\Users\yasmi\Desktop\Open Da\carte_interactive.html')
print("Carte interactive sauvegardee !")

print("\n========================================")
print("   PROJET TERMINE AVEC SUCCES !")
print("   Fichiers generes dans Open Da :")
print("   - graphique_stats.png")
print("   - graphe_visualisation.png")
print("   - carte_interactive.html")
print("========================================")