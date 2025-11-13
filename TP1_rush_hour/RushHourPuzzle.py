import csv
from collections import deque
import copy
import time
import pygame
import random
import os
import sys

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

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


def bFS(etat_initial):
    init_node = Node(etat_initial)

    if init_node.state.isGoal():
        return init_node

    open = deque([init_node])
    close = set()
    close.add(tuple(tuple(row) for row in init_node.state.board))

    while open:
        current = open.popleft()

        for action, child_state in current.state.successorFunction():
            child_node = Node(child_state, current, action, current.g + 1)
            state_repr = tuple(tuple(row) for row in child_state.board)

            if state_repr not in close:
                if child_state.isGoal():
                    return child_node
                open.append(child_node)
                close.add(state_repr)

    return None

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

# Ecrans
def start_screen(screen, width, height):
    # --- Charger le fond ---
    background = pygame.image.load("assets/background.jpg").convert()
    background = pygame.transform.scale(background, (width, height))

    # --- Charger le bouton ---
    button_img = pygame.image.load("assets/button_orang.png").convert_alpha()
    button_img = pygame.transform.scale(button_img, (250, 100))  # ajuste la taille selon ton image
    button_rect = button_img.get_rect(center=(width // 2, height // 2 + 80))

    # --- Polices ---
    title_font = pygame.font.Font('font/Pixeltype.ttf', 80)
    button_font = pygame.font.Font('font/Pixeltype.ttf', 60)

    # --- Textes ---
    title = title_font.render("Rush Hour", True, (255, 170, 70))
    start_text = button_font.render("START", True, (255, 255, 255))

    waiting = True
    while waiting:
        screen.blit(background, (0, 0))

        # Titre
        screen.blit(title, (width // 2 - title.get_width() // 2, height // 2 - 150))

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
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # clic gauche
                if button_rect.collidepoint(event.pos):
                    waiting = False

def end_screen(screen, width, height):
    # --- Charger et ajuster le fond ---
    background = pygame.image.load("assets/background.jpg").convert()
    background = pygame.transform.scale(background, (width, height))

    # --- Charger le bouton ---
    button_img = pygame.image.load("assets/button_orang.png").convert_alpha()
    button_img = pygame.transform.scale(button_img, (250, 100))  # ajuste la taille si besoin
    button_rect = button_img.get_rect(center=(width // 2, height // 2 + 120))

    # --- Polices ---
    title_font = pygame.font.SysFont("Arial", 50, bold=True)
    info_font = pygame.font.SysFont("Arial", 28)
    button_font = pygame.font.Font('font/Pixeltype.ttf', 60)

    # --- Textes ---
    title = title_font.render("Félicitations !", True, (255, 255, 0))
    info = info_font.render("Vous avez résolu le puzzle !", True, (230, 230, 230))
    quit_text = button_font.render("QUIT", True, (255, 255, 255))

    waiting = True
    while waiting:
        # --- Affichage ---
        screen.blit(background, (0, 0))
        screen.blit(title, (width // 2 - title.get_width() // 2, height // 2 - 120))
        screen.blit(info, (width // 2 - info.get_width() // 2, height // 2 - 50))

        # Bouton (image + texte)
        screen.blit(button_img, button_rect.topleft)
        screen.blit(
            quit_text,
            (
                button_rect.centerx - quit_text.get_width() // 2,
                button_rect.centery - quit_text.get_height() // 2
            )
        )

        pygame.display.flip()

        # --- Événements ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

def level_selection_screen(screen, width, height):
    # Charger et redimensionner le fond
    background = pygame.image.load("assets/background.jpg").convert()
    background = pygame.transform.scale(background, (width, height))

    # Charger le bouton image (plus petit)
    button_img = pygame.image.load("assets/button_orang.png").convert_alpha()
    button_img = pygame.transform.scale(button_img, (210, 65))  # ↓ plus petit qu’avant (250x80)

    # Listes des niveaux
    level_files = ["1.csv", "2-a.csv", "2-b.csv", "2-c.csv", "2-d.csv", "2-e.csv", "e-f.csv"]
    level_names = ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Level 6", "Level 7"]

    # Polices
    title_font = pygame.font.Font('font/Pixeltype.ttf', 60)
    button_font = pygame.font.Font('font/Pixeltype.ttf', 35)  # police légèrement réduite

    # Titre
    title_text = title_font.render("Choose a level", True, (255, 255, 255))

    # Position de départ (remontée)
    start_y = 140  # ↑ un peu plus haut
    gap = 70       # ↓ espace réduit (au lieu de 95)

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
            text_surf = button_font.render(lvl_name, True, (255, 255, 255))
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
                mx, my = pygame.mouse.get_pos()
                for rect, csv_file in buttons:
                    if rect.collidepoint(mx, my):
                        selected_file = csv_file
                        waiting = False
                        break

    return selected_file

# Animation
def assign_vehicle_images(vehicles):
    for v in vehicles:
        if v.id == 'X':
            v.image_key = "car_X"
        elif v.length == 2:
            v.image_key = random.choice(["car_h1","car_h2","car_h3"]) if v.orientation=='H' else random.choice(["car_v1","car_v2","car_v3"])
        elif v.length == 3:
            v.image_key = random.choice(["truck_h1","truck_h2"]) if v.orientation=='H' else random.choice(["truck_v1","truck_v2"])
        else:
            v.image_key = "car_h2"

def draw_animated_board(screen, temp_puzzle, cell_size, margin, font):
    ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
    images = {
        "background": pygame.image.load(os.path.join(ASSET_DIR, "road_asphalt82.png")),
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
    bw, bh = temp_puzzle.board_width, temp_puzzle.board_height
    bg = pygame.transform.scale(images["background"], (bw*cell_size+margin*2, bh*cell_size+margin*2))
    screen.blit(bg, (0,0))
    for r in range(bh):
        for c in range(bw):
            if temp_puzzle.board[r][c]=='#':
                rect = pygame.Rect(margin+c*cell_size, margin+r*cell_size, cell_size, cell_size)
                wall_img = pygame.transform.scale(images["wall"], (cell_size, cell_size))
                screen.blit(wall_img, rect.topleft)
    for v in temp_puzzle.vehicles:
        x_pixel = margin + v.x * cell_size
        y_pixel = margin + v.y * cell_size
        img = images[v.image_key]
        w = v.length*cell_size if v.orientation=='H' else cell_size
        h = cell_size if v.orientation=='H' else v.length*cell_size
        img = pygame.transform.scale(img, (int(w-8), int(h-8)))
        screen.blit(img, (x_pixel+4, y_pixel+4))
       #text_surf = font.render(v.id, True, (10,10,10))
        #screen.blit(text_surf, (x_pixel+10, y_pixel+5))
    pygame.display.flip()

def animate_solution(initial_puzzle, solution_actions, fps=60, frames_per_move=12):
    cell_size = 80
    margin = 20

    # --- Calcul de la taille idéale du board ---
    board_width = initial_puzzle.board_width
    board_height = initial_puzzle.board_height
    anim_width = board_width * cell_size + margin * 2
    anim_height = board_height * cell_size + margin * 2

    # --- Créer une fenêtre temporaire adaptée ---
    screen = pygame.display.set_mode((anim_width, anim_height))
    pygame.display.set_caption("Rush Hour - Animation")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    working = copy.deepcopy(initial_puzzle)
    working.setBoard()
    anim_positions = [[float(v.x), float(v.y)] for v in working.vehicles]
    assign_vehicle_images(working.vehicles)

    running = True
    action_index = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        if action_index < len(solution_actions):
            vid, direction = solution_actions[action_index]
            idx = next(i for i, v in enumerate(working.vehicles) if v.id == vid)
            dx, dy = {'L': (-1, 0), 'R': (1, 0), 'U': (0, -1), 'D': (0, 1)}.get(direction, (0, 0))
            target_x = working.vehicles[idx].x + dx
            target_y = working.vehicles[idx].y + dy
            step_x, step_y = dx / frames_per_move, dy / frames_per_move

            for _ in range(frames_per_move):
                anim_positions[idx][0] += step_x
                anim_positions[idx][1] += step_y
                temp = copy.deepcopy(working)
                for i, v in enumerate(temp.vehicles):
                    v.x = anim_positions[i][0]
                    v.y = anim_positions[i][1]
                draw_animated_board(screen, temp, cell_size, margin, font)
                clock.tick(fps)

            working.vehicles[idx].x = int(round(target_x))
            working.vehicles[idx].y = int(round(target_y))
            anim_positions[idx] = [float(working.vehicles[idx].x), float(working.vehicles[idx].y)]
            working.setBoard()
            action_index += 1
        else:
            running = False

    # --- Revenir à la taille initiale après l’animation ---
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    end_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT)


# Main
if __name__ == "__main__":
    pygame.init()

    pygame.mixer.music.load("assets/musique.mp3")
    pygame.mixer.music.set_volume(0.6)  # volume entre 0.0 et 1.0
    pygame.mixer.music.play(-1) 

    # Taille unique pour toute l’application
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Rush Hour")

    # --- Écran de démarrage ---
    start_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

    # --- Sélection du niveau ---
    selected_file = level_selection_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
    print("Niveau choisi :", selected_file)

    # --- Chargement du puzzle ---
    puzzle = RushHourPuzzle()
    puzzle.setVehicles(selected_file)
    puzzle.setBoard()
    puzzle.printBoard()

    # --- Résolution ---
    solution = bFS(puzzle)
    if solution:
        print("Solution trouvée")
        actions = solution.getSolution()
        print("Chemin des actions :", actions)
        animate_solution(puzzle, actions, fps=40, frames_per_move=12)  # la fenêtre reste 800x600
    else:
        print("Pas de solution trouvée")

    pygame.quit()
