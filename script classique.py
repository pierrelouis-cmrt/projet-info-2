import os
import time
import matplotlib.pyplot as plt
from matplotlib import animation
import imageio
import random

plt.close('all')

# ---------------------------------------
# Gif
# ---------------------------------------

def display_gif(ax, filepath):
    frames = imageio.mimread(filepath)
    if not frames:
        print(f"Impossible de lire le GIF à partir de {filepath}")
        return None

    ax.axis('off')
    # Afficher la première image du GIF
    im = ax.imshow(frames[0], zorder=0)

    def update(frame):
        im.set_data(frame)
        return [im]

    # IMPORTANT : blit=False pour que tout (texte, etc.) soit rafraîchi correctement
    ani = animation.FuncAnimation(ax.figure, update, frames=frames, interval=80, blit=False)
    return ani



# ---------------------------------------
# 1) Lecture du fichier de configuration et stockage des informations des cartes 
# ---------------------------------------
def lire_fichier_config(fichier):
    """
    Lit le fichier de configuration, randomise les positions des formes,
    et retourne un dictionnaire { 'indice': [(x,y), largeur, hauteur, couleur], ... }.
    """
    shapes = []
    coordinates = []
    
    # Lecture du fichier et stockage des informations
    with open(fichier, 'r') as f:
        for ligne in f:
            elements = ligne.strip().split(';')
            if len(elements) < 5:
                continue
            indice = elements[0]
            point_depart = eval(elements[1])  # Conversion de "[x,y]" en tuple
            largeur = int(elements[2])
            hauteur = int(elements[3])
            couleur = elements[4]
            
            # Stocker les infos de la forme sans coordonnée, et collecter la coordonnée séparément
            shapes.append((indice, largeur, hauteur, couleur))
            coordinates.append(point_depart)
    
    # Mélanger aléatoirement les coordonnées
    #random.shuffle(coordinates)
    
    # Réattribuer les coordonnées mélangées aux formes
    dictionnaire_formes = {}
    for shape, new_coord in zip(shapes, coordinates):
        indice, largeur, hauteur, couleur = shape
        dictionnaire_formes[indice] = [new_coord, largeur, hauteur, couleur]
    
    return dictionnaire_formes


# ---------------------------------------
# 2) Calcul des coordonnées d'une forme
# ---------------------------------------
def compute_shape_coords(data):
    """
    À partir des informations d'une forme, calcule les coordonnées des sommets du rectangle.
    """
    (x, y), largeur, hauteur, couleur = data
    coords = [(x, y), (x + largeur, y), (x + largeur, y + hauteur), (x, y + hauteur)]
    return coords


# ---------------------------------------
# 3) Création des fichiers CSV pour chaque forme et mise à jour du dictionnaire
# ---------------------------------------
def create_shape_files(formes):
    """
    Parcourt le dictionnaire des formes, crée un fichier CSV pour chaque forme
    dans le dossier 'figures' au format spécifié, et remplace la valeur 
    associée à chaque clé par le chemin du fichier créé.
    Affiche le dictionnaire avant et après la création des fichiers.
    """
    #print("Dictionnaire avant création des fichiers :")
    #print(formes)

    dossier = "figures"
    os.makedirs(dossier, exist_ok=True)

    for key in list(formes.keys()):
        data = formes[key]
        coords = compute_shape_coords(data)
        couleur = data[3]
        filename = os.path.join(dossier, f"rectangle_{key}.csv")
        with open(filename, 'w') as f:
            f.write(f"{couleur};\n")
            for pt in coords:
                f.write(f"{pt};\n")
        formes[key] = filename

    #print("\nDictionnaire après création des fichiers :")
    #print(formes)


# ---------------------------------------
# 4) Fonction pour tracer et remplir un rectangle
# ---------------------------------------
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


# ---------------------------------------
# 5) Gestion du jeu
# ---------------------------------------
def init_game_state():
    """
    Initialise et renvoie le dictionnaire qui stocke l'état global du jeu.
    """
    return {
        'formes': None,
        'cards': [],
        'fig': None,
        'ax': None,
        'clicked_cards': [],
        'pairs_found': 0,
        'total_pairs': 0,
        'player1_score': 0,
        'player2_score': 0,
        'current_player': 1,  # joueur 1 ou 2
        'start_time': 0,
        'disable_clicks': False,
        'score_timer_text': None,
        'timer': None,
        'namep1': None,
        'namep2': None
    }


def setup_board(game_state):
    """
    Configure l'axes (suppression de l'affichage) et crée toutes les cartes (rectangles noirs).
    Calcule aussi le nombre total de paires, puis initialise l'affichage du score/temps.
    """
    ax = game_state['ax']
    ax.set_axis_off()

    for key, data in game_state['formes'].items():
        (x, y), largeur, hauteur, couleur = data
        
        # Dessiner le rectangle initial (face cachée en noir)
        poly = tracer_rectangle(
            ax, x, y, largeur, hauteur, 
            facecolor='black', edgecolor='white', linewidth=1
        )

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
        game_state['cards'].append(card_info)

    ax.set_aspect('equal', adjustable='box')
    ax.autoscale_view()

    # Total de paires (puisqu'il y a 2 cartes par couleur)
    game_state['total_pairs'] = len(game_state['cards']) // 2

    # Préparation d'un texte pour afficher le score et le temps
    game_state['score_timer_text'] = ax.text(
        0.5, 1.02, "", 
        transform=ax.transAxes, ha="center", va="bottom", color="black",
        fontsize=12, fontweight="bold"
    )

    # Mise à jour initiale de l'affichage Score/Timer
    update_score_and_timer(game_state)


def connect_events(game_state):
    """
    Connecte l'événement de clic de souris et met en place un timer
    pour la mise à jour du temps.
    """ 
    fig = game_state['fig']
    cid = fig.canvas.mpl_connect('button_press_event', 
                                 lambda event: on_click(event, game_state))

    # Configuration du timer pour mettre à jour le temps chaque seconde
    game_state['timer'] = fig.canvas.new_timer(interval=1000)
    game_state['timer'].add_callback(lambda: update_score_and_timer(game_state))
    game_state['timer'].start()


def on_click(event, game_state):
    """
    Gère la logique lors d'un clic sur le canevas :
    - Vérifie si on a cliqué sur une carte
    - Retourne la carte si elle est cachée
    - Compare la carte cliquée avec une autre si 2 cartes sont cliquées
    - Met à jour le score et le joueur
    """
    if game_state['disable_clicks'] or event.xdata is None or event.ydata is None:
        return

    for card in game_state['cards']:
        # Vérifier si (xdata, ydata) est à l'intérieur de la zone de la carte
        if (card['x'] <= event.xdata <= card['x'] + card['width'] and
            card['y'] <= event.ydata <= card['y'] + card['height']):
            
            # Si la carte est déjà retournée, on ne fait rien
            if not card['is_revealed']:
                reveal_card(card)
                game_state['clicked_cards'].append(card)

                # Si 2 cartes cliquées, vérifier la correspondance
                if len(game_state['clicked_cards']) == 2:
                    card1, card2 = game_state['clicked_cards']
                    if card1['true_color'] == card2['true_color']:
                        # Paire trouvée
                        game_state['pairs_found'] += 1
                        if game_state['current_player'] == 1:
                            game_state['player1_score'] += 1
                        else:
                            game_state['player2_score'] += 1

                        game_state['clicked_cards'].clear()
                        print(f"Correspondance ! Paires trouvées : {game_state['pairs_found']}/{game_state['total_pairs']}")

                        # Mettre à jour le score/temps
                        update_score_and_timer(game_state)

                        # Si toutes les paires sont trouvées -> fin du jeu
                        if game_state['pairs_found'] == game_state['total_pairs']:
                            print("Vous avez trouvé toutes les paires ! Fin du jeu !")
                            end_game(game_state)
                        else:
                            # Le joueur courant rejoue, on ne change pas de joueur
                            pass
                    else:
                        # Pas de correspondance, on attend 1.5s puis on cache à nouveau
                        game_state['disable_clicks'] = True
                        plt.pause(1.5)
                        hide_card(card1)
                        hide_card(card2)
                        game_state['clicked_cards'].clear()
                        game_state['disable_clicks'] = False

                        # Passer au joueur suivant
                        next_player(game_state)
                        update_score_and_timer(game_state)

            break  # On sort de la boucle une fois la carte trouvée

    game_state['fig'].canvas.draw()


def reveal_card(card):
    """
    Retourne la carte (on affiche sa 'true_color').
    """
    card['is_revealed'] = True
    card['face_color'] = card['true_color']
    card['patch'].set_facecolor(card['true_color'])


def hide_card(card):
    """
    Retourne la carte face cachée (noire).
    """
    card['is_revealed'] = False
    card['face_color'] = 'black'
    card['patch'].set_facecolor('black')


def next_player(game_state):
    """
    Passe au joueur suivant (1 -> 2 ou 2 -> 1).
    """
    if game_state['current_player'] == 1:
        game_state['current_player'] = 2
    else:
        game_state['current_player'] = 1


def update_score_and_timer(game_state):
    """
    Met à jour l'affichage du score et du temps écoulé.
    """
    elapsed_time = int(time.time() - game_state['start_time'])
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    time_str = f"{minutes:02d}:{seconds:02d}"

    # Déterminer le nom du joueur courant
    if game_state['current_player'] == 1:
        name_current = game_state['namep1']
    else:
        name_current = game_state['namep2']

    score_str = (f"{game_state['namep1']} : {game_state['player1_score']}   "
                 f"{game_state['namep2']} : {game_state['player2_score']}   "
                 f"(Tour de {name_current})   "
                 f"Temps : {time_str}")
    
    game_state['score_timer_text'].set_text(score_str)
    game_state['fig'].canvas.draw_idle()


def end_game(game_state):
    # 1) Déterminer winner et loser
    if game_state['player1_score'] >= game_state['player2_score']:
        winner = game_state['namep1']
        loser = game_state['namep2']
    else:
        winner = game_state['namep2']
        loser = game_state['namep1']

    # 2) Stopper le timer, désactiver les clics
    if game_state['timer']:
        game_state['timer'].stop()
    game_state['disable_clicks'] = True

    # 3) Message sur l'axe principal
    game_state['ax'].text(
        0.5, 0.8,
        f"FÉLICITATIONS !\nToutes les paires sont trouvées !\n{winner} a gagné contre {loser}",
        transform=game_state['ax'].transAxes,
        ha="center", va="center",
        fontsize=20, color="black", fontweight="bold"
    )

    # 4) Ajouter l'axe du GIF
    gif_ax = game_state['fig'].add_axes([0.25, 0.1, 0.5, 0.5])
    gif_ax.axis('off')

    gif_path = "gif/i-win-you-lose.gif"
    if not os.path.exists(gif_path):
        print(f"Le fichier GIF n'a pas été trouvé à {gif_path}")
    else:
        ani = display_gif(gif_ax, gif_path)
        if ani is not None:
            game_state['fig']._gif_animation = ani

    # 5) Ajouter le texte par-dessus le GIF, avec un zorder élevé et coordonnées normalisées
    #    (0, 0) = coin bas-gauche de l'axe, (1, 1) = coin haut-droit de l'axe
    gif_ax.text(
        0.65, 0.8,
        f"{winner}",
        transform=gif_ax.transAxes,
        ha="center", va="center",
        fontsize=16, color="black",
        zorder=10
    )
    gif_ax.text(
        0.35, 0.28,
        f"{loser}",
        transform=gif_ax.transAxes,
        ha="center", va="center",
        fontsize=16, color="black",
        zorder=10
    )

    # 6) Forcer la mise à jour
    game_state['fig'].canvas.draw_idle()




# ---------------------------------------
# Exécution du script principal
# ---------------------------------------
if __name__ == "__main__":
    # 1) Lecture de la configuration
    fichier_config = "config.txt"
    formes_initiales = lire_fichier_config(fichier_config)

    # 2) Création des fichiers CSV et mise à jour du dictionnaire pour les formes
    formes_for_files = formes_initiales.copy()
    create_shape_files(formes_for_files)

    # 3) Initialisation de l'état du jeu
    game_state = init_game_state()

    # Récupération du nom des joueurs
    namep1 = str(input("Quel est le nom du joueur 1 ? "))
    namep2 = str(input("Quel est le nom du joueur 2 ? "))

    # Stockage dans le game_state
    game_state['namep1'] = namep1
    game_state['namep2'] = namep2

    # 4) Stocker les formes dans le state
    game_state['formes'] = formes_initiales

    # 5) Création de la figure et de l'axes
    fig, ax = plt.subplots()
    game_state['fig'] = fig
    game_state['ax'] = ax
    game_state['start_time'] = time.time()

    # 6) Configuration du plateau de jeu et connexion des événements
    setup_board(game_state)
    connect_events(game_state)

    # 7) Afficher la fenêtre Matplotlib (boucle principale)
    fig.canvas.manager.full_screen_toggle() # Mode plein écran ;)
    plt.show()