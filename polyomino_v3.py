# pygame-based polyomino drawer (patched)
# Requires: pygame (pip install pygame)
# Run: python draw_v4.py
#
# This variant adds a user selection phase (console prompts)
# to choose:
#  - square board size (N x N), 6 <= N <= 20
#  - which polyomino class to use (tri/tet/pen/mix)
#  - color choice policy: 'unique' (u), 'random' (r), or 'same' (s)
#
# Color choice mapping:
# unique (u) - each distinct polyomino name is assigned a unique color
#                randomly from PALETTE and that color is used every time
#                that polyomino is placed (colors are drawn without reuse
#                until the palette is exhausted, then reshuffled).
# random (r) - each placement chooses a random color from PALETTE.
# same   (s) - a single random color is chosen and used for all placements.
#
# Placement is always random and stops when occupied squares reaches user selected value.
# After placement the program waits for either:
#   - 'R' restarts the script (re-run console prompts and placement)
#   - ESC quits and closes window
#
# All placements enforce no-overlap and in-bounds.
# Counts are updated in this order: place -> increment polyomino count -> increment square count.

import sys
import math
import random
import pygame

# ---------- Configuration ----------
WINDOW_SIZE = (1200, 800)
FPS = 60

GRID_CELL = 32
# Colors requested
LIGHT_SQUARE = (255, 255, 240)
DARK_SQUARE = (232, 200, 150)
GRID_COLOR = (102, 51, 0)
BG_COLOR = (32, 32, 32)
GRID_ORIGIN = (32, 32)  # top-left pixel of grid

# Defaults
DEFAULT_GRID_COLS = 20

# ---------- Sample polyomino definitions ----------
SAMPLE_POLYOMINOES = {
    "tri-I": [(0, 0), (1, 0), (2, 0)],
    "tri-L": [(0, 0), (0, 1), (1, 1)],
    "tet-I": [(0, 0), (0, 1), (0, 2), (0, 3)],
    "tet-L": [(0, 0), (0, 1), (0, 2), (1, 2)],
    "tet-O": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "tet-S": [(1, 0), (2, 0), (0, 1), (1, 1)],
    "tet-T": [(0, 1), (1, 1), (2, 1), (1, 0)],
    "pen-F": [(0,1), (1,0), (1,1), (1,2), (2,2)],
    "pen-I": [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)],
    "pen-L": [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0)],
    "pen-N": [(0, 0), (0, 1), (1, 1), (1, 2), (1, 3)],
    "pen-P": [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)],
    "pen-T": [(0,2), (1, 2), (2, 2), (1, 0), (1, 1)],
    "pen-U": [(0, 0), (0, 1), (1, 0), (2, 0), (2, 1)],
    "pen-V": [(0, 0), (0, 1), (0, 2), (1, 0), (2, 0)],
    "pen-W": [(0, 1), (0, 2), (1, 0), (1, 1), (2, 0)],
    "pen-X": [(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)],
    "pen-Y": [(0, 2), (1, 0), (1, 1), (1, 2), (1, 3)],
    "pen-Z": [(0,2), (1,0), (1,1), (1,2), (2,0)],
    "hex-01": [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5)],
    "hex-02": [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)],
    "hex-03": [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (4, 1)],
    "hex-04": [(0, 0), (1, 0), (2, 0), (2, 1), (3, 0), (4, 0)],
    "hex-05": [(0, 1), (1, 1), (2, 1), (3, 0), (3, 1), (4, 0)],
    "hex-06": [(0, 1), (1, 1), (2, 0), (2, 1), (3, 0), (4, 0)],
    "hex-07": [(0, 0), (1, 0), (2, 0), (3, 0), (3, 1), (4, 0)],
    "hex-08": [(0, 0), (0, 1), (1, 0), (1, 1), (2, 1), (3, 1)],
    "hex-09": [(0, 0), (0, 1), (1, 0), (2, 0), (3, 0), (3, 1)],
    "hex-10": [(0, 1), (1, 0), (1, 1), (2, 0), (3, 0), (3, 1)],
    "hex-11": [(0, 1), (1, 0), (1, 1), (2, 0), (2, 1), (3, 0)],
    "hex-12": [(0, 0), (1, 0), (1, 1), (2, 0), (2, 1), (3, 0)],
    "hex-13": [(0, 0), (0, 1), (1, 0), (2, 0), (2, 1), (3, 0)],
    "hex-14": [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (3, 1)],
    "hex-15": [(0, 0), (1, 0), (1, 1), (1, 2), (2, 1), (2, 2)],
    "hex-16": [(0, 1), (0, 2), (1, 0), (1, 1), (2, 1), (2, 2)],
    "hex-17": [(0, 0), (0, 1), (1, 0), (2, 0), (2, 1), (2, 2)],
    "hex-18": [(0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 2)],
    "hex-19": [(0, 1), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1)],
    "hex-20": [(0, 0), (0, 1), (0, 2), (1, 1), (2, 1), (2, 2)],
    "hex-21": [(0, 0), (1, 0), (1, 1), (2, 0), (2, 1), (2, 2)],
    "hex-22": [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2), (3, 1)],
    "hex-23": [(0, 1), (1, 1), (1, 2), (2, 0), (2, 1), (3, 1)],
    "hex-24": [(0, 1), (0, 2), (1, 1), (2, 1), (3, 0), (3, 1)],
    "hex-25": [(0, 1), (1, 1), (2, 0), (2, 1), (2, 2), (3, 2)],
    "hex-26": [(0, 2), (1, 2), (2, 1), (2, 2), (3, 0), (3, 1)],
    "hex-27": [(0, 2), (1, 1), (1, 2), (2, 0), (2, 1), (3, 0)],
    "hex-28": [(0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (3, 0)],
    "hex-29": [(0, 2), (1, 2), (2, 0), (2, 1), (2, 2), (3, 2)],
    "hex-30": [(0, 1), (0, 2), (1, 1), (2, 0), (2, 1), (3, 0)],
    "hex-31": [(0, 1), (0, 2), (1, 1), (2, 0), (2, 1), (3, 1)],
    "hex-32": [(0, 1), (1, 1), (2, 0), (2, 1), (2, 2), (3, 1)],
    "hex-33": [(0, 1), (1, 1), (2, 0), (2, 1), (3, 1), (3, 2)],
    "hex-34": [(0, 0), (0, 1), (0, 2), (1, 0), (2, 0), (3, 0)],
    "hex-35": [(0, 1), (1, 1), (2, 1), (3, 0), (3, 1), (3, 2)],
}

PALETTE = [
    (0, 0, 0),
    (0, 0, 128),
    (0, 0, 255),
    (0, 128, 0),
    (0, 128, 128),
    (0, 128, 255),
    (0, 255, 0),
    (0, 255, 128),
    (0, 255, 255),
    (128, 0, 0),
    (128, 0, 128),
    (128, 0, 255),
    (128, 128, 0),
    (128, 128, 128),
    (128, 128, 255),
    (128, 255, 0),
    (128, 255, 128),
    (128, 255, 255),
    (255, 0, 0),
    (255, 0, 128),
    (255, 0, 255),
    (255, 128, 0),
    (255, 128, 128),
    (255, 128, 255),
    (255, 255, 0),
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

def pick_color(name, color_choice, unique_color_map=None, shared_color=None):
    """
    Centralized color selection:
    - 'unique' reads from unique_color_map[name] if available (fallback random)
    - 'same' returns shared_color (fallback random)
    - otherwise returns a random palette color
    """
    if color_choice == "unique":
        if unique_color_map and name in unique_color_map:
            return unique_color_map[name]
        # fallback to random if not preassigned
        return random.choice(PALETTE)
    elif color_choice == "same":
        return shared_color if shared_color is not None else random.choice(PALETTE)
    else:
        return random.choice(PALETTE)

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
        """
        Draw checkerboard squares with lower-left square always the darker color.
        Grid origin is top-left; row index 'gy' goes from 0 (top) to rows-1 (bottom).
        For a cell at (gx, gy) we compute parity using (gx + (rows-1 - gy)) so that
        (0, rows-1) -> parity 0 (even) -> dark square.
        """
        ox, oy = self.origin
        cs = self.cell_size
        for gx in range(self.cols):
            for gy in range(self.rows):
                # parity so lower-left is dark
                parity = (gx + (self.rows - 1 - gy)) % 2
                color = DARK_SQUARE if parity == 0 else LIGHT_SQUARE
                px = ox + gx * cs
                py = oy + gy * cs
                rect = pygame.Rect(px, py, cs, cs)
                pygame.draw.rect(surface, color, rect)

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
        # Column/row labels are intentionally not rendered to avoid unnecessary cost.

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

# Determine pieces by class prefix
def pieces_for_class(choice_token):
    token = choice_token.lower()
    if token == "3":
        prefix = "tri"
    elif token == "4":
        prefix = "tet"
    elif token == "5":
        prefix = "pen"
    elif token == "6":
        prefix = "hex"
    else:
        prefix = None
    if prefix:
        return [(name, SAMPLE_POLYOMINOES[name]) for name in SAMPLE_POLYOMINOES if name.startswith(prefix)]
    else:
        return [(name, SAMPLE_POLYOMINOES[name]) for name in SAMPLE_POLYOMINOES]

# ---------- Main application ----------
def main():
    # Do not initialize pygame or open the window before console prompts.
    # The pygame init + display are performed after the user inputs so prompts are visible.
    while True:
        # Console configuration in required order
        grid_n = ask_int("Board size n x n (6..20)", 6, 20, DEFAULT_GRID_COLS)

        # Polyomino class prompt (user picks tri/tet/pen or mix)
        poly_choice_token = ask_choice("Polyomino class", ["3","4","5","6","9"], "6")

        # Color choice prompt: allow full word or first letter (u/r/s)
        raw_color = ask_choice("Colors", ["unique","random","same","u","r","s"], "random")
        # normalize
        if raw_color in ("u", "unique"):
            color_choice = "unique"
        elif raw_color in ("r", "random"):
            color_choice = "random"
        elif raw_color in ("s", "same"):
            color_choice = "same"
        else:
            color_choice = "random"

        # Now initialize pygame and create the window AFTER prompts so console isn't obscured.
        pygame.init()
        screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Polyomino Drawer")
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("Consolas", 16)
        # title_font = pygame.font.SysFont("Consolas", 20, bold=True)

        # Setup grid size locally
        grid_cols = grid_n
        grid_rows = grid_n

        board = Board(grid_cols, grid_rows, GRID_CELL, GRID_ORIGIN)

        # threshold (ceil 25%)
        target_squares = math.ceil(board.cols * board.rows * 0.30)

        # Build chosen piece list according to class token
        chosen = pieces_for_class(poly_choice_token)
        # chosen is list of (name, cells)

        # Prepare color structures according to color_choice
        unique_color_map = {}
        shared_color = None
        if color_choice == "unique":
            # Pre-assign unique colors to available polyomino names (for consistent preview)
            # This ensures each available name has a distinct color until palette is exhausted.
            # Implementation: shuffle PALETTE and pop colors; when exhausted reshuffle and continue.
            color_pool = PALETTE[:]
            random.shuffle(color_pool)
            for name, _ in chosen:
                if not color_pool:
                    color_pool = PALETTE[:]
                    random.shuffle(color_pool)
                unique_color_map[name] = color_pool.pop()
        elif color_choice == "same":
            shared_color = random.choice(PALETTE)
        # if color_choice == "random", no prep needed

        # Build a canonical poly_list for UI cycling (so TAB/1-9 can still show shapes)
        poly_list = []
        for i, (name, cells) in enumerate(chosen):
            # assign a default color for listing consistent with policy via pick_color
            color = pick_color(name, color_choice, unique_color_map, shared_color)
            poly_list.append(Polyomino(cells, color=color, name=name))

        if not poly_list:
            # fallback
            for i, (name, cells) in enumerate(SAMPLE_POLYOMINOES.items()):
                poly_list.append(Polyomino(cells, color=random.choice(PALETTE), name=name))

        current_index = 0
        # current_poly = poly_list[current_index]

        placed_polys = []
        placed_count = 0
        occupied_squares = 0

        # helper for placing and counting (strict no-overlap) - now uses Board API
        def try_place_and_record(poly_obj, gx, gy):
            nonlocal placed_count, occupied_squares
            # use Board.can_place for bounds/overlap check
            if not board.can_place(poly_obj, gx, gy):
                return False
            # place using Board.place_poly
            board.place_poly(poly_obj, gx, gy)
            # update counters
            placed_count += 1
            occupied_squares += len(poly_obj.cells)
            # record placed poly for future use (undo/replay/stats)
            placed_polys.append((Polyomino(poly_obj.cells, color=poly_obj.color, name=poly_obj.name), gx, gy))
            return True

        # Helper to produce the next piece (Polyomino object with appropriate color and randomized orientation)
        def get_next_piece_for_placement(randomize_orientation=True):
            # choose piece (name, cells) randomly from chosen pool
            name, cells = random.choice(chosen)
            # choose color per policy via centralized helper
            color = pick_color(name, color_choice, unique_color_map, shared_color)
            poly = Polyomino(cells, color=color, name=name)
            if randomize_orientation:
                poly = random_orientation(poly)
            return poly

        # ---------- Random placement logic (always run) ----------
        if not chosen:
            print("No polyominoes available for placement.")
        else:
            max_total_attempts = 8000
            total_attempts = 0
            # We'll repeatedly try to place pieces (multiple instances allowed)
            while occupied_squares < target_squares and total_attempts < max_total_attempts:
                total_attempts += 1
                # pick a piece according to selection rules (random from chosen)
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
                    try_gx = random.randint(0, max_gx)
                    try_gy = random.randint(0, max_gy)
                    if try_place_and_record(p, try_gx, try_gy):
                        placed = True
                        break
                # if not placed, continue
            if occupied_squares >= target_squares:
                print(f"Random placement complete.")
                print(f"Placed {placed_count} pieces, occupied squares: {occupied_squares}/{target_squares}")
            else:
                print(f"Random placement stopped after {total_attempts} attempts. Placed {placed_count} pieces, occupied squares: {occupied_squares}/{target_squares}")

        # After placement, enter a waiting loop: user can press 'r' to repeat or ESC / close to quit.
        waiting = True
        restart_requested = False

        while waiting:
            dt = clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_r:
                        # 'Repeat' requested: restart the entire script (go back to input prompts)
                        restart_requested = True
                        waiting = False
                        break
                    elif event.key == pygame.K_TAB:
                        if poly_list:
                            current_index = (current_index + 1) % len(poly_list)
                #            base = poly_list[current_index]
                #            current_poly = Polyomino(base.cells, color=base.color, name=base.name)
                    elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                        board.cell_size = clamp(board.cell_size + 2, 8, 80)
                    elif event.key == pygame.K_MINUS or event.key == pygame.K_UNDERSCORE:
                        board.cell_size = clamp(board.cell_size - 2, 8, 80)
                    elif pygame.K_1 <= event.key <= pygame.K_9:
                        idx = event.key - pygame.K_1
                        if idx < len(poly_list):
                            current_index = idx
                #            base = poly_list[current_index]
                #            current_poly = Polyomino(base.cells, color=base.color, name=base.name)
                # mouse movement / clicks previously used for preview; preview removed so ignore mouse motion/button effects here

            # Drawing
            screen.fill(BG_COLOR)
            board.draw_background(screen)
            board.draw_placed(screen)
            board.draw_grid_lines(screen, font)

            ui_x = GRID_ORIGIN[0] + board.cell_size * board.cols + 48
            ui_y = GRID_ORIGIN[1]
            ui_y += 32

            ui_y += 8
            summary = [
                f"board: {board.cols} x {board.rows}",
                f"class: {poly_choice_token}",
                f"colors: {color_choice}",
                f"targets: {placed_count}",
                f"squares: {occupied_squares}",
                "",
                f"press 'r' to repeat",
                f"press ESC to Quit",
            ]
            for line in summary:
                txt = font.render(line, True, (200,200,200))
                screen.blit(txt, (ui_x, ui_y))
                ui_y += 18

            pygame.display.flip()

        # repeat = clean up and loop back to the outer while True to re-run prompts & placement
        if restart_requested:
            pygame.quit()  # close window so prompts are visible again
            continue
        else:
            # normally unreachable because quit exits; safeguard
            break

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()