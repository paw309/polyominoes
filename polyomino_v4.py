# pygame-based polyomino drawer (modified for GUI menu)
# Requires pygame (pip install pygame)
#
# Placement happens when user clicks the blue "start" button
# Menu remains visible but is disabled while a layout is shown
# only "repeat" and "exit" remain active then.

import sys
import math
import random
import pygame

# ---------- Configuration ----------
WINDOW_SIZE = (1200, 720)
FPS = 60

GRID_CELL = 36
# Colors requested
LIGHT_SQUARE = (255, 255, 240)
DARK_SQUARE = (232, 200, 150)
GRID_COLOR = (102, 51, 0)
BG_COLOR = (32, 32, 32)
GRID_ORIGIN = (32, 32)  # kept for backwards compatibility if needed

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
    (0, 0, 128),
    (0, 0, 255),
    (0, 64, 64),
    (0, 64, 192),
    (0, 128, 0),
    (0, 128, 128),
    (0, 128, 192),
    (0, 128, 255),
    (0, 192, 0),
    (0, 192, 192),
    (0, 192, 255),
    (0, 255, 0),
    (0, 255, 128),
    (0, 255, 255),
    (128, 0, 0),
    (128, 0, 128),
    (128, 0, 192),
    (128, 0, 255),
    (128, 64, 192),
    (128, 192, 64),
    (128, 192, 192),
    (128, 128, 0),
    (128, 128, 255),
    (128, 255, 0),
    (128, 255, 192),
    (128, 255, 255),
    (255, 0, 0),
    (255, 0, 128),
    (255, 0, 255),
    (255, 64, 64),
    (255, 64, 192),
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


class Polyomino:
    def __init__(self, cells, color=None, name=None):
        self.cells = normalize(cells)
        self.name = name or "poly"
        self.color = color or random.choice(PALETTE)

    def rotated(self):
        return Polyomino(rotate90(self.cells), color=self.color, name=self.name)

    def flipped(self):
        return Polyomino(flip_horizontal(self.cells), color=self.color, name=self.name)

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

    def draw_grid_lines(self, surface):
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

def clamp(n, a, b):
    return max(a, min(b, n))

# ---------- User selection helpers (moved to GUI) ----------
def random_orientation(poly):
    p = poly
    rotates = random.randint(0, 3)
    for _ in range(rotates):
        p = p.rotated()
    if random.choice([True, False]):
        p = p.flipped()
    return Polyomino(p.cells, color=poly.color, name=poly.name)

# Determine shapes by class prefix
def shapes_for_class(choice_token):
    token = str(choice_token).lower()
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

# ---------- Main application (GUI-driven) ----------
def main():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Polyomino Drawer (GUI menu)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Consolas", 16)

    # Initial board defaults (editable in GUI)
    grid_cols = DEFAULT_GRID_COLS
    grid_rows = DEFAULT_GRID_COLS
    # initial origin is arbitrary; we'll compute and set the true origin every frame
    board = Board(grid_cols, grid_rows, GRID_CELL, GRID_ORIGIN)

    # GUI menu selection options and defaults
    menu_items = [
        # label, possible values list, current index
        ("piece", ["knight", "fairy"], 0),  # default 'knight'
        # 'board' will be numeric 6..20; store as list of ints for cycling
        ("board", [i for i in range(6, 25)], 0),
        ("shapes", ["triomino", "tetromino", "pentomino", "hexomino", "mixed"], 2),  # default pentomino
        ("density", ["35%", "30%", "25%", "20%", "15%", "10%"], 2),  # default '25%'
        ("colors", ["unique", "random", "same"], 1),  # default random
    ]

    # compute initial index for board default properly
    for idx, v in enumerate(menu_items[1][1]):
        if v == DEFAULT_GRID_COLS:
            menu_items[1] = (menu_items[1][0], menu_items[1][1], idx)
            break

    # store button rects to detect clicks
    widget_rects = {}  # keys: ("minus", i), ("plus", i), "start", "repeat", "exit"

    # state
    placed_polys = []
    placed_count = 0
    occupied_squares = 0
    waiting_for_start = True  # placement hasn't been run yet
    layout_shown = False  # true while a placement is visible; menu disabled except repeat/exit

    # color mapping state for placements (recomputed when placement runs)
    unique_color_map = {}
    shared_color = None
    color_pool = None

    # current selections / board size used by placement; update before running placement
    def get_current_selections():
        sel = {}
        for label, values, idx in menu_items:
            sel[label] = values[idx]
        return sel

    current_selections = get_current_selections()
    current_board_size = int(current_selections["board"])

    def compute_density_from_index(idx):
        # idx 0-> '35%' corresponds to density_choice 1 . 6 mapping originally
        density_choice = idx + 1
        return 0.4 - (density_choice * 0.05)

    # Placement routine (runs when start clicked)
    def run_placement():
        nonlocal board, placed_polys, placed_count, occupied_squares
        nonlocal unique_color_map, shared_color, color_pool, layout_shown, waiting_for_start
        nonlocal current_board_size, current_selections

        # reset board & counters
        # origin is not important here; main loop will recompute the on-screen origin
        board = Board(current_board_size, current_board_size, GRID_CELL, GRID_ORIGIN)
        board.clear()
        placed_polys = []
        placed_count = 0
        occupied_squares = 0

        # prepare chosen shapes list according to shapes selection token
        shapes_choice = current_selections["shapes"]
        shapes_token = {"triomino": "3", "tetromino": "4", "pentomino": "5", "hexomino": "6", "mixed": "9"}[shapes_choice]
        chosen = shapes_for_class(shapes_token)
        if not chosen:
            return

        # color setup
        unique_color_map = {}
        shared_color = None
        color_pool = None
        color_choice = current_selections["colors"]
        if color_choice == "unique":
            color_pool = PALETTE[:]
            random.shuffle(color_pool)
        elif color_choice == "same":
            shared_color = random.choice(PALETTE)

        # threshold
        density = compute_density_from_index(menu_items[3][2])
        target_squares = math.ceil(board.cols * board.rows * density)

        # placement loop (same logic as original)
        max_total_attempts = 8000
        total_attempts = 0
        while occupied_squares < target_squares and total_attempts < max_total_attempts:
            total_attempts += 1
            # pick a shape and color
            name, cells = random.choice(chosen)
            if color_choice == "unique":
                color = unique_color_map.get(name)
                if color is None:
                    if not color_pool:
                        color_pool = PALETTE[:]
                        random.shuffle(color_pool)
                    color = color_pool.pop()
                    unique_color_map[name] = color
            elif color_choice == "random":
                color = random.choice(PALETTE)
            else:
                color = shared_color
            p = Polyomino(cells, color=color, name=name)
            p = random_orientation(p)
            bw, bh = p.bounding()
            max_gx = board.cols - bw
            max_gy = board.rows - bh
            if max_gx < 0 or max_gy < 0:
                continue
            for _ in range(200):
                try_gx = random.randint(0, max_gx)
                try_gy = random.randint(0, max_gy)
                if board.can_place(p, try_gx, try_gy):
                    board.place_poly(p, try_gx, try_gy)
                    placed_count += 1
                    occupied_squares += len(p.cells)
                    placed_polys.append((p, try_gx, try_gy))
                    break

        # done: show layout and disable menu
        layout_shown = True
        waiting_for_start = False

    # Main loop
    while True:
        clock.tick(FPS)
        screen.fill(BG_COLOR)

        # --- compute message box and board origin/layout first ---
        # message box is pinned one GRID_CELL from left and top of game window
        margin = GRID_CELL
        msg_left = margin
        msg_top = margin
        msg_width = GRID_CELL * 10
        msg_right = msg_left + msg_width
        msg_bottom = WINDOW_SIZE[1] - margin  # one GRID_CELL margin from bottom
        msg_height = msg_bottom - msg_top
        msg_rect = pygame.Rect(msg_left, msg_top, msg_width, msg_height)
        # fill message box background
        pygame.draw.rect(screen, LIGHT_SQUARE, msg_rect)

        # remaining area for the board: to the right of the message box, with a one GRID_CELL margin
        area_left = msg_right + margin
        area_top = margin
        area_right = WINDOW_SIZE[0] - margin
        area_bottom = WINDOW_SIZE[1] - margin
        area_width = area_right - area_left
        area_height = area_bottom - area_top

        # compute board pixel size and center it in remaining area while preserving a one-GRID_CELL margin
        board_pixel_w = board.cols * board.cell_size
        board_pixel_h = board.rows * board.cell_size

        origin_x = area_left + (area_width - board_pixel_w) // 2
        origin_y = area_top + (area_height - board_pixel_h) // 2

        # clamp to ensure the board origin does not violate the left/top margin or go beyond the right/bottom margin
        origin_x = max(area_left, min(origin_x, area_right - board_pixel_w))
        origin_y = max(area_top, min(origin_y, area_bottom - board_pixel_h))

        board.origin = (origin_x, origin_y)

        # draw board background and placed polys (board origin has been set to the centered position)
        board.draw_background(screen)
        board.draw_placed(screen)
        board.draw_grid_lines(screen)

        # Prepare layout metrics for menu items (inside message box)
        # All messages begin one GRID_CELL from left of message box
        text_x = msg_left + GRID_CELL
        first_line_y = msg_top + GRID_CELL
        line_spacing = GRID_CELL * 0.5  # spacing between lines
        font_height = font.get_linesize()
        line_height = font_height + line_spacing

        # Compute maximum label width (to align minus buttons)
        label_texts = [label for (label, _, _) in menu_items]
        label_surfaces = [font.render(l + ":", True, (0, 0, 0)) for l in label_texts]
        label_widths = [s.get_width() for s in label_surfaces]
        max_label_width = max(label_widths) if label_widths else 0

        # positions:
        minus_x = text_x + max_label_width + GRID_CELL
        minus_btn_w = GRID_CELL
        minus_btn_h = GRID_CELL
        plus_btn_right = msg_right - GRID_CELL
        plus_x = plus_btn_right - GRID_CELL
        plus_btn_w = GRID_CELL
        plus_btn_h = GRID_CELL

        # compute y positions for each menu item line
        y = first_line_y

        # render each menu item: label, minus button, selection centered, plus button
        widget_rects.clear()
        for idx, (label, values, cur_idx) in enumerate(menu_items):
            minus_rect = pygame.Rect(minus_x, y, minus_btn_w, minus_btn_h)
            pygame.draw.rect(screen, DARK_SQUARE, minus_rect)
            lt = font.render("<", True, (0, 160, 0))
            lt_rect = lt.get_rect(center=minus_rect.center)
            screen.blit(lt, lt_rect)
            widget_rects[("minus", idx)] = minus_rect

#            lbl_surf = font.render(f"{label}:", True, (0, 0, 0))
#            screen.blit(lbl_surf, (text_x, y))
            lbl_surf = font.render(f"{label}:", True, (0, 0, 0))
            lbl_rect = lbl_surf.get_rect(midleft=(text_x, minus_rect.centery))
            screen.blit(lbl_surf, lbl_rect)


            plus_rect = pygame.Rect(plus_x, y, plus_btn_w, plus_btn_h)
            pygame.draw.rect(screen, DARK_SQUARE, plus_rect)
            gt = font.render(">", True, (255, 0, 0))
            gt_rect = gt.get_rect(center=plus_rect.center)
            screen.blit(gt, gt_rect)
            widget_rects[("plus", idx)] = plus_rect

            sel_text = str(values[cur_idx])
            sel_surf = font.render(sel_text, True, (0, 0, 0))
            sel_left = minus_rect.right
            sel_right = plus_rect.left
            sel_center_x = sel_left + (sel_right - sel_left) // 2
            sel_rect = sel_surf.get_rect(center=(sel_center_x, minus_rect.centery))
            screen.blit(sel_surf, sel_rect)

            y += line_height

        # After Colors, one GRID_CELL below draw 'start' button (or 'repeat' if layout_shown) at same location
        y += GRID_CELL  # one GRID_CELL gap
        start_left = minus_x
        start_right = plus_btn_right
        start_rect = pygame.Rect(start_left, y, start_right - start_left, GRID_CELL)
        # Toggle label & behavior: when menu active show "start", when layout shown show "repeat"
        if layout_shown:
            pygame.draw.rect(screen, (0, 128, 255), start_rect)
            start_label = font.render("repeat", True, (255, 255, 255))
        else:
            pygame.draw.rect(screen, (0, 128, 255), start_rect)
            start_label = font.render("start", True, (255, 255, 255))
        start_label_rect = start_label.get_rect(center=start_rect.center)
        screen.blit(start_label, start_label_rect)
        widget_rects["start"] = start_rect  # used for both start and repeat (toggle)

        # If layout_shown display targets & squares below the start/repeat button
        y += GRID_CELL + GRID_CELL * 1  # small gap after start
        if layout_shown:
            targets_surf = font.render(f"targets: {placed_count}", True, (0,0,0))
            screen.blit(targets_surf, (text_x, y))
            y += line_height
            squares_surf = font.render(f"squares: {occupied_squares}", True, (0,0,0))
            screen.blit(squares_surf, (text_x, y))
            y += line_height

        # draw the 'exit' button: red (255,0,0), two GRID_CELL wide, one GRID_CELL high,
        # placed one GRID_CELL above the bottom of the message window and with the right edge aligned with plus button right side
        exit_w = GRID_CELL * 2
        exit_h = GRID_CELL
        exit_right = plus_btn_right
        exit_left = exit_right - exit_w
        exit_top = msg_bottom - GRID_CELL - exit_h  # one GRID_CELL above bottom of message window
        exit_rect = pygame.Rect(exit_left, exit_top, exit_w, exit_h)
        pygame.draw.rect(screen, (255, 0, 0), exit_rect)
        exit_label = font.render("exit", True, (255, 255, 255))
        exit_label_rect = exit_label.get_rect(center=exit_rect.center)
        screen.blit(exit_label, exit_label_rect)
        widget_rects["exit"] = exit_rect

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Commented out keyboard handlers for r and ESC (left in code as requested)
                # if event.key == pygame.K_ESCAPE:
                #     pygame.quit()
                #     sys.exit()
                # elif event.key == pygame.K_r:
                #     pass
                if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    board.cell_size = clamp(board.cell_size + 2, 8, 80)
                elif event.key == pygame.K_MINUS or event.key == pygame.K_UNDERSCORE:
                    board.cell_size = clamp(board.cell_size - 2, 8, 80)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # If a layout is shown, only respond to 'repeat' (start rect) and 'exit'
                if layout_shown:
                    if widget_rects.get("start") and widget_rects["start"].collidepoint(mx, my):
                        # Repeat pressed -> restart back to interactive menu (clear layout)
                        layout_shown = False
                        waiting_for_start = True
                        # clear placed state and board so menu becomes interactive again
                        placed_polys = []
                        placed_count = 0
                        occupied_squares = 0
                        # set board to the currently selected board size so grid updates visually
                        current_selections = get_current_selections()
                        current_board_size = int(current_selections["board"])
                        board = Board(current_board_size, current_board_size, GRID_CELL, GRID_ORIGIN)
                    elif widget_rects["exit"].collidepoint(mx, my):
                        pygame.quit()
                        sys.exit()
                    # ignore other clicks while layout is shown
                else:
                    # menu is active and interactive
                    handled = False
                    for idx in range(len(menu_items)):
                        if widget_rects.get(("minus", idx)) and widget_rects[("minus", idx)].collidepoint(mx, my):
                            label, values, cur_idx = menu_items[idx]
                            cur_idx = (cur_idx - 1) % len(values)
                            menu_items[idx] = (label, values, cur_idx)
                            handled = True
                            break
                        if widget_rects.get(("plus", idx)) and widget_rects[("plus", idx)].collidepoint(mx, my):
                            label, values, cur_idx = menu_items[idx]
                            cur_idx = (cur_idx + 1) % len(values)
                            menu_items[idx] = (label, values, cur_idx)
                            handled = True
                            break
                    if handled:
                        # update current selections so immediate changes affect UI and possible next run
                        current_selections = get_current_selections()
                        current_board_size = int(current_selections["board"])
                    else:
                        # start button?
                        if widget_rects["start"].collidepoint(mx, my):
                            # read current selections into variables used by placement
                            current_selections = get_current_selections()
                            current_board_size = int(current_selections["board"])
                            # update board object to reflect chosen size on-screen before placement
                            board = Board(current_board_size, current_board_size, GRID_CELL, GRID_ORIGIN)
                            # run placement
                            run_placement()

        pygame.display.flip()

if __name__ == "__main__":
    main()