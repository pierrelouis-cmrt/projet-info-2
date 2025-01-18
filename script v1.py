import os
import matplotlib.pyplot as plt

#---------------------------------------
# 1) Lecture du fichier de configuration et stockage des informations des cartes 
#---------------------------------------

def lire_fichier_config(fichier):
    """
    Lit le fichier de configuration et retourne un dictionnaire
    { '1': [(x,y), largeur, hauteur, couleur], '2': [...], ... }
    """
    dictionnaire_formes = {}
    with open(fichier, 'r') as f:
        for ligne in f:
            elements = ligne.strip().split(';')
            if len(elements) < 5:
                continue
            indice = elements[0]
            point_depart = eval(elements[1])  # Convertit le texte '[x,y]' en tuple
            largeur = int(elements[2])
            hauteur = int(elements[3])
            couleur = elements[4]
            dictionnaire_formes[indice] = [point_depart, largeur, hauteur, couleur]
    return dictionnaire_formes

#---------------------------------------
# 2) Calcul des coordonnées d'une forme
#---------------------------------------

def compute_shape_coords(data):
    """
    À partir des informations d'une forme, calcule les coordonnées des sommets du rectangle.
    """
    (x, y), largeur, hauteur, couleur = data
    coords = [(x, y), (x + largeur, y), (x + largeur, y + hauteur), (x, y + hauteur)]
    return coords

#---------------------------------------
# 3) Création des fichiers CSV pour chaque forme et mise à jour du dictionnaire
#---------------------------------------

def create_shape_files(formes):
    """
    Parcourt le dictionnaire des formes, crée un fichier CSV pour chaque forme
    dans le dossier 'rectangles' au format spécifié, et remplace la valeur 
    associée à chaque clé par le chemin du fichier créé.
    Affiche le dictionnaire avant et après la création des fichiers.
    """
    print("Dictionnaire avant création des fichiers :")
    print(formes)

    dossier = "rectangles"
    os.makedirs(dossier, exist_ok=True)

    for key in list(formes.keys()):
        data = formes[key]
        coords = compute_shape_coords(data)
        couleur = data[3]
        filename = os.path.join(dossier, f"figure_{key}.csv")
        with open(filename, 'w') as f:
            f.write(f"{couleur};\n")
            for pt in coords:
                f.write(f"{pt};\n")
        formes[key] = filename

    print("\nDictionnaire après création des fichiers :")
    print(formes)

#---------------------------------------
# 4) Fonction pour tracer et remplir un rectangle
#---------------------------------------

def tracer_rectangle(ax, x, y, largeur, hauteur, facecolor='black', edgecolor='white', linewidth=1):
    """
    Trace le contour d'un rectangle sur l'axes `ax` et remplit son intérieur.
    """
    # Calcul des limites
    x_min, x_max = x, x + largeur
    y_min, y_max = y, y + hauteur

    # Coordonnées pour tracer le contour du rectangle
    x_coords = [x_min, x_max, x_max, x_min, x_min]
    y_coords = [y_min, y_min, y_max, y_max, y_min]

    # Tracer le contour
    ax.plot(x_coords, y_coords, color=edgecolor, linewidth=linewidth)

    # Remplir l'intérieur
    poly = ax.fill(x_coords, y_coords, facecolor=facecolor, edgecolor=edgecolor, linewidth=linewidth)[0]

    return poly

#---------------------------------------
# Variables globales pour le jeu
#---------------------------------------

cards = []
clicked_cards = []
pairs_found = 0
disable_clicks = False
total_pairs = None
fig = None
ax = None

#---------------------------------------
# 5) Configuration initiale du plateau de jeu
#---------------------------------------

def setup_board(formes):
    """
    Initialise le plateau de jeu avec les rectangles cachés.
    """
    global cards, fig, ax, total_pairs, clicked_cards, pairs_found, disable_clicks

    clicked_cards = []
    pairs_found = 0
    disable_clicks = False
    cards = []

    fig, ax = plt.subplots()
    plt.title("Jeu de mémoire")
    ax.set_axis_off()

    for key, data in formes.items():
        (x, y), largeur, hauteur, couleur = data
        
        # Dessiner le rectangle initial (face cachée en noir)
        poly = tracer_rectangle(ax, x, y, largeur, hauteur, facecolor='black', edgecolor='white', linewidth=1)

        card_info = {
            'id': key,
            'x': x,
            'y': y,
            'width': largeur,
            'height': hauteur,
            'true_color': couleur,
            'face_color': 'black',
            'is_revealed': False,
            'patch': poly
        }
        cards.append(card_info)

    ax.set_aspect('equal', adjustable='box')
    ax.autoscale_view()

    total_pairs = len(cards) // 2

#---------------------------------------
# 6) Gestion des événements et interaction
#---------------------------------------

def connect_events():
    """
    Connecte l'événement de clic sur la figure à la fonction on_click.
    """
    fig.canvas.mpl_connect('button_press_event', on_click)

def on_click(event):
    """
    Gère le clic de l'utilisateur sur la figure pour révéler ou cacher les cartes.
    """
    global disable_clicks, clicked_cards, pairs_found

    if disable_clicks or event.xdata is None or event.ydata is None:
        return

    for card in cards:
        if (card['x'] <= event.xdata <= card['x'] + card['width'] and
            card['y'] <= event.ydata <= card['y'] + card['height']):
            if not card['is_revealed']:
                reveal_card(card)
                clicked_cards.append(card)

                if len(clicked_cards) == 2:
                    card1, card2 = clicked_cards
                    if card1['true_color'] == card2['true_color']:
                        pairs_found += 1
                        clicked_cards = []
                        print(f"Correspondance ! Paires trouvées : {pairs_found}/{total_pairs}")
                        if pairs_found == total_pairs:
                            print("Vous avez trouvé toutes les paires ! Fin du jeu !")
                    else:
                        disable_clicks = True
                        plt.pause(1.5)
                        hide_card(card1)
                        hide_card(card2)
                        clicked_cards = []
                        disable_clicks = False
            break
    fig.canvas.draw()

def reveal_card(card):
    """
    Révèle une carte en changeant sa couleur.
    """
    card['is_revealed'] = True
    card['face_color'] = card['true_color']
    card['patch'].set_facecolor(card['true_color'])

def hide_card(card):
    """
    Cache une carte en restaurant sa couleur noire.
    """
    card['is_revealed'] = False
    card['face_color'] = 'black'
    card['patch'].set_facecolor('black')

#---------------------------------------
# Exécution du script principal
#---------------------------------------

# Lecture de la configuration
fichier_config = "config.txt"
formes_initiales = lire_fichier_config(fichier_config)

# Création des fichiers CSV et mise à jour du dictionnaire pour les formes
formes_for_files = formes_initiales.copy()
create_shape_files(formes_for_files)

# Mise en place et affichage du jeu de mémoire
setup_board(formes_initiales)
connect_events()
plt.show()
