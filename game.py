import pygame
import random
from random import randint as ri
import heapq

pygame.init()
pygame.key.set_repeat(200, 60)

#print(pygame.font.get_fonts())
# Fixed grid dimensions (number of characters)
COLS = 100
ROWS = 40

# Setup Fullscreen & Resizable display
flags = pygame.FULLSCREEN | pygame.RESIZABLE
screen = pygame.display.set_mode((0, 0), flags)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("ASCII Grid Roguelike")

NUMROOMS = 80
NUM_ENEMIES = 10
PLAYER_MAX_HP = 99999
ENEMY_MAX_HP = 20

player_hp = PLAYER_MAX_HP

def a_star(start, goal, blocked):
    if start == goal:
        return None

    open_set = [(abs(start[0] - goal[0]) + abs(start[1] - goal[1]), 0, start)]
    came_from = {}
    g_score = {start: 0}

    while open_set:
        _, current_g, current = heapq.heappop(open_set)

        if current == goal:
            while came_from[current] != start:
                current = came_from[current]
            return current

        if current_g > g_score.get(current, float('inf')):
            continue

        r, c = current
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            neighbor = (nr, nc)

            if not (0 <= nr < ROWS and 0 <= nc < COLS):
                continue
            if WholeMap[nr][nc] == '#':
                continue
            if neighbor != goal and neighbor in blocked:
                continue

            tentative_g = current_g + 1
            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + abs(nr - goal[0]) + abs(nc - goal[1])
                heapq.heappush(open_set, (f_score, tentative_g, neighbor))

    return None

def genMap(numrooms=NUMROOMS, start_pos = None):
    Map = []
    floors = set()
    rooms = []

    # 1. Spawn Room 1 near the center to leave room on all sides
    r1_h, r1_w = ri(6, 10), ri(8, 14)
    if start_pos == None:
        r1_x = ROWS//2 - r1_h//2
        r1_y = COLS//2 - r1_w//2
    else:
        # Genetate map for new place
        entry_r, entry_c = start_pos
        floors.add((entry_r, entry_c))

        if entry_c == 0:
            r1_y = 0
            r1_x = max(0 , min(ROWS - r1_h, entry_r - r1_h // 2))
            if entry_r == 0:
                floors.add((1,0))
            elif entry_r == ROWS - 1:
                floors.add((ROWS - 2, 0))
        elif entry_c == COLS - 1:
            r1_y = COLS - r1_w
            r1_x = max(0 , min(ROWS - r1_h, entry_r - r1_h // 2))
            if entry_r == 0:
                floors.add((1, COLS - 1))
            elif entry_r == ROWS - 1:
                floors.add((ROWS - 2, COLS - 1))
        elif entry_r == 0:  # Entered North edge
            r1_x = 0
            r1_y = max(0, min(COLS - r1_w, entry_c - r1_w // 2))
            if entry_c == 0:
                floors.add((0, 1))
            elif entry_c == COLS - 1:
                floors.add((0, COLS - 2))
        elif entry_r == ROWS - 1:  # Entered South edge
            r1_x = ROWS - r1_h
            r1_y = max(0, min(COLS - r1_w, entry_c - r1_w // 2))
            if entry_c == 0:
                floors.add((ROWS - 1, 1))
            elif entry_c == COLS - 1:
                floors.add((ROWS - 1, COLS - 2))
 
    # Carve Room 1 floor tiles
    for r in range(r1_x + 1, r1_x + r1_h - 1):
        for c in range(r1_y + 1, r1_y + r1_w - 1):
            floors.add((r, c))

    rooms.append((r1_x, r1_y, r1_h, r1_w))

    # 2. Pick a random direction for the corridor
    directions = {
        'N': (-1, 0),
        'S': (1, 0),
        'W': (0, -1),
        'E': (0, 1)
    }

    for _ in range(numrooms - 1):
        prev_x, prev_y, prev_h, prev_w = random.choice(rooms)

        side = random.choice(['N', 'S', 'W', 'E'])
        dr, dc = directions[side]

        # Pick starting door position on Room 1's edge
        if side == 'N':
            start_r, start_c = prev_x, ri(prev_y + 1, prev_y + prev_w - 2)
        elif side == 'S':
            start_r, start_c = prev_x + prev_h - 1, ri(prev_y + 1, prev_y + prev_w - 2)
        elif side == 'W':
            start_r, start_c = ri(prev_x + 1, prev_x + prev_h - 2), prev_y
        else:  # 'E'
            start_r, start_c = ri(prev_x + 1, prev_x + prev_h - 2), prev_y + prev_w - 1

        # 3. Carve the Corridor
        corridor_len = ri(4, 8)
        curr_r, curr_c = start_r, start_c

        for _ in range(corridor_len):
            if 0 <= curr_r < ROWS and 0 <= curr_c < COLS:
                floors.add((curr_r, curr_c))
            curr_r += dr
            curr_c += dc

        # Essential Fix: Add the doorway tile into Room 2
        if 0 <= curr_r < ROWS and 0 <= curr_c < COLS:
            floors.add((curr_r, curr_c))

        # 4. Generate Room 2 attached to the corridor end
        r_h, r_w = ri(6, 10), ri(8, 14)

        if side == 'N':
            r_x = curr_r - r_h + 1
            r_y = curr_c - ri(1, r_w - 2)
        elif side == 'S':
            r_x = curr_r
            r_y = curr_c - ri(1, r_w - 2)
        elif side == 'W':
            r_x = curr_r - ri(1, r_h - 2)
            r_y = curr_c - r_w + 1
        else:  # 'E'
            r_x = curr_r - ri(1, r_h - 2)
            r_y = curr_c

        # Carve Room 2 floors
        for r in range(r_x + 1, r_x + r_h - 1):
            for c in range(r_y + 1, r_y + r_w - 1):
                if 0 <= r < ROWS and 0 <= c < COLS:
                    floors.add((r, c))

        rooms.append((r_x, r_y, r_h, r_w)) 
    
    # 5. Build walls around all floor tiles (Room 1, Corridor, and Room 2)
    walls = set()
    for r, c in floors:
        for adj_r in range(r - 1, r + 2):
            for adj_c in range(c - 1, c + 2):
                if (adj_r, adj_c) not in floors:
                    if 0 <= adj_r < ROWS and 0 <= adj_c < COLS:
                        walls.add((adj_r, adj_c))

    # 6. Render the map
    for i in range(ROWS):
        row = []
        for j in range(COLS):
            if (i, j) in walls:
                row.append('#')
            elif (i, j) in floors:
                row.append(random.choice(['.', ',']))
            else:
                row.append(' ')  # Empty outer space
        Map.append(row)

    return Map, floors

def spawnEnemies(num, fft, exlude_pos=None):
    enemy_dict = {}
    avalable_tiles = list(fft - {exlude_pos}) if exlude_pos else list(fft)

    for _ in range(num):
        if avalable_tiles:
            pos = random.choice(avalable_tiles)
            enemy_dict[pos] = ENEMY_MAX_HP
            avalable_tiles.remove(pos)
    return enemy_dict

def update_grid_layout(width, height, cols, rows, font_name="monospace"):
    """Calculates font size and padding offsets to center the grid."""
    max_char_w = width / cols
    max_char_h = height / rows

    font_size = int(max_char_h)

    while font_size > 1:
        font = pygame.font.SysFont(font_name, font_size)
        char_w, char_h = font.size("A")

        if char_w <= max_char_w and char_h <= max_char_h:
            break
        font_size -= 1
    else:
        font = pygame.font.SysFont(font_name, 1)
        char_w, char_h = font.size("A")

    # Calculate exact offsets to center the rendered grid on screen
    offset_x = (width - (cols * char_w)) // 2
    offset_y = (height - (rows * char_h)) // 2

    return font, char_w, char_h, offset_x, offset_y


# Initial calculation
font, char_width, char_height, offset_x, offset_y = update_grid_layout(
    WIDTH, HEIGHT, COLS, ROWS
)

# Colors
BACKGROUND = (30, 30, 10)
TEXT_COLOR = (200, 250, 250)
UI_COLOR = (255, 80, 80)

clock = pygame.time.Clock()
running = True

# Player starts in the exact middle grid coordinate
zone_pos = [0,0]
world = {}

playerpos = [ROWS // 2, COLS // 2]
WholeMap, fft = genMap()
enemy_dict = spawnEnemies(random.randrange(1, 20), fft, tuple(playerpos))
world[tuple(zone_pos)] = (WholeMap, fft, enemy_dict)

def change_zone(dz_r, dz_c, new_player_r, new_player_c):
    global WholeMap, fft, enemy_dict

    if not (0 <= new_player_r < ROWS and 0 <= new_player_c < COLS):
        return

    target_key = (zone_pos[0] + dz_r, zone_pos[1] + dz_c)

    if target_key in world:
        target_map, target_fft, _ = world[target_key]
        if (
            (new_player_r, new_player_c) not in target_fft
            or target_map[new_player_r][new_player_c] in ('#', ' ')
        ):
            return

    world[tuple(zone_pos)] = (WholeMap, fft, enemy_dict)

    zone_pos[0], zone_pos[1] = target_key
    playerpos[0] = new_player_r
    playerpos[1] = new_player_c

    
    if target_key in world:
        WholeMap, fft, enemy_dict = world[target_key]

    else:
        WholeMap, fft = genMap(start_pos=(new_player_r, new_player_c))
        enemy_dict = spawnEnemies(random.randrange(1,20), fft, (new_player_r, new_player_c))
        world[target_key] = (WholeMap, fft, enemy_dict)


def try_move(dr, dc):
    global player_hp
    new_r = playerpos[0] + dr
    new_c = playerpos[1] + dc
    # Changing zones 
    if new_r < 0:
        change_zone(-1, 0, ROWS - 1, playerpos[1])
    elif new_r >= ROWS:
        change_zone(1, 0, 0, playerpos[1])
    elif new_c < 0:
        change_zone(0, -1, playerpos[0], COLS - 1)
    elif new_c >= COLS:
        change_zone(0, 1, playerpos[0], 0)
    else:
        # Normal movement
        if (new_r, new_c) in enemy_dict:
            enemy_dict[(new_r, new_c)] -= 10 # Damage dealt to enemy
            # If enemy dies
            if enemy_dict[(new_r, new_c)] <= 0:
                del enemy_dict[(new_r, new_c)]

        elif WholeMap[new_r][new_c] != '#':
            playerpos[0] = new_r
            playerpos[1] = new_c

    
def enemy_move():
    global enemy_dict, player_hp
    new_enemy_dict = {} 

    target = tuple(playerpos)

    sorted_enemies = sorted(
        enemy_dict.items(),
        key=lambda item: abs(item[0][0] - target[0]) + abs(item[0][1] - target[1]),
    )
    remaining_enemies = set(enemy_dict.keys())

    for (r, c), hp in sorted_enemies:
        remaining_enemies.remove((r, c))
        blocked = set(new_enemy_dict.keys()) | remaining_enemies
        next_step = a_star((r, c), target, blocked)

        if next_step is not None:
            new_r, new_c = next_step
            if [new_r, new_c] == playerpos:
                player_hp = max(0, player_hp - 5)
            else:
                new_enemy_dict[(new_r, new_c)] = hp

        else:
            new_enemy_dict[(r, c)] = hp

    enemy_dict = new_enemy_dict

        
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Recalculate grid centering if screen size changes
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            (
                font,
                char_width,
                char_height,
                offset_x,
                offset_y,
            ) = update_grid_layout(WIDTH, HEIGHT, COLS, ROWS)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if player_hp > 0:
                moved = False
                if event.key in (pygame.K_UP, pygame.K_w, pygame.K_k):
                    try_move(-1, 0)
                    moved = True
                if event.key in (pygame.K_DOWN, pygame.K_s, pygame.K_j):
                    try_move(1, 0)
                    moved = True
                if event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_l):  
                    try_move(0, 1)
                    moved = True    
                if event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_h):
                    try_move(0, -1)
                    moved = True            

                if moved:
                    enemy_move()

            if event.key == pygame.K_SPACE:
                WholeMap, fft = genMap()
                enemy_dict = spawnEnemies(random.randrange(1,20), fft)
                player_hp = PLAYER_MAX_HP
                playerpos = [ROWS // 2, COLS // 2]
                world.clear()
                zone_pos = [0,0]
    

    screen.fill(BACKGROUND)
    # Render centered character grid
    for row in range(ROWS):
        for col in range(COLS):
            if [row, col] == playerpos:
                char = '@'
                TEXT_COLOR = (225, 28, 255)
            elif (row, col) in enemy_dict:
                char = 'e'
                TEXT_COLOR = (255, 80, 80)
            else:
                char = WholeMap[row][col]
                TEXT_COLOR = (200, 250, 250)

            char_surface = font.render(char, True, TEXT_COLOR)

            x = offset_x + (col * char_width)
            y = offset_y + (row * char_height)
            screen.blit(char_surface, (x, y))

    hp_text = f"HP: {player_hp}/{PLAYER_MAX_HP}, xy: {playerpos[0]},{playerpos[1]}, Zone: ({zone_pos[1]}, {-zone_pos[0]})"
    if player_hp <= 0:
        hp_text = "Game Over"

    ui_surface = font.render(hp_text, True, UI_COLOR)
    screen.blit(ui_surface, (20,20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
