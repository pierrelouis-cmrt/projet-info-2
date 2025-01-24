import os
import time
import random
import matplotlib.pyplot as plt
from matplotlib.patheffects import withStroke

plt.close('all')

# ===============================
# Génération du fichier config "formes"
# ===============================

def generate_shapes_config(filename="config_shapes.txt"):
    """
    Génère un fichier config pour le mode formes :
    36 cartes = (3 formes × 6 couleurs) × 2 exemplaires.
    Positionnement aléatoire dans une grille 6×6.
    """
    shapes = ["circle", "triangle", "rectangle"]
    colors = ["red", "green", "blue", "yellow", "purple", "orange"]

    combos = [(s, c) for s in shapes for c in colors]  # 18 combos
    all_cards = combos * 2  # double => 36
    random.shuffle(all_cards)

    coords = []
    for row in range(6):
        for col in range(6):
            x = col * 3
            y = row * 3
            coords.append((x, y))
    random.shuffle(coords)

    with open(filename, "w") as f:
        for i, (shape, color) in enumerate(all_cards):
            idx = f"shape_{i+1}"
            (x, y) = coords[i]
            L, H = 3, 3
            line = f"{idx};[{x},{y}];{L};{H};{color};{shape}\n"
            f.write(line)

    return filename


# ===============================
# Lecture du fichier config
# ===============================

def lire_fichier_config(fichier):
    """
    Lit chaque ligne du fichier (ex: ID;[x,y];L;H;couleur;shape)
    et renvoie un dict { 'ID': [(x,y), L, H, couleur, shape], ... }.
    """
    d = {}
    with open(fichier, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(";")
            if len(parts) < 5:
                continue
            idx = parts[0]
            xy = eval(parts[1])  # "[x,y]" -> tuple(x,y)
            L = int(parts[2])
            H = int(parts[3])
            color = parts[4]
            shape = parts[5].strip() if len(parts) >= 6 else "rectangle"

            d[idx] = [xy, L, H, color, shape]
    return d


# ===============================
# Fonctions pour tracer (back & front)
# ===============================
import matplotlib.patches as mpatches

def patch_rectangle(ax, x, y, L, H, facecolor='black', edgecolor='white', lw=1):
    coords = [(x,y), (x+L,y), (x+L,y+H), (x,y+H)]
    poly = plt.Polygon(coords, closed=True, facecolor=facecolor, edgecolor=edgecolor, linewidth=lw)
    ax.add_patch(poly)
    return poly

def patch_circle(ax, x, y, L, H, facecolor='black', edgecolor='white', lw=1):
    cx = x + L/2
    cy = y + H/2
    r = min(L, H)/2
    circle = mpatches.Circle((cx, cy), r, facecolor=facecolor, edgecolor=edgecolor, linewidth=lw)
    ax.add_patch(circle)
    return circle

def patch_triangle(ax, x, y, L, H, facecolor='black', edgecolor='white', lw=1):
    p1 = (x + L/2, y + H)
    p2 = (x, y)
    p3 = (x + L, y)
    poly = plt.Polygon([p1, p2, p3], closed=True, facecolor=facecolor, edgecolor=edgecolor, linewidth=lw)
    ax.add_patch(poly)
    return poly

def create_card_patches(ax, x, y, L, H, shape, color):
    """
    Crée 3 patches :
      1) back_patch : rectangle noir (dos)
      2) front_bg   : rectangle noir occupant la bounding box (invisible jusqu'à la révélation)
      3) front_shape: la forme colorée (invisible jusqu'à la révélation)
    """
    back_patch = patch_rectangle(ax, x, y, L, H, facecolor='black', edgecolor='white')

    front_bg = patch_rectangle(ax, x, y, L, H, facecolor='black', edgecolor='white')
    front_bg.set_visible(False)

    if shape == "circle":
        front_shape = patch_circle(ax, x, y, L, H, facecolor=color, edgecolor='white')
    elif shape == "triangle":
        front_shape = patch_triangle(ax, x, y, L, H, facecolor=color, edgecolor='white')
    else:
        # rectangle par défaut
        front_shape = patch_rectangle(ax, x, y, L, H, facecolor=color, edgecolor='white')
    front_shape.set_visible(False)

    return back_patch, front_bg, front_shape


# ===============================
# Gestion du jeu
# ===============================

def init_game_state():
    return {
        'formes': None,       # dict {ID: [ (x,y), L, H, color, shape ]}
        'cards': [],
        'fig': None,
        'ax': None,
        'clicked_cards': [],
        'pairs_found': 0,
        'total_pairs': 0,
        'player1_score': 0,
        'player2_score': 0,
        'current_player': 1,
        'start_time': 0,
        'disable_clicks': False,
        'score_timer_text': None,
        'timer': None,
        'namep1': "Joueur1",
        'namep2': "Joueur2"
    }

def setup_board(game_state):
    ax = game_state['ax']
    ax.set_axis_off()

    for key, data in game_state['formes'].items():
        (x, y), L, H, color, shape = data
        back_patch, front_bg, front_shape = create_card_patches(ax, x, y, L, H, shape, color)

        card_info = {
            'id': key,
            'x': x,
            'y': y,
            'L': L,
            'H': H,
            'color': color,
            'shape': shape,
            'is_revealed': False,
            'back_patch': back_patch,
            'front_bg': front_bg,
            'front_shape': front_shape
        }
        game_state['cards'].append(card_info)

    ax.set_aspect('equal', 'box')
    ax.autoscale_view()

    # total de paires = nb_cartes / 2
    game_state['total_pairs'] = len(game_state['cards']) // 2

    txt = ax.text(
        0.5, 1.02, "",
        transform=ax.transAxes, ha="center", va="bottom",
        fontsize=12, fontweight="bold", color="black"
    )
    game_state['score_timer_text'] = txt

    update_score_and_timer(game_state)

def connect_events(game_state):
    fig = game_state['fig']
    fig.canvas.mpl_connect('button_press_event', lambda e: on_click(e, game_state))

    timer = fig.canvas.new_timer(interval=1000)
    timer.add_callback(lambda: update_score_and_timer(game_state))
    timer.start()
    game_state['timer'] = timer

def on_click(event, game_state):
    if game_state['disable_clicks'] or event.xdata is None or event.ydata is None:
        return

    for card in game_state['cards']:
        x, y, L, H = card['x'], card['y'], card['L'], card['H']
        if x <= event.xdata <= x+L and y <= event.ydata <= y+H:
            if not card['is_revealed']:
                reveal_card(card)
                game_state['clicked_cards'].append(card)
                if len(game_state['clicked_cards']) == 2:
                    c1, c2 = game_state['clicked_cards']
                    # Condition pour une paire: même couleur ET même forme
                    if (c1['color'] == c2['color']) and (c1['shape'] == c2['shape']):
                        game_state['pairs_found'] += 1
                        if game_state['current_player'] == 1:
                            game_state['player1_score'] += 1
                        else:
                            game_state['player2_score'] += 1

                        game_state['clicked_cards'].clear()
                        update_score_and_timer(game_state)

                        if game_state['pairs_found'] == game_state['total_pairs']:
                            end_game(game_state)
                        # Sinon, le même joueur rejoue
                    else:
                        # Pas de match
                        game_state['disable_clicks'] = True
                        plt.pause(1.5)
                        hide_card(c1)
                        hide_card(c2)
                        game_state['clicked_cards'].clear()
                        game_state['disable_clicks'] = False
                        next_player(game_state)
                        update_score_and_timer(game_state)
            break

    game_state['fig'].canvas.draw()

def reveal_card(card):
    card['is_revealed'] = True
    card['back_patch'].set_visible(False)
    card['front_bg'].set_visible(True)
    card['front_shape'].set_visible(True)

def hide_card(card):
    card['is_revealed'] = False
    card['back_patch'].set_visible(True)
    card['front_bg'].set_visible(False)
    card['front_shape'].set_visible(False)

def next_player(game_state):
    if game_state['current_player'] == 1:
        game_state['current_player'] = 2
    else:
        game_state['current_player'] = 1

def update_score_and_timer(game_state):
    elapsed = int(time.time() - game_state['start_time'])
    mins = elapsed // 60
    secs = elapsed % 60
    t_str = f"{mins:02d}:{secs:02d}"

    current_name = game_state['namep1'] if game_state['current_player'] == 1 else game_state['namep2']
    score_txt = (f"{game_state['namep1']} : {game_state['player1_score']}   "
                 f"{game_state['namep2']} : {game_state['player2_score']}   "
                 f"(Tour de {current_name})   Temps : {t_str}")
    game_state['score_timer_text'].set_text(score_txt)
    game_state['fig'].canvas.draw_idle()

def end_game(game_state):
    print("Fin du jeu !")
    if game_state['timer']:
        game_state['timer'].stop()

    p1, p2 = game_state['player1_score'], game_state['player2_score']
    if p1 >= p2:
        winner, loser = game_state['namep1'], game_state['namep2']
    else:
        winner, loser = game_state['namep2'], game_state['namep1']

    game_state['disable_clicks'] = True
    game_state['ax'].text(
    0.5, 0.8,
    f"FÉLICITATIONS !\n{winner} a gagné contre {loser}",
    transform=game_state['ax'].transAxes, ha="center", va="center",
    fontsize=16, color="white", fontweight="bold",
    path_effects=[withStroke(linewidth=3, foreground="black")]
)
    game_state['fig'].canvas.draw_idle()


# ===============================
# MAIN (uniquement mode "formes")
# ===============================
if __name__ == "__main__":
    # Pour s'assurer d'un vrai random différent à chaque lancement :
    random.seed(None)

    # On génère/écrit un fichier de config "config_shapes.txt"
    config_file = generate_shapes_config("config_shapes.txt")
    
    # On lit ce fichier et on stocke en mémoire
    d_formes = lire_fichier_config(config_file)

    # Prépare l'état du jeu
    game_state = init_game_state()
    game_state['formes'] = d_formes

    # Noms des joueurs
    p1 = input("Nom du joueur 1 : ")
    p2 = input("Nom du joueur 2 : ")
    game_state['namep1'] = p1 if p1 else "Joueur1"
    game_state['namep2'] = p2 if p2 else "Joueur2"

    fig, ax = plt.subplots()
    game_state['fig'] = fig
    game_state['ax'] = ax
    game_state['start_time'] = time.time()

    # Configuration du plateau et connexion des événements
    setup_board(game_state)
    connect_events(game_state)

    # Affichage + frenêtre maximisée
    manager = plt.get_current_fig_manager()
    try:
        manager.window.state('zoomed')
    except AttributeError:
        manager.window.showMaximized()
    plt.show()
