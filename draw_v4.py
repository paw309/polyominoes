# pygame-based polyomino drawer (patched)
# Requires: pygame (pip install pygame)
# Run: python draw_v2.py
#
# This variant adds a user selection phase (console prompts)
# to choose:
#  - square board size (N x N), 8 <= N <= 16
#  - which polyomino class to use (tri/tet/pen/mix)
#  - placement mode: random or user placement (interactive)
#  - degree of difficulty: integer 1..7 (controls selection & coloring rules)
#
# Degree mapping (1..7) controls which pieces are selected and color policy:
# 1) user-selected class, randomly choose any piece from that class each placement, use a different color each placement
# 2) user-selected class, cycle through class, use a different color each placement
# 3) user-selected class, cycle through class), use a random color each placement
# 4) user-selected class, cycle through class, use same color each placement
# 5) mixed classes, randomly choose any piece, use a different color each placement
# 6) mixed classes, randomly choose any piece, use a random color each placement
# 7) mixed classes, randomly choose any piece, use same color each placement
#
# Placement stops when occupied squares >= ceil(rows * cols * 0.2).
# All placements (random and interactive) enforce no-overlap and in-bounds.
# Counts are updated in this order: place -> increment polyomino count -> increment square count.

import sys
import math
import random
import pygame

# ---------- Configuration ----------
WINDOW_SIZE = (1200, 700)
FPS = 60

GRID_CELL = 30
GRID_COLOR = (200, 200, 200)
BG_COLOR = (30, 30, 30)
GRID_ORIGIN = (60, 60)  # top-left pixel of grid

# Defaults (may be overridden by user selection)
DEFAULT_GRID_COLS = 16
DEFAULT_GRID_ROWS = 16

# ---------- Sample polyomino definitions ----------
SAMPLE_POLYOMINOES = {
    "triomino-I": [(0, 0), (1, 0), (2, 0)],
    "triomino-L": [(0, 0), (0, 1), (1, 1)],
    "tetromino-I": [(0, 0), (0, 1), (0, 2), (0, 3)],
    "tetromino-L": [(0, 0), (0, 1), (0, 2), (1, 2)],
    "tetromino-O": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "tetromino-S": [(1, 0), (2, 0), (0, 1), (1, 1)],
    "tetromino-T": [(0, 1), (1, 1), (2, 1), (1, 0)],
    "pentomino-F": [(0,1), (1,0), (1,1), (1,2), (2,2)],
    "pentomino-I": [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)],
    "pentomino-L": [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0)],
    "pentomino-N": [(0, 0), (0, 1), (1, 1), (1, 2), (1, 3)],
    "pentomino-P": [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)],
    "pentomino-T": [(0,2), (1, 2), (2, 2), (1, 0), (1, 1)],
    "pentomino-U": [(0, 0), (0, 1), (1, 0), (2, 0), (2, 1)],
    "pentomino-V": [(0, 0), (0, 1), (0, 2), (1, 0), (2, 0)],
    "pentomino-W": [(0, 1), (0, 2), (1, 0), (1, 1), (2, 0)],
    "pentomino-X": [(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)],
    "pentomino-Y": [(0, 2), (1, 0), (1, 1), (1, 2), (1, 3)],
    "pentomino-Z": [(0,2), (1,0), (1,1), (1,2), (2,0)],
}

PALETTE = [
    (65, 105, 225),
    (255, 99, 71),
    (191, 255, 0),
    (80, 180, 255),
    (147, 112, 219),
    (220, 20, 60),
    (0, 255, 255),
    (255, 200, 50),
    (50, 205, 50),
    (124, 252, 0),
    (255, 0, 255),
    (255, 20, 147),
    (255, 127, 80),
    (100, 40, 160),
    (186, 85, 211),
    (255, 140, 0),
    (210, 180, 140),
    (0, 255, 127),
    (64, 224, 208),
]

# ---------- Polyomino helper functions ----------
def normalize(cells):
    if not cells:
        return cells
    minx = min(c[0] for c in cells)
    miny = min(c[1] for c in cells)
    return [(x - minx, y - miny) for (x, y) in cells]

def rotate90(cells):
    rotated = [(y, -x) for (x, y) in cells]
    return normalize(rotated)

def flip_horizontal(cells):
    flipped = [(-x, y) for (x, y) in cells]
    return normalize(flipped)

class Polyomino:
    def __init__(self, cells, color=None, name=None):
        self.cells = normalize(cells)
        self.name = name or "poly"
        self.color = color or random.choice(PALETTE)

    def rotated(self):
        return Polyomino(rotate90(self.cells), color=self.color, name=self.name + "_rot")

    def flipped(self):
        return Polyomino(flip_horizontal(self.cells), color=self.color, name=self.name + "_flip")

    def bounding(self):
        if not self.cells:
            return 0, 0
        maxx = max(x for x, _ in self.cells)
        maxy = max(y for _, y in self.cells)
        return maxx + 1, maxy + 1

class Board:
    def __init__(self, cols, rows, cell_size, origin):
        self.cols = cols
        self.rows = rows
        self.cell_size = cell_size
        self.origin = origin
        self.grid = {}  # (x,y) -> color

    def to_pixel(self, gx, gy):
        ox, oy = self.origin
        return ox + gx * self.cell_size, oy + gy * self.cell_size

    def draw_background(self, surface):
        ox, oy = self.origin
        cs = self.cell_size
        grid_rect = pygame.Rect(ox - 1, oy - 1, cs * self.cols + 2, cs * self.rows + 2)
        pygame.draw.rect(surface, (255, 255, 230), grid_rect)

    def draw_grid_lines(self, surface, font=None):
        ox, oy = self.origin
        cs = self.cell_size
        for x in range(self.cols + 1):
            start = (ox + x * cs, oy)
            end = (ox + x * cs, oy + self.rows * cs)
            pygame.draw.line(surface, GRID_COLOR, start, end, 1)
        for y in range(self.rows + 1):
            start = (ox, oy + y * cs)
            end = (ox + self.cols * cs, oy + y * cs)
            pygame.draw.line(surface, GRID_COLOR, start, end, 1)
        if font:
            for x in range(self.cols):
                px, py = self.to_pixel(x, 0)
                label = font.render(str(x), True, (160,160,160))
                surface.blit(label, (px + 2, oy - 18))
            for y in range(self.rows):
                px, py = self.to_pixel(0, y)
                label = font.render(str(y), True, (160,160,160))
                surface.blit(label, (ox - 26, py + 2))

    def can_place(self, poly, gx, gy):
        for x, y in poly.cells:
            tx = gx + x
            ty = gy + y
            if not (0 <= tx < self.cols and 0 <= ty < self.rows):
                return False
            if (tx, ty) in self.grid:
                return False
        return True

    def place_poly(self, poly, gx, gy):
        for x, y in poly.cells:
            tx = gx + x
            ty = gy + y
            if 0 <= tx < self.cols and 0 <= ty < self.rows:
                self.grid[(tx, ty)] = poly.color

    def draw_placed(self, surface):
        for (x, y), color in self.grid.items():
            px, py = self.to_pixel(x, y)
            rect = pygame.Rect(px+1, py+1, self.cell_size-1, self.cell_size-1)
            pygame.draw.rect(surface, color, rect)

    def clear(self):
        self.grid.clear()

# ---------- Drawing helpers ----------
def draw_polyomino_preview(surface, board, poly, gx, gy, alpha=180):
    for x, y in poly.cells:
        tx = gx + x
        ty = gy + y
        if 0 <= tx < board.cols and 0 <= ty < board.rows:
            px, py = board.to_pixel(tx, ty)
            rect = pygame.Rect(px+1, py+1, board.cell_size-1, board.cell_size-1)
            try:
                preview_color = poly.color + (alpha,)
                s = pygame.Surface((board.cell_size-1, board.cell_size-1), pygame.SRCALPHA)
                s.fill(preview_color)
                surface.blit(s, (px+1, py+1))
            except Exception:
                pygame.draw.rect(surface, poly.color, rect)

def grid_from_pixel(board, px, py):
    ox, oy = board.origin
    cs = board.cell_size
    gx = (px - ox) // cs
    gy = (py - oy) // cs
    return gx, gy

def clamp(n, a, b):
    return max(a, min(b, n))

# ---------- User selection (console) ----------
def ask_int(prompt, min_v, max_v, default):
    while True:
        try:
            raw = input(f"{prompt} [{default}]: ").strip()
        except EOFError:
            return default
        if raw == "":
            return default
        try:
            v = int(raw)
            if v < min_v or v > max_v:
                print(f"Please enter an integer between {min_v} and {max_v}.")
                continue
            return v
        except ValueError:
            print("Invalid integer, try again.")

def ask_choice(prompt, choices, default):
    choices_str = "/".join(choices)
    while True:
        try:
            raw = input(f"{prompt} ({choices_str}) [{default}]: ").strip().lower()
        except EOFError:
            return default
        if raw == "":
            return default
        if raw in choices:
            return raw
        print("Invalid choice, try again.")

def random_orientation(poly):
    p = poly
    rotates = random.randint(0, 3)
    for _ in range(rotates):
        p = p.rotated()
    if random.choice([True, False]):
        p = p.flipped()
    return Polyomino(p.cells, color=poly.color, name=poly.name)

# Color pool generator for "different color each placement" policy
class ColorPool:
    def __init__(self, palette):
        self.palette = list(palette)
        self.pool = []
        self._refill()

    def _refill(self):
        self.pool = self.palette[:]
        random.shuffle(self.pool)

    def next(self):
        if not self.pool:
            self._refill()
        return self.pool.pop()

# Piece cycling helper for "use every piece in class" policy
class PieceCycle:
    def __init__(self, pieces):
        self.pieces = list(pieces)
        self.pool = []
        self._refill()

    def _refill(self):
        self.pool = self.pieces[:]
        random.shuffle(self.pool)

    def next(self):
        if not self.pool:
            self._refill()
        return self.pool.pop()

# Determine pieces by class prefix
def pieces_for_class(choice_token):
    token = choice_token.lower()
    if token == "tri":
        prefix = "triomino"
    elif token == "tet":
        prefix = "tetromino"
    elif token == "pen":
        prefix = "pentomino"
    else:
        prefix = None
    if prefix:
        return [(name, SAMPLE_POLYOMINOES[name]) for name in SAMPLE_POLYOMINOES if name.startswith(prefix)]
    else:
        return [(name, SAMPLE_POLYOMINOES[name]) for name in SAMPLE_POLYOMINOES]

# ---------- Main application ----------
def main():
#    print("Polyomino Drawer - configuration")
    grid_n = ask_int("Board size n x n (8..20)", 8, 20, DEFAULT_GRID_COLS)
    poly_choice_token = ask_choice("Polyomino class", ["tri","tet","pen","mix"], "pen")
    placement_choice = ask_choice("Placement mode", ["random", "user"], "random")
    # replace color mode input with degree of difficulty (1..7)
    degree = ask_int("Degree of difficulty (1..7)", 1, 7, 4)

    # Setup grid size locally
    grid_cols = grid_n
    grid_rows = grid_n

    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Polyomino Drawer")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Consolas", 16)
    title_font = pygame.font.SysFont("Consolas", 20, bold=True)

    board = Board(grid_cols, grid_rows, GRID_CELL, GRID_ORIGIN)

    # threshold (ceil 20%)
    target_squares = math.ceil(board.cols * board.rows * 0.2)

    # Build chosen piece list according to class token
    chosen = pieces_for_class(poly_choice_token)
    # chosen is list of (name, cells)

    # Prepare selection & color policy according to degree
    # Determine whether to operate on selected class only or mixed
    def degree_uses_class_only(deg):
        return deg in (1,2,3,4)

    # For degrees 1-4, use the user-selected class; for 5-7, use mixed (all)
    if degree_uses_class_only(degree):
        pool_entries = chosen[:]  # list of (name, cells)
    else:
        # mixed: all pieces
        pool_entries = [(name, SAMPLE_POLYOMINOES[name]) for name in SAMPLE_POLYOMINOES]

    # For "use every piece" degrees: 2,3,4
    use_every_piece = degree in (2,3,4)
    # For "random piece each time" degrees: 1,5,6,7 (and others not in use_every)
    # Color policies:
    color_policy = None
    #  - "different": different color each placement (no immediate repeats) -> ColorPool
    #  - "random": random.choice every placement
    #  - "same": single shared color for all placements
    if degree in (1,2,5):
        color_policy = "different"
    elif degree in (3,6):
        color_policy = "random"
    elif degree in (4,7):
        color_policy = "same"
    else:
        color_policy = "random"

    # Prepare color and piece cycling structures
    color_pool = ColorPool(PALETTE) if color_policy == "different" else None
    shared_color = None
    if color_policy == "same":
        shared_color = random.choice(PALETTE)

    piece_cycle = PieceCycle(pool_entries) if use_every_piece else None

    # Build a canonical poly_list for UI cycling (so TAB/1-9 can still show shapes)
    poly_list = []
    for i, (name, cells) in enumerate(pool_entries):
        # assign a default color for listing (not authoritative for actual placements if policy overrides)
        color = random.choice(PALETTE) if color_policy != "same" else shared_color
        poly_list.append(Polyomino(cells, color=color, name=name))

    if not poly_list:
        # fallback
        for i, (name, cells) in enumerate(SAMPLE_POLYOMINOES.items()):
            poly_list.append(Polyomino(cells, color=random.choice(PALETTE), name=name))

    current_index = 0
    current_poly = poly_list[current_index]

    # piece position in grid coords
    piece_gx = board.cols // 2
    piece_gy = board.rows // 2

    placed_polys = []
    placed_count = 0
    occupied_squares = 0

    # helper for placing and counting (strict no-overlap)
    def try_place_and_record(poly_obj, gx, gy):
        nonlocal placed_count, occupied_squares
        abs_positions = []
        for x, y in poly_obj.cells:
            tx = gx + x
            ty = gy + y
            if not (0 <= tx < board.cols and 0 <= ty < board.rows):
                return False
            abs_positions.append((tx, ty))
        # ensure no overlap
        for pos in abs_positions:
            if pos in board.grid:
                return False
        # 1) place
        for pos in abs_positions:
            board.grid[pos] = poly_obj.color
        # 2) increment poly count
        placed_count += 1
        # 3) increment squares count
        occupied_squares += len(abs_positions)
        # record
        placed_polys.append((Polyomino(poly_obj.cells, color=poly_obj.color, name=poly_obj.name), gx, gy))
        return True

    # Helper to produce the next piece (Polyomino object with appropriate color and randomized orientation)
    def get_next_piece_for_placement(randomize_orientation=True):
        # choose piece (name, cells)
        if use_every_piece:
            name, cells = piece_cycle.next()
        else:
            name, cells = random.choice(pool_entries)
        # choose color
        if color_policy == "different":
            color = color_pool.next()
        elif color_policy == "random":
            color = random.choice(PALETTE)
        else:  # same
            color = shared_color
        poly = Polyomino(cells, color=color, name=name)
        if randomize_orientation:
            poly = random_orientation(poly)
        return poly

    # ---------- Random placement logic (allow repeated instances to reach coverage) ----------
    if placement_choice == "random":
        pool = pool_entries[:]
        if not pool:
            print("No polyominoes available for random placement.")
        else:
            MAX_TOTAL_ATTEMPTS = 8000
            total_attempts = 0
            # We'll repeatedly try to place pieces (multiple instances allowed)
            while occupied_squares < target_squares and total_attempts < MAX_TOTAL_ATTEMPTS:
                total_attempts += 1
                # pick a piece according to degree rules
                p = get_next_piece_for_placement(randomize_orientation=True)
                # try multiple random positions for this piece
                bw, bh = p.bounding()
                max_gx = board.cols - bw
                max_gy = board.rows - bh
                if max_gx < 0 or max_gy < 0:
                    # piece too big
                    continue
                placed = False
                # small inner attempts to find a valid non-overlapping place for this piece
                for _ in range(200):
                    gx = random.randint(0, max_gx)
                    gy = random.randint(0, max_gy)
                    if try_place_and_record(p, gx, gy):
                        placed = True
                        break
                # if not placed, continue; pool/cycle will move on naturally
            if occupied_squares >= target_squares:
                print(f"Random placement complete.")
                print(f"Placed {placed_count} pieces, occupied squares: {occupied_squares}/{target_squares}")
            else:
                print(f"Random placement stopped after {total_attempts} attempts. Placed {placed_count} pieces, occupied squares: {occupied_squares}/{target_squares}")

    running = True
    show_instructions = True

    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_RIGHT:
                    piece_gx = clamp(piece_gx + 1, -10, board.cols + 10)
                elif event.key == pygame.K_LEFT:
                    piece_gx = clamp(piece_gx - 1, -10, board.cols + 10)
                elif event.key == pygame.K_DOWN:
                    piece_gy = clamp(piece_gy + 1, -10, board.rows + 10)
                elif event.key == pygame.K_UP:
                    piece_gy = clamp(piece_gy - 1, -10, board.rows + 10)

                elif event.key == pygame.K_r:
                    current_poly = current_poly.rotated()
                elif event.key == pygame.K_f:
                    current_poly = current_poly.flipped()
                elif event.key == pygame.K_TAB:
                    # cycle polyomino in UI list
                    current_index = (current_index + 1) % len(poly_list)
                    base = poly_list[current_index]
                    current_poly = Polyomino(base.cells, color=base.color, name=base.name)
                elif event.key == pygame.K_SPACE:
                    if occupied_squares >= target_squares:
                        print("Target coverage reached; no more placements allowed.")
                    else:
                        # For interactive placement we follow the degree rules:
                        # get a piece (we won't randomize orientation here to give user control, but we'll randomize if degree picks random piece)
                        # Use orientation randomization for random selection degrees; for "use every piece" also use randomized orientation for variety.
                        p = get_next_piece_for_placement(randomize_orientation=True)
                        if not try_place_and_record(p, piece_gx, piece_gy):
                            print("Cannot place piece here (overlap or out-of-bounds).")

                elif event.key == pygame.K_c:
                    board.clear()
                    placed_polys.clear()
                    placed_count = 0
                    occupied_squares = 0
                    # reset pools
                    color_pool = ColorPool(PALETTE) if color_policy == "different" else color_pool
                    piece_cycle = PieceCycle(pool_entries) if use_every_piece else piece_cycle
                elif event.key == pygame.K_i:
                    show_instructions = not show_instructions
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    board.cell_size = clamp(board.cell_size + 2, 8, 80)
                elif event.key == pygame.K_MINUS or event.key == pygame.K_UNDERSCORE:
                    board.cell_size = clamp(board.cell_size - 2, 8, 80)

                # number keys to choose shape directly (UI)
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    idx = event.key - pygame.K_1
                    if idx < len(poly_list):
                        current_index = idx
                        base = poly_list[current_index]
                        current_poly = Polyomino(base.cells, color=base.color, name=base.name)

            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                gx, gy = grid_from_pixel(board, mx, my)
                piece_gx, piece_gy = gx, gy

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left click places
                    mx, my = event.pos
                    gx, gy = grid_from_pixel(board, mx, my)
                    if occupied_squares >= target_squares:
                        print("Target coverage reached; no more placements allowed.")
                    else:
                        p = get_next_piece_for_placement(randomize_orientation=True)
                        if not try_place_and_record(p, gx, gy):
                            print("Cannot place piece here (overlap or out-of-bounds).")
                elif event.button == 3:  # right click rotate CW
                    current_poly = current_poly.rotated()
                elif event.button == 2:  # middle click flip
                    current_poly = current_poly.flipped()

        # Drawing
        screen.fill(BG_COLOR)
        board.draw_background(screen)
        board.draw_placed(screen)
        board.draw_grid_lines(screen, font)

        # draw preview: show current_poly (UI) at mouse even though placement may follow degree rules
        draw_polyomino_preview(screen, board, current_poly, piece_gx, piece_gy)

        # draw UI
        ui_x = GRID_ORIGIN[0] + board.cell_size * board.cols + 48
        ui_y = GRID_ORIGIN[1]
        ui_y += 34

        controls = [
            "Controls:",
            "Move: mouse / arrow keys",
            "Place: left click or SPACE",
            "Rotate: R or Right-click",
            "Flip: F or Middle-click",
            "Next piece: TAB",
            "Pick 1-9: choose piece",
            "Clear: C",
            "Zoom: +/-",
            "Toggle help: I",
            "Quit: ESC",
        ]
        for line in controls:
            txt = font.render(line, True, (180,180,180))
            screen.blit(txt, (ui_x, ui_y))
            ui_y += 18


        ui_y += 8
        summary = [
            f"Board: {board.cols} x {board.rows}",
            f"Class: {poly_choice_token}",
            f"Placement: {placement_choice}",
            f"Degree: {degree}",
            f"Placed pieces: {placed_count}",
            f"Occupied squares: {occupied_squares} / {target_squares}",
        ]
        for line in summary:
            txt = font.render(line, True, (200,200,200))
            screen.blit(txt, (ui_x, ui_y))
            ui_y += 18

        if show_instructions:
            instructions = [
            #    "Left click to snap/place polyomino at that grid cell.",
            #    "Use +/- to change grid zoom (cell size).",
            ]
            iy = GRID_ORIGIN[1] + board.rows * board.cell_size + 12
            for line in instructions:
                txt = font.render(line, True, (200,200,200))
                screen.blit(txt, (GRID_ORIGIN[0], iy))
                iy += 18

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()