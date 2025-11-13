import csv
from collections import deque
import copy
import time
import pygame
import random
import os
import sys
import heapq
import itertools 


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

#------------------------------#
#   Les classe (state et node)
#------------------------------#

#STATE
class Vehicule:
    def __init__(self, voiture_id, x, y, orientation, length):
        self.id = voiture_id
        self.x = x
        self.y = y
        self.orientation = orientation
        self.length = length

class RushHourPuzzle:
    def __init__(self):
        self.board_height = 6
        self.board_width = 6
        self.vehicles = []
        self.walls = []
        self.board = []

    def setVehicles(self, csv_file):
        with open(csv_file, newline='') as csvfile:
            lecteur = csv.reader(csvfile)
            lignes = list(lecteur)
            self.board_width = int(lignes[0][0])
            self.board_height = int(lignes[0][1])

            for ligne in lignes[1:]:
                if ligne[0] == '#':
                    x = int(ligne[1])
                    y = int(ligne[2])
                    self.walls.append((x, y))
                else:
                    voiture_id = ligne[0]
                    x = int(ligne[1])
                    y = int(ligne[2])
                    orientation = ligne[3]
                    length = int(ligne[4])
                    self.vehicles.append(Vehicule(voiture_id, x, y, orientation, length))

    def setBoard(self):
        # table pleine des points '.'
        self.board = []
        for i in range(self.board_height):
            row = []
            for j in range(self.board_width):
                row.append('.')
            self.board.append(row)
        # placement des véhicules 
        for v in self.vehicles:
            if v.orientation == 'H':
                for k in range(v.length):
                    self.board[v.y][v.x + k] = v.id
            else:
                for k in range(v.length):
                    self.board[v.y + k][v.x] = v.id

        # les murs :
        for (x, y) in self.walls:
            self.board[y][x] = '#'

    def printBoard(self):
        print("\n----------------------")
        for row in self.board:
            print(" ".join(row))
        print("----------------------")
        time.sleep(0.05)

    def isGoal(self):
        for i in self.vehicles:
            if i.id == 'X':
                if i.x + i.length == self.board_width:
                    return True
        return False

    def successorFunction(self):
        successors = []
        for i, v in enumerate(self.vehicles):
            if v.orientation == 'H':#horisental
                # gauche
                if v.x > 0 and self.board[v.y][v.x - 1] == '.':
                    etat_succes = copy.deepcopy(self)
                    etat_succes.vehicles[i].x -= 1
                    etat_succes.setBoard()
                    successors.append(((v.id, 'L'), etat_succes))
                # droite
                if v.x + v.length < self.board_width and self.board[v.y][v.x + v.length] == '.':
                    etat_succes = copy.deepcopy(self)
                    etat_succes.vehicles[i].x += 1
                    etat_succes.setBoard()
                    successors.append(((v.id, 'R'), etat_succes))
            else:  # Vertical
                # haut
                if v.y > 0 and self.board[v.y - 1][v.x] == '.':
                    etat_succes = copy.deepcopy(self)
                    etat_succes.vehicles[i].y -= 1
                    etat_succes.setBoard()
                    successors.append(((v.id, 'U'), etat_succes))
                # bas
                if v.y + v.length < self.board_height and self.board[v.y + v.length][v.x] == '.':
                    etat_succes = copy.deepcopy(self)
                    etat_succes.vehicles[i].y += 1
                    etat_succes.setBoard()
                    successors.append(((v.id, 'D'), etat_succes))
        return successors

# Node 
class Node:
    def __init__(self, state, parent=None, action=None, g=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.g = g
        self.f = 0

    def getPath(self):
        node = self
        path = []
        while node is not None:
            path.append(node.state)
            node = node.parent
        return list(reversed(path))

    def getSolution(self):
        node = self
        actions = []
        while node.parent is not None:
            actions.append(node.action)
            node = node.parent
        return list(reversed(actions))

    def setF(self, h):
        self.f = self.g + h

#------------------------------#
#LES ALGORITHEMes de recherches
#------------------------------#

def bFS(etat_initial):
    init_node = Node(etat_initial)
    explored = 0

    if init_node.state.isGoal():
        return init_node

    open = deque([init_node])
    close = set()
    
    while open:
        current = open.popleft()
        close.add(tuple(tuple(row) for row in current.state.board))
        explored += 1
        for action, child_state in current.state.successorFunction():
            
            child_node = Node(child_state, current, action, current.g + 1)
            state_repr = tuple(tuple(row) for row in child_state.board)
            if child_state.isGoal():
                    print("BFS explored:", explored, "states")
                    print("BFS cost:", child_node.g)
                    return child_node

            if state_repr not in close and all(tuple(tuple(row) for row in n.state.board) != state_repr for n in open):
                
                open.append(child_node)
    return None



# --- Heuristiques --- #
def heuristique1(state):
    """Distance de la voiture X à la sortie."""
    for v in state.vehicles:
        if v.id == 'X':
            return (state.board_width - (v.x + v.length))
    return 0


def heuristique2(state):
    """
    Heuristique h2 : distance du véhicule X à la sortie
    + nombre de véhicules bloquant son chemin.
    """
    # Trouver la voiture rouge 'X'
    x_car = None
    for v in state.vehicles:
        if v.id == 'X':
            x_car = v
            break
    if x_car is None:
        return 0

    # Distance horizontale jusqu’à la sortie
    distance = state.board_width - (x_car.x + x_car.length)

    # Compter les véhicules bloquant le chemin de sortie
    y = x_car.y
    blocking = 0
    for xx in range(x_car.x + x_car.length, state.board_width):
        cell = state.board[y][xx]
        if cell != '.':
            blocking += 1

    return distance + blocking


def heuristique3(state):
    """
    Heuristique: distance restante + nombre de véhicules bloquant la sortie,
    en ajoutant une pénalité si ces véhicules eux-mêmes sont bloqués 
    """
    # trouver X
    x_car = None
    for v in state.vehicles:
        if v.id == 'X':
            x_car = v
            break
    if x_car is None:
        return 0

    distance = state.board_width - (x_car.x + x_car.length)
    y = x_car.y
    blocking_ids = []
    for xx in range(x_car.x + x_car.length, state.board_width):
        cell = state.board[y][xx]
        if cell != '.':
            blocking_ids.append(cell)

    # compter véhicules qui bloquent et pénaliser selon s'ils sont bloqués
    penalty = 0
    for bid in set(blocking_ids):
        # chercher ce véhicule
        bv = next((vv for vv in state.vehicles if vv.id == bid), None)
        if bv is None:
            continue
        # regarder devant/derrière selon orientation pour estimer s'il peut bouger facilement
        can_move = False
        if bv.orientation == 'H':
            # tester gauche/droite d'une cellule
            if bv.x > 0 and state.board[bv.y][bv.x - 1] == '.':
                can_move = True
            if bv.x + bv.length < state.board_width and state.board[bv.y][bv.x + bv.length] == '.':
                can_move = True
        else:
            if bv.y > 0 and state.board[bv.y - 1][bv.x] == '.':
                can_move = True
            if bv.y + bv.length < state.board_height and state.board[bv.y + bv.length][bv.x] == '.':
                can_move = True
        if not can_move:
            penalty += 1  # véhicule lui-même bloqué -> plus coûteux

    return distance + len(set(blocking_ids)) + penalty

# --- Algorithme A* --- #
def aStar(etat_initial, heuristique):
    Open = []  # priority queue (heap) contenant des tuples (f, counter, node)
    Closed = {}  # dict: état_repr -> meilleur f connu (permets la comparaison)
    counter = itertools.count()  # compteur unique pour éviter les comparaisons de Node
    explored = 0

    init_node = Node(etat_initial)
    init_node.g = 0
    init_node.f = init_node.g + heuristique(init_node.state)
    heapq.heappush(Open, (init_node.f, next(counter), init_node))

    while Open:
        f_val, _, current = heapq.heappop(Open)
        # repésentation de l'état courant (immutable)
        state_repr = tuple(tuple(row) for row in current.state.board)

        # Si cette entrée est obsolète (on a déjà trouvé un meilleur f pour cet état),
        # on l'ignore.
        if state_repr in Closed and f_val > Closed[state_repr]:
            continue

        explored += 1

        # Test but : faire après la vérif des entrées obsolètes
        if current.state.isGoal():
            print("A* explored:", explored, "states")
            print("A* cost:", current.g)
            return current

        # Marquer l'état comme exploré en enregistrant le meilleur f connu
        Closed[state_repr] = current.f

        # Expansion
        for action, successor in current.state.successorFunction():
            child = Node(successor, current, action)
            child.g = current.g + 1  # chaque déplacement coûte 1
            child.f = child.g + heuristique(child.state)

            child_repr = tuple(tuple(row) for row in child.state.board)

            # Si dans Closed :
            if child_repr in Closed:
                # si on trouve un meilleur f que celui stocké, on "ré-ouvre" l'état
                if child.f < Closed[child_repr]:
                    # supprimer l'enregistrement Closed pour permettre la réinsertion
                    del Closed[child_repr]
                    heapq.heappush(Open, (child.f, next(counter), child))
                # sinon on ignore ce successeur
                continue

            # Vérifier si déjà dans Open 
            in_open = False
            for i, (open_f, _, n) in enumerate(Open):
                if tuple(tuple(row) for row in n.state.board) == child_repr:
                    in_open = True
                    # si le nouveau chemin est meilleur, remplacer l'entrée existante
                    if child.f < open_f:
                        Open[i] = (child.f, next(counter), child) #remplacer l'encien tuple avec le nouuv 
                        heapq.heapify(Open)  # réorganiser le heap après modification
                    break

            if not in_open and child_repr not in Closed:
                heapq.heappush(Open, (child.f, next(counter), child))

    # Aucun chemin trouvé
    return None




#------------------------------#
# Ecrans
#------------------------------#

def splash_screen(screen, width, height):
    # Charger et redimensionner le fond
    background = pygame.image.load("assets/background_splash.jpg").convert()
    background = pygame.transform.scale(background, (width, height))

    # Charger le logo
    logo = pygame.image.load("assets/logo.png").convert_alpha()
    logo_width, logo_height = 400, 200  
    logo = pygame.transform.scale(logo, (logo_width, logo_height))
    logo_rect = logo.get_rect(center=(width // 2, height // 2))

    # Afficher le splash
    screen.blit(background, (0, 0))
    screen.blit(logo, logo_rect)
    pygame.display.flip()

    # Attendre 3 secondes OU jusqu’à une touche/clique
    start_time = pygame.time.get_ticks()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                click_sound.play()
                waiting = False
        # si 3 secondes sont passées, on quitte
        if pygame.time.get_ticks() - start_time > 3000:
            waiting = False

def start_screen(screen, width, height):
    # --- Charger le fond ---
    background = pygame.image.load("assets/background.jpg").convert()
    background = pygame.transform.scale(background, (width, height))

    # --- Charger le bouton ---
    button_img = pygame.image.load("assets/button_orang.png").convert_alpha()
    button_img = pygame.transform.scale(button_img, (250, 100))  # ajuste la taille selon ton image
    button_rect = button_img.get_rect(center=(width // 2, height // 2 + 80))

    # --- Polices ---
    title_font = pygame.font.Font('font/Pixeltype.ttf', 150)
    button_font = pygame.font.Font('font/Pixeltype.ttf', 60)

    # --- Textes ---
    title = title_font.render("Rush Hour", True, (242, 98, 10))
    start_text = button_font.render("START", True, (0, 0, 0))
    #---logo---
    logo = pygame.image.load("assets/logo.png").convert()
    logo=pygame.transform.scale(logo, (600,150))

    waiting = True
    while waiting:
        screen.blit(background, (0, 0))

        # Titre
        screen.blit(title, (width // 2 - title.get_width() // 2, height // 2 - 150))
        #screen.blit(logo , (width // 2 - title.get_width() // 2, height // 2 - 150))

        # Bouton (image + texte)
        screen.blit(button_img, button_rect.topleft)
        screen.blit(
            start_text,
            (
                button_rect.centerx - start_text.get_width() // 2,
                button_rect.centery - start_text.get_height() // 2
            )
        )

        pygame.display.flip()

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Clic sur le bouton
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  
                click_sound.play()
                if button_rect.collidepoint(event.pos):
                    waiting = False
def algorithm_selection_screen(screen, width, height):
    # Charger et redimensionner le fond
    background = pygame.image.load("assets/background.jpg").convert()
    background = pygame.transform.scale(background, (width, height))

    # Charger le bouton image
    button_img = pygame.image.load("assets/button_orang.png").convert_alpha()
    button_img = pygame.transform.scale(button_img, (250, 90))

    # Polices
    title_font = pygame.font.Font('font/Pixeltype.ttf', 80)
    button_font = pygame.font.Font('font/Pixeltype.ttf', 45)

    # Titre
    title_text = title_font.render("Choose Algorithm", True, (242, 98, 10))

    # Positions des boutons (un peu plus espacés)
    # Espacement régulier des boutons
    spacing = 100
    #start_y = height // 2 - spacing * 1.5  # pour centrer verticalement les 4 boutons
    start_y = 200

    bfs_rect    = button_img.get_rect(center=(width // 2, start_y))
    astar1_rect = button_img.get_rect(center=(width // 2, start_y + spacing))
    astar2_rect = button_img.get_rect(center=(width // 2, start_y + spacing * 2))
    astar3_rect = button_img.get_rect(center=(width // 2, start_y + spacing * 3))


    waiting = True
    selected_algo = None

    while waiting:
        screen.blit(background, (0, 0))
        screen.blit(title_text, (width // 2 - title_text.get_width() // 2, 100))

        # --- Bouton BFS ---
        screen.blit(button_img, bfs_rect.topleft)
        bfs_text = button_font.render("BFS", True, (0, 0, 0))
        screen.blit(
            bfs_text,
            (
                bfs_rect.centerx - bfs_text.get_width() // 2,
                bfs_rect.centery - bfs_text.get_height() // 2,
            ),
        )

        # --- Bouton A* (h1) ---
        screen.blit(button_img, astar1_rect.topleft)
        astar1_text = button_font.render("A* (h1)", True, (0, 0, 0))
        screen.blit(
            astar1_text,
            (
                astar1_rect.centerx - astar1_text.get_width() // 2,
                astar1_rect.centery - astar1_text.get_height() // 2,
            ),
        )

        # --- Bouton A* (h2) ---
        screen.blit(button_img, astar2_rect.topleft)
        astar2_text = button_font.render("A* (h2)", True, (0, 0, 0))
        screen.blit(
            astar2_text,
            (
                astar2_rect.centerx - astar2_text.get_width() // 2,
                astar2_rect.centery - astar2_text.get_height() // 2,
            ),
        )
        # --- Bouton A* (h3) ---
        screen.blit(button_img, astar3_rect.topleft)
        astar3_text = button_font.render("A* (h3)", True, (0, 0, 0))
        screen.blit(
            astar3_text,
            (
                astar3_rect.centerx - astar3_text.get_width() // 2,
                astar3_rect.centery - astar3_text.get_height() // 2,
            ),
        )
        pygame.display.flip()

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click_sound.play()
                if bfs_rect.collidepoint(event.pos):
                    selected_algo = "BFS"
                    waiting = False
                elif astar1_rect.collidepoint(event.pos):
                    selected_algo = "A* (h1)"
                    waiting = False
                elif astar2_rect.collidepoint(event.pos):
                    selected_algo = "A* (h2)"
                    waiting = False
                elif astar3_rect.collidepoint(event.pos):
                    selected_algo = "A* (h3)"
                    waiting = False


    return selected_algo

def end_screen(screen, width, height, solution):
    # --- Charger et ajuster le fond ---
    background = pygame.image.load("assets/background.jpg").convert()
    background = pygame.transform.scale(background, (width, height))

    # --- Charger le bouton ---
    button_img = pygame.image.load("assets/button_orang.png").convert_alpha()
    button_img = pygame.transform.scale(button_img, (220, 90))

    # --- Positions des boutons ---
    levels_rect = button_img.get_rect(center=(width // 2 - 220, height // 2 + 150))
    algos_rect  = button_img.get_rect(center=(width // 2, height // 2 + 150))
    quit_rect   = button_img.get_rect(center=(width // 2 + 220, height // 2 + 150))

    # --- Polices ---
    title_font = pygame.font.Font('font/Pixeltype.ttf', 130)
    info_font = pygame.font.Font('font/Pixeltype.ttf', 80)
    step_font = pygame.font.Font('font/Pixeltype.ttf', 70)
    button_font = pygame.font.Font('font/Pixeltype.ttf', 50)

    # --- Textes ---
    title = title_font.render("Winner!", True, (255, 255, 0))
    info = info_font.render("You solved the puzzle!", True, (0, 0, 0))
    steps_text = step_font.render(f"Steps: {len(solution)}", True, (0, 0, 0))

    levels_text = button_font.render("LEVELS", True, (0, 0, 0))
    algos_text = button_font.render("ALGOS", True, (0, 0, 0))
    quit_text = button_font.render("QUIT", True, (0, 0, 0))

    waiting = True
    choice = "quit"

    while waiting:
        screen.blit(background, (0, 0))
        screen.blit(title, (width // 2 - title.get_width() // 2, height // 2 - 180))
        screen.blit(info, (width // 2 - info.get_width() // 2, height // 2 - 80))
        screen.blit(steps_text, (width // 2 - steps_text.get_width() // 2, height // 2))

        # Boutons
        screen.blit(button_img, levels_rect.topleft)
        screen.blit(button_img, algos_rect.topleft)
        screen.blit(button_img, quit_rect.topleft)

        screen.blit(levels_text, (levels_rect.centerx - levels_text.get_width() // 2, levels_rect.centery - levels_text.get_height() // 2))
        screen.blit(algos_text,  (algos_rect.centerx  - algos_text.get_width() // 2,  algos_rect.centery  - algos_text.get_height() // 2))
        screen.blit(quit_text,   (quit_rect.centerx   - quit_text.get_width() // 2,   quit_rect.centery   - quit_text.get_height() // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click_sound.play()
                if levels_rect.collidepoint(event.pos):
                    choice = "levels"
                    waiting = False
                    break
                elif algos_rect.collidepoint(event.pos):
                    choice = "algos"
                    waiting = False
                    break
                elif quit_rect.collidepoint(event.pos):
                    choice = "quit"
                    waiting = False
                    break

    return choice


def level_selection_screen(screen, width, height):
    # Charger et redimensionner le fond
    background = pygame.image.load("assets/background.jpg").convert()
    background = pygame.transform.scale(background, (width, height))

    # Charger le bouton image (plus petit)
    button_img = pygame.image.load("assets/button_orang.png").convert_alpha()
    button_img = pygame.transform.scale(button_img, (210, 65))  

    # Listes des niveaux
    level_files = ["1.csv", "2-a.csv", "2-b.csv", "2-c.csv", "2-d.csv", "2-e.csv", "e-f.csv"]
    level_names = ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Level 6", "Level 7"]

    # Polices
    title_font = pygame.font.Font('font/Pixeltype.ttf', 60)
    button_font = pygame.font.Font('font/Pixeltype.ttf', 35)  

    # Titre
    title_text = title_font.render("Choose a level", True, (242, 98, 10))

    # Position de départ (btns de levels)
    start_y = 140  
    gap = 70      

    waiting = True
    selected_file = None

    while waiting:
        screen.blit(background, (0, 0))
        screen.blit(title_text, (width//2 - title_text.get_width()//2, 40))

        buttons = []
        for i, lvl_name in enumerate(level_names):
            rect = button_img.get_rect(center=(width // 2, start_y + i * gap))

            # Afficher le bouton
            screen.blit(button_img, rect.topleft)

            # Texte centré
            text_surf = button_font.render(lvl_name, True, (0, 0, 0))
            screen.blit(
                text_surf,
                (
                    rect.centerx - text_surf.get_width() // 2,
                    rect.centery - text_surf.get_height() // 2
                )
            )
            buttons.append((rect, level_files[i]))

        pygame.display.flip()

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click_sound.play()
                for rect, csv_file in buttons:
                    if rect.collidepoint(event.pos):
                        selected_file = csv_file
                        waiting = False
                        break

    return selected_file
# ======================
#   ANIMATION
# ======================

def assign_vehicle_images(vehicles):
    for v in vehicles:
        if v.id == 'X':
            v.image_key = "car_X"
        elif v.length == 2:
            v.image_key = random.choice(["car_h1", "car_h2", "car_h3"]) if v.orientation == 'H' else random.choice(["car_v1", "car_v2", "car_v3"])
        elif v.length == 3:
            v.image_key = random.choice(["truck_h1", "truck_h2"]) if v.orientation == 'H' else random.choice(["truck_v1", "truck_v2"])
        else:
            v.image_key = "car_h2"


def draw_animated_board(screen, temp_puzzle, cell_size, margin, font, offset_x=0, offset_y=0):
    ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
    images = {
        "background": pygame.image.load(os.path.join(ASSET_DIR, "Regular_car_select.png")),
        "wall": pygame.image.load(os.path.join(ASSET_DIR, "tree_small.png")),
        "car_h1": pygame.image.load(os.path.join(ASSET_DIR, "car_h1.png")),
        "car_h2": pygame.image.load(os.path.join(ASSET_DIR, "car_h2.png")),
        "car_h3": pygame.image.load(os.path.join(ASSET_DIR, "car_h3.png")),
        "car_v1": pygame.image.load(os.path.join(ASSET_DIR, "car_v1.png")),
        "car_v2": pygame.image.load(os.path.join(ASSET_DIR, "car_v2.png")),
        "car_v3": pygame.image.load(os.path.join(ASSET_DIR, "car_v3.png")),
        "car_X": pygame.image.load(os.path.join(ASSET_DIR, "car_X.png")),
        "truck_h1": pygame.image.load(os.path.join(ASSET_DIR, "truck_h1.png")),
        "truck_h2": pygame.image.load(os.path.join(ASSET_DIR, "truck_h2.png")),
        "truck_v1": pygame.image.load(os.path.join(ASSET_DIR, "truck_v1.png")),
        "truck_v2": pygame.image.load(os.path.join(ASSET_DIR, "truck_v2.png")),
    }

    # Charger et redimensionner le fond pour couvrir tout l'écran
    screen_width, screen_height = screen.get_size()
    background_full = pygame.transform.scale(images["background"], (screen_width, screen_height))
    screen.blit(background_full, (0, 0))  # Le fond sur tout l'écran

  
    bw, bh = temp_puzzle.board_width, temp_puzzle.board_height



    # ---arbres ---
    for r in range(bh):
        for c in range(bw):
            if temp_puzzle.board[r][c] == '#':
                rect = pygame.Rect(offset_x + margin + c * cell_size,
                                   offset_y + margin + r * cell_size,
                                   cell_size, cell_size)
                wall_img = pygame.transform.scale(images["wall"], (cell_size, cell_size))
                screen.blit(wall_img, rect.topleft)

    # --- véhicules ---
    for v in temp_puzzle.vehicles:
        x_pixel = offset_x + margin + v.x * cell_size
        y_pixel = offset_y + margin + v.y * cell_size
        img = images[v.image_key]
        w = v.length * cell_size if v.orientation == 'H' else cell_size
        h = cell_size if v.orientation == 'H' else v.length * cell_size
        img = pygame.transform.scale(img, (int(w - 8), int(h - 8)))
        screen.blit(img, (x_pixel + 4, y_pixel + 4))

    #pygame.display.flip()
def animate_solution(initial_puzzle, solution_actions, fps=50, frames_per_move=10):
    # --- Fenêtre ---
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Rush Hour - Animation")

    # --- Paramètres ---
    margin = 40
    cell_size = 80

    # --- Calcul des dimensions du plateau ---
    board_width = initial_puzzle.board_width
    board_height = initial_puzzle.board_height
    board_px_width = board_width * cell_size + margin * 2
    board_px_height = board_height * cell_size + margin * 2

    # --- Centrage du plateau ---
    offset_x = (SCREEN_WIDTH - board_px_width) // 2 + margin
    offset_y = (SCREEN_HEIGHT - board_px_height) // 2 + margin

    # --- Initialisation ---
    clock = pygame.time.Clock()
    font = pygame.font.Font('font/Pixeltype.ttf', 40)
    working = copy.deepcopy(initial_puzzle)
    working.setBoard()
    anim_positions = [[float(v.x), float(v.y)] for v in working.vehicles]
    assign_vehicle_images(working.vehicles)

    running = True
    skip = False
    action_index = 0
    total_steps = len(solution_actions)

    # --- Bouton Skip ---
    button_img = pygame.image.load("assets/button_orang.png").convert_alpha()
    button_img = pygame.transform.scale(button_img, (180, 70))
    skip_rect = button_img.get_rect(topright=(SCREEN_WIDTH - 40, 40))
    skip_text = font.render("SKIP", True, (0, 0, 0))

    # --- Boucle principale ---
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click_sound.play()
                if skip_rect.collidepoint(event.pos):
                    skip = True
                    running = False
                    break

        if skip:
            break

        if action_index < total_steps:
            vid, direction = solution_actions[action_index]
            idx = next(i for i, v in enumerate(working.vehicles) if v.id == vid)
            dx, dy = {'L': (-1, 0), 'R': (1, 0), 'U': (0, -1), 'D': (0, 1)}.get(direction, (0, 0))
            target_x = working.vehicles[idx].x + dx
            target_y = working.vehicles[idx].y + dy
            step_x, step_y = dx / frames_per_move, dy / frames_per_move

            # Animation fluide
            for _ in range(frames_per_move):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return "quit"
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if skip_rect.collidepoint(event.pos):
                            skip = True
                            break
                if skip:
                    break

                anim_positions[idx][0] += step_x
                anim_positions[idx][1] += step_y
                temp = copy.deepcopy(working)
                for i, v in enumerate(temp.vehicles):
                    v.x = anim_positions[i][0]
                    v.y = anim_positions[i][1]
                draw_animated_board(screen, temp, cell_size, margin, font, offset_x, offset_y)

                # Bouton + compteur steps
                screen.blit(button_img, skip_rect.topleft)
                screen.blit(skip_text, (
                    skip_rect.centerx - skip_text.get_width() // 2,
                    skip_rect.centery - skip_text.get_height() // 2
                ))
                step_counter = font.render(f"Step {action_index + 1}/{total_steps}", True, (255, 255, 255))
                screen.blit(step_counter, (40, 40))

                pygame.display.flip()
                clock.tick(fps)

            if skip:
                break

            working.vehicles[idx].x = int(round(target_x))
            working.vehicles[idx].y = int(round(target_y))
            anim_positions[idx] = [float(working.vehicles[idx].x), float(working.vehicles[idx].y)]
            working.setBoard()
            action_index += 1
        else:
            running = False

        # Affichage stable entre mouvements
        draw_animated_board(screen, working, cell_size, margin, font, offset_x, offset_y)
        screen.blit(button_img, skip_rect.topleft)
        screen.blit(skip_text, (
            skip_rect.centerx - skip_text.get_width() // 2,
            skip_rect.centery - skip_text.get_height() // 2
        ))
        step_counter = font.render(f"Step {action_index}/{total_steps}", True, (255, 255, 255))
        screen.blit(step_counter, (40, 40))
        pygame.display.flip()

    # Si le joueur clique sur "Skip", on passe directement à l'écran de fin
    if skip:
        return end_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT, solution_actions)

    # Sinon, animation finale de sortie de la voiture X
    car_x = next((v for v in working.vehicles if v.id == 'X'), None)
    if car_x and not skip:
        idx = next(i for i, v in enumerate(working.vehicles) if v.id == 'X')
        while (anim_positions[idx][0] * cell_size + offset_x) < SCREEN_WIDTH:
            anim_positions[idx][0] += 0.1
            temp = copy.deepcopy(working)
            for i, v in enumerate(temp.vehicles):
                v.x = anim_positions[i][0]
                v.y = anim_positions[i][1]
            draw_animated_board(screen, temp, cell_size, margin, font, offset_x, offset_y)

            screen.blit(button_img, skip_rect.topleft)
            screen.blit(skip_text, (
                skip_rect.centerx - skip_text.get_width() // 2,
                skip_rect.centery - skip_text.get_height() // 2
            ))
            step_counter = font.render(f"{total_steps}/{total_steps}", True, (255, 255, 255))
            screen.blit(step_counter, (40, 40))
            pygame.display.flip()
            clock.tick(fps)

    # Arrive à l'écran de fin
    return end_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT, solution_actions)



# Main
if __name__ == "__main__":
    pygame.init()

    pygame.mixer.music.load("assets/musique.mp3")
    pygame.mixer.music.set_volume(0.6)
    pygame.mixer.music.play(-1)

    click_sound = pygame.mixer.Sound("assets/click.wav")

    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Rush Hour")

    # Écran d'intro
    splash_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

    # Écran de démarrage
    start_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

    while True:
        # Étape 1 : choisir le niveau 
        selected_file = level_selection_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        if not selected_file:
            pygame.quit()
            sys.exit()

        print("Niveau choisi :", selected_file)

        # Charger le puzzle
        puzzle = RushHourPuzzle()
        puzzle.setVehicles(selected_file)
        puzzle.setBoard()

        # Boucle pour rechoisir l’algo sans changer de niveau
        while True:
            # Étape 2 : choisir l'algorithme
            selected_algo = algorithm_selection_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
            print("Algorithme choisi :", selected_algo)

            # Résolution
            if selected_algo == "BFS":
                solved_node = bFS(puzzle)
            elif selected_algo == "A* (h1)":
                solved_node = aStar(puzzle, heuristique1)
            elif selected_algo == "A* (h2)":
                solved_node = aStar(puzzle, heuristique2)
            elif selected_algo == "A* (h3)":
                solved_node = aStar(puzzle, heuristique3)


            else:
                solved_node = None

            # Étape 3 : animation ou retour
            if solved_node:
                actions = solved_node.getSolution()
                print("Chemin des actions :", actions)
                end_choice = animate_solution(puzzle, actions, fps=80, frames_per_move=10)

                if end_choice == "levels":
                    # Revenir à la sélection de niveau
                    break  
                elif end_choice == "algos":
                    # Revenir à la sélection d'algo pour le même niveau
                    continue  
                else:
                    pygame.quit()
                    sys.exit()
            else:
                print("Pas de solution trouvée.")
                break
