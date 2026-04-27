"""Maze GUI"""

import os
import pygame
import pygame.freetype
import math
from src.utility.point import Point
from src.utility.direction import Direction
from src.car import Car
from src.workspace import Workspace
from src.simulation import list_datasets
from .constants import GridState, Color, Config
from .button_events import ButtonEventHandler
from .button_actions import ButtonActions

_DETECT_COLORS = {}   # kept for compatibility but DETECT section removed from UI

_CLASS_PALETTE = [
    (255,  59,  48), (  0, 122, 255), ( 52, 199,  89), (255, 149,   0),
    (175,  82, 222), ( 90, 200, 250), (255,  45,  85), (255, 204,   0),
    (255, 255, 255), (162, 132,  94),
]

_EMOJI_FONT = os.path.join(
    os.path.sep, 'usr', 'share', 'fonts', 'truetype', 'noto', 'NotoColorEmoji.ttf'
)

# Map Direction → pygame rotation angle (positive = CCW in pygame)
# Base image is normalized to face NORTH (up).
_DIR_ANGLE = {
    Direction.NORTH:  0,
    Direction.EAST:  -90,   # 90° clockwise
    Direction.SOUTH: 180,
    Direction.WEST:   90,   # 90° counter-clockwise
}


class Board:
    def __init__(self, start=(1, 1), goal=None, num_rows=21, num_cols=21,
                 win_w=1280, win_h=900, margin=Config.GRID_MARGIN):

        self.start = start
        self.goal = goal or (num_rows - 2, num_cols - 2)
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.margin = margin

        self.controller_width = 340
        self.grid_w = win_w - self.controller_width
        self.grid_h = win_h

        self.cell_w = int((self.grid_w - (margin * (num_cols + 1))) / num_cols)
        self.cell_h = int((self.grid_h - (margin * (num_rows + 1))) / num_rows)

        self.grid = [[0] * num_cols for _ in range(num_rows)]
        for i in range(num_rows):
            self.grid[i][0] = GridState.WALL
            self.grid[i][num_cols - 1] = GridState.WALL
        for j in range(num_cols):
            self.grid[0][j] = GridState.WALL
            self.grid[num_rows - 1][j] = GridState.WALL

        self.workspace = Workspace(num_cols, num_rows)
        self.workspace.load_from_maze(self.grid)

        self.car = Car(Point(start[0], start[1]), Direction.NORTH, self.workspace)

        self.warning_active = False
        self.warning_timer = 0
        self.grid_surface = None
        self.needs_redraw = True

        self.solution_path = []
        self.detected_cells = {}
        self.spawned_objects = []
        self.classifier = None
        self.current_obj_info = None

        self.perfect_maze = False
        self.datasets = list_datasets()
        self.dataset_idx = 0
        self.n_objects = 20
        self.sim_model = 'tree'

        self._load_config()

        pygame.init()
        self.screen = pygame.display.set_mode([win_w, win_h])
        pygame.display.set_caption("Micro Mouse Maze")

        self.font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 17)
        self.title_font = pygame.font.Font(None, 28)

        self._load_agent_image()

        self.button_actions = ButtonActions(self)
        self.event_handler = ButtonEventHandler()
        for btn_num, callback in self.button_actions.get_callbacks().items():
            self.event_handler.register_callback(btn_num, callback)

        self.button_rects = {}
        self.algorithm_buttons = []
        self.solve_buttons = []
        self.sim_buttons = []

    def _load_config(self):
        import json
        cfg = os.path.normpath(
            os.path.join(os.path.dirname(__file__), '..', '..', 'config.json'))
        if not os.path.isfile(cfg):
            return
        try:
            with open(cfg) as f:
                data = json.load(f)
            self.n_objects = int(data.get('n_objects', self.n_objects))
            self.perfect_maze = bool(data.get('perfect_maze', self.perfect_maze))
            self.sim_model = data.get('model', self.sim_model)
            ds = data.get('dataset')
            if ds and ds in self.datasets:
                self.dataset_idx = self.datasets.index(ds)
        except Exception:
            pass

    def _load_agent_image(self):
        size = max(8, min(self.cell_w, self.cell_h) - 4)
        raw = None

        # Try mouse emoji
        if os.path.isfile(_EMOJI_FONT):
            try:
                ef = pygame.freetype.Font(_EMOJI_FONT, 109)
                surf, _ = ef.render('🐭', (255, 255, 255))
                if surf.get_width() > 10:
                    raw = pygame.transform.smoothscale(surf, (size, size))
            except Exception:
                pass

        # Fallback: programmatic mouse facing down
        if raw is None:
            raw = pygame.Surface((size, size), pygame.SRCALPHA)
            r = size // 2
            pygame.draw.circle(raw, (180, 180, 180), (r, r), r - 1)
            pygame.draw.circle(raw, (180, 180, 180), (r - r // 2, r // 3), r // 3)
            pygame.draw.circle(raw, (210, 130, 150), (r - r // 2, r // 3), r // 5)
            pygame.draw.circle(raw, (180, 180, 180), (r + r // 2, r // 3), r // 3)
            pygame.draw.circle(raw, (210, 130, 150), (r + r // 2, r // 3), r // 5)
            pygame.draw.circle(raw, (30, 30, 30), (r - r // 3, r - r // 5), max(2, r // 7))
            pygame.draw.circle(raw, (30, 30, 30), (r + r // 3, r - r // 5), max(2, r // 7))
            pygame.draw.circle(raw, (220, 100, 120), (r, r + r // 4), max(2, r // 8))

        # Both emoji and drawn mouse face DOWN — rotate 180° to normalise to NORTH (up)
        self.original_img = pygame.transform.rotate(raw, 180)
        self.img_w = self.img_h = size
        self.agent_img = self.original_img

    @property
    def agent(self):
        return self.car

    def reset_agent(self):
        self.car.position = Point(self.start[0], self.start[1])
        self.car.direction = Direction.NORTH
        self.current_obj_info = None
        self.needs_redraw = True

    def show_warning(self, active):
        self.warning_active = active
        self.warning_timer = Config.WARNING_FLASH_DURATION if active else 0
        self.needs_redraw = True

    # ── Button helpers ────────────────────────────────────────────────────────

    def _draw_circular_arrow_button(self, cx, cy, radius, direction):
        mouse_pos = pygame.mouse.get_pos()
        dist = math.hypot(mouse_pos[0] - cx, mouse_pos[1] - cy)
        color = Color.BUTTON_HOVER if dist <= radius else Color.BUTTON_BG
        pygame.draw.circle(self.screen, color, (cx, cy), radius)
        pygame.draw.circle(self.screen, Color.BORDER, (cx, cy), radius, 2)
        aw, ah, sw = int(radius * 0.35), int(radius * 0.45), int(radius * 0.15)
        if direction == "N":
            tip, bl, br = (cx, cy-ah), (cx-aw, cy), (cx+aw, cy)
            stem = [(cx-sw, cy), (cx+sw, cy), (cx+sw, cy+ah), (cx-sw, cy+ah)]
        elif direction == "S":
            tip, bl, br = (cx, cy+ah), (cx+aw, cy), (cx-aw, cy)
            stem = [(cx-sw, cy-ah), (cx+sw, cy-ah), (cx+sw, cy), (cx-sw, cy)]
        elif direction == "E":
            tip, bl, br = (cx+ah, cy), (cx, cy-aw), (cx, cy+aw)
            stem = [(cx-ah, cy-sw), (cx, cy-sw), (cx, cy+sw), (cx-ah, cy+sw)]
        else:
            tip, bl, br = (cx-ah, cy), (cx, cy+aw), (cx, cy-aw)
            stem = [(cx, cy-sw), (cx+ah, cy-sw), (cx+ah, cy+sw), (cx, cy+sw)]
        pygame.draw.polygon(self.screen, Color.ARROW, [tip, bl, br])
        pygame.draw.polygon(self.screen, Color.ARROW, stem)
        return pygame.Rect(cx - radius, cy - radius, radius * 2, radius * 2)

    def _draw_round_button(self, cx, cy, radius, text, color=Color.BUTTON_BG):
        mouse_pos = pygame.mouse.get_pos()
        dist = math.hypot(mouse_pos[0] - cx, mouse_pos[1] - cy)
        btn_color = Color.BUTTON_HOVER if dist <= radius else color
        pygame.draw.circle(self.screen, btn_color, (cx, cy), radius)
        pygame.draw.circle(self.screen, Color.BORDER, (cx, cy), radius, 2)
        surf = self.font.render(text, True, Color.TEXT_PRIMARY)
        self.screen.blit(surf, surf.get_rect(center=(cx, cy)))
        return pygame.Rect(cx - radius, cy - radius, radius * 2, radius * 2)

    def _draw_small_button(self, cx, cy, w, h, text, color=Color.BUTTON_BG):
        rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
        btn_color = (Color.BUTTON_HOVER if rect.collidepoint(pygame.mouse.get_pos())
                     else color)
        pygame.draw.rect(self.screen, btn_color, rect, border_radius=5)
        pygame.draw.rect(self.screen, Color.BORDER, rect, 1, border_radius=5)
        surf = self.small_font.render(text, True, Color.TEXT_PRIMARY)
        self.screen.blit(surf, surf.get_rect(center=(cx, cy)))
        return rect

    def _section_label(self, text, cx, y):
        surf = self.font.render(text, True, Color.TEXT_SECONDARY)
        self.screen.blit(surf, surf.get_rect(center=(cx, y)))

    def _draw_divider(self, y):
        pygame.draw.line(self.screen, Color.BORDER,
                         (self.grid_w + 16, y),
                         (self.grid_w + self.controller_width - 16, y), 1)

    # ── Controller panel ──────────────────────────────────────────────────────

    def _draw_controller(self):
        cx = self.grid_w + self.controller_width // 2
        bg = pygame.Rect(self.grid_w, 0, self.controller_width, self.grid_h)
        pygame.draw.rect(self.screen, Color.PANEL_BG, bg)
        pygame.draw.rect(self.screen, Color.BORDER, bg, 2)

        # Title
        title = self.title_font.render("CONTROLLER", True, Color.TEXT_PRIMARY)
        self.screen.blit(title, title.get_rect(center=(cx, 26)))
        self._draw_divider(44)

        # SOLVE
        self._section_label("SOLVE  (A-maze-ing)", cx, 60)
        self.solve_buttons = []
        for i, (lbl, key) in enumerate([('BFS','bfs'),('DFS','dfs'),('A*','astar'),('CLR',None)]):
            bx = cx - 90 + i * 60
            rect = self._draw_round_button(bx, 88, 20, lbl,
                                           Color.BUTTON_ACTIVE if key is None else Color.BUTTON_BG)
            self.solve_buttons.append((rect, key))
        self._draw_divider(116)

        # D-pad  (no DETECT section — more breathing room)
        dpad_y, btn_r = 230, 34
        self.button_rects[1] = self._draw_circular_arrow_button(cx,       dpad_y - 54, btn_r, "N")
        self.button_rects[2] = self._draw_circular_arrow_button(cx + 54,  dpad_y,      btn_r, "E")
        self.button_rects[3] = self._draw_circular_arrow_button(cx,       dpad_y + 54, btn_r, "S")
        self.button_rects[4] = self._draw_circular_arrow_button(cx - 54,  dpad_y,      btn_r, "W")

        # Reset / Status
        action_y = dpad_y + 108
        self.button_rects[5] = self._draw_round_button(cx - 66, action_y, 26, "RESET")
        self.button_rects[6] = self._draw_round_button(cx + 66, action_y, 26, "STATUS")
        self._draw_divider(action_y + 40)

        # MAZE GENERATION
        gen_label_y = action_y + 56
        self._section_label("MAZE GENERATION", cx, gen_label_y)
        self.algorithm_buttons = []
        gen_btn_y = gen_label_y + 32
        for idx, name in enumerate(['DFS', 'BFS', 'Prim', 'HK']):
            bx = cx - 90 + idx * 60
            rect = self._draw_round_button(bx, gen_btn_y, 20, name)
            self.algorithm_buttons.append((rect, name))
        self._draw_divider(gen_btn_y + 34)

        # SIMULATION
        sim_y0 = gen_btn_y + 50
        self._draw_simulation_section(cx, sim_y0)

        # INFO panel (fills remaining height)
        info_divider_y = sim_y0 + 160
        self._draw_divider(info_divider_y)
        self._draw_info_panel(cx, info_divider_y + 14)

    def _draw_simulation_section(self, cx, y0):
        self.sim_buttons = []
        bw, bh = 36, 20

        self._section_label("SIMULATION", cx, y0)

        ds_y = y0 + 26
        lbl = self.small_font.render("Dataset:", True, Color.TEXT_SECONDARY)
        self.screen.blit(lbl, (self.grid_w + 12, ds_y - 7))
        prev_r = self._draw_small_button(self.grid_w + 68, ds_y, 20, bh, "<")
        self.sim_buttons.append((prev_r, 'ds_prev'))
        ds_name = self.datasets[self.dataset_idx] if self.datasets else "none"
        if len(ds_name) > 14:
            ds_name = ds_name[:13] + "…"
        ns = self.small_font.render(ds_name, True, Color.TEXT_PRIMARY)
        self.screen.blit(ns, ns.get_rect(center=(self.grid_w + 180, ds_y)))
        next_r = self._draw_small_button(self.grid_w + self.controller_width - 18, ds_y, 20, bh, ">")
        self.sim_buttons.append((next_r, 'ds_next'))

        n_y = ds_y + 30
        nl = self.small_font.render("N objects:", True, Color.TEXT_SECONDARY)
        self.screen.blit(nl, (self.grid_w + 12, n_y - 7))
        dec_r = self._draw_small_button(self.grid_w + 164, n_y, 20, bh, "-")
        self.sim_buttons.append((dec_r, 'n_dec'))
        nv = self.font.render(str(self.n_objects), True, Color.TEXT_PRIMARY)
        self.screen.blit(nv, nv.get_rect(center=(self.grid_w + 200, n_y)))
        inc_r = self._draw_small_button(self.grid_w + 236, n_y, 20, bh, "+")
        self.sim_buttons.append((inc_r, 'n_inc'))

        m_y = n_y + 30
        ml = self.small_font.render("Model:", True, Color.TEXT_SECONDARY)
        self.screen.blit(ml, (self.grid_w + 12, m_y - 7))
        tc = Color.BUTTON_ACTIVE if self.sim_model == 'tree' else Color.BUTTON_BG
        sc = Color.BUTTON_ACTIVE if self.sim_model == 'svm'  else Color.BUTTON_BG
        tr = self._draw_small_button(self.grid_w + 164, m_y, 42, bh, "Tree", tc)
        sr = self._draw_small_button(self.grid_w + 218, m_y, 42, bh, "SVM",  sc)
        self.sim_buttons.append((tr, 'model_tree'))
        self.sim_buttons.append((sr, 'model_svm'))

        sp_y = m_y + 34
        spr = self._draw_small_button(cx - 42, sp_y, 68, 24, "SPAWN", Color.BUTTON_ACTIVE)
        clr = self._draw_small_button(cx + 42, sp_y, 56, 24, "CLR",   Color.BUTTON_BG)
        self.sim_buttons.append((spr, 'spawn'))
        self.sim_buttons.append((clr, 'clear_spawn'))

    def _draw_info_panel(self, cx, y0):
        """Large info/status panel — shows object attributes+prediction or status message."""
        self._section_label("INFO", cx, y0)
        y = y0 + 18
        x0 = self.grid_w + 12
        max_y = self.grid_h - 10

        if self.current_obj_info:
            info = self.current_obj_info
            # Header
            hdr = self.small_font.render("Object detected!", True, (52, 199, 89))
            self.screen.blit(hdr, (x0, y)); y += 20

            # Attributes
            for col in info['feature_cols']:
                if y + 14 > max_y:
                    break
                val = str(info['data'].get(col, ''))
                key = (col[:13] + "…") if len(col) > 14 else col
                val = (val[:12] + "…") if len(val) > 13 else val
                surf = self.small_font.render(f"{key}: {val}", True, Color.TEXT_PRIMARY)
                self.screen.blit(surf, (x0 + 4, y)); y += 16

            # Divider
            if y + 4 < max_y:
                pygame.draw.line(self.screen, Color.BORDER, (x0, y + 2),
                                 (self.grid_w + self.controller_width - 12, y + 2), 1)
                y += 10

            # Prediction (highlighted)
            if y + 18 < max_y:
                pred_text = f"→  {info['prediction']}"
                ps = self.font.render(pred_text, True, (52, 199, 89))
                self.screen.blit(ps, (x0, y))

        else:
            # Warning dot
            w_color = (Color.WARNING if self.warning_active and (self.warning_timer // 5) % 2 == 0
                       else Color.BUTTON_BG)
            pygame.draw.circle(self.screen, w_color, (x0 + 8, y + 8), 8)
            pygame.draw.circle(self.screen, Color.BORDER, (x0 + 8, y + 8), 8, 1)

            # Status message
            msg = self.button_actions.get_current_message()
            if msg:
                mx = x0 + 22
                for i, chunk in enumerate([msg[j:j+24] for j in range(0, len(msg), 24)][:4]):
                    if y + i * 16 + 14 > max_y:
                        break
                    surf = self.small_font.render(chunk, True, Color.TEXT_PRIMARY)
                    self.screen.blit(surf, (mx, y + i * 16))

            # Hint
            hint_y = y + 80
            if hint_y + 14 < max_y:
                hint = self.small_font.render("← → ↑ ↓  arrow keys", True, Color.BORDER)
                self.screen.blit(hint, hint.get_rect(center=(cx, hint_y)))

    # ── Grid rendering ────────────────────────────────────────────────────────

    def _cell_pixel(self, row, col):
        x = (self.margin + self.cell_w) * col + self.margin
        y = (self.margin + self.cell_h) * row + self.margin
        return x, y

    def _get_grid_cell_from_mouse(self, mouse_pos):
        x, y = mouse_pos
        if x >= self.grid_w:
            return None
        col = x // (self.cell_w + self.margin)
        row = y // (self.cell_h + self.margin)
        if 0 <= row < self.num_rows and 0 <= col < self.num_cols:
            return (row, col)
        return None

    def _create_grid_surface(self):
        surf = pygame.Surface((self.grid_w, self.grid_h))
        surf.fill(Color.BACKGROUND)
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                x, y = self._cell_pixel(row, col)
                color = (Color.WALL_COLOR if self.grid[row][col] == GridState.WALL
                         else Color.FREE_COLOR)
                pygame.draw.rect(surf, color, (x, y, self.cell_w, self.cell_h))
        return surf

    def _get_agent_surface(self):
        row, col = self.car.get_position()
        px, py = self._cell_pixel(row, col)
        img_x = px + (self.cell_w - self.img_w) // 2
        img_y = py + (self.cell_h - self.img_h) // 2

        angle = _DIR_ANGLE[self.car.direction]
        if angle:
            rotated = pygame.transform.rotate(self.original_img, angle)
            rect = rotated.get_rect(center=(img_x + self.img_w // 2,
                                            img_y + self.img_h // 2))
            return rotated, rect.x, rect.y
        return self.original_img, img_x, img_y

    def _check_object_at_agent(self):
        if not self.spawned_objects or self.classifier is None:
            self.current_obj_info = None
            return
        pos = self.car.get_position()
        for row, col, data in self.spawned_objects:
            if (row, col) == pos:
                prediction = self.classifier.predict(data)
                self.current_obj_info = {
                    'data': data,
                    'prediction': prediction,
                    'feature_cols': self.classifier._feature_cols,
                }
                return
        self.current_obj_info = None

    def draw_grid(self):
        self.needs_redraw = True

    def _update_display(self):
        if not self.needs_redraw:
            return

        self.screen.fill(Color.BACKGROUND)

        if self.grid_surface is None:
            self.grid_surface = self._create_grid_surface()
        self.screen.blit(self.grid_surface, (0, 0))

        # Solution path
        if self.solution_path:
            sv = pygame.Surface((self.cell_w, self.cell_h), pygame.SRCALPHA)
            sv.fill((*Color.SOLUTION_COLOR, 180))
            for row, col in self.solution_path:
                self.screen.blit(sv, self._cell_pixel(row, col))

        # Goal
        gx, gy = self._cell_pixel(self.goal[0], self.goal[1])
        pygame.draw.rect(self.screen, Color.GOAL_COLOR, (gx, gy, self.cell_w, self.cell_h))

        # Spawned objects — neutral white dots
        r_dot = max(3, min(self.cell_w, self.cell_h) // 4)
        for row, col, _ in self.spawned_objects:
            px, py = self._cell_pixel(row, col)
            cx_dot = px + self.cell_w // 2
            cy_dot = py + self.cell_h // 2
            pygame.draw.circle(self.screen, (220, 220, 220), (cx_dot, cy_dot), r_dot)
            pygame.draw.circle(self.screen, (100, 100, 100), (cx_dot, cy_dot), r_dot, 1)

        # Agent
        img, ix, iy = self._get_agent_surface()
        self.screen.blit(img, (ix, iy))

        # Check for object at agent position (updates current_obj_info)
        self._check_object_at_agent()

        self._draw_controller()
        pygame.display.update()
        self.needs_redraw = False

    # ── Main loop ─────────────────────────────────────────────────────────────

    def _handle_sim_action(self, action):
        if action == 'ds_prev':
            if self.datasets:
                self.dataset_idx = (self.dataset_idx - 1) % len(self.datasets)
                self.needs_redraw = True
        elif action == 'ds_next':
            if self.datasets:
                self.dataset_idx = (self.dataset_idx + 1) % len(self.datasets)
                self.needs_redraw = True
        elif action == 'n_dec':
            self.n_objects = max(1, self.n_objects - 5)
            self.needs_redraw = True
        elif action == 'n_inc':
            self.n_objects = min(500, self.n_objects + 5)
            self.needs_redraw = True
        elif action == 'model_tree':
            self.sim_model = 'tree'
            self.needs_redraw = True
        elif action == 'model_svm':
            self.sim_model = 'svm'
            self.needs_redraw = True
        elif action == 'spawn':
            self.button_actions.spawn_simulation()
        elif action == 'clear_spawn':
            self.classifier = None
            self.current_obj_info = None
            self.button_actions.clear_simulation()

    def run(self):
        done = False
        clock = pygame.time.Clock()
        frame_count = 0
        self.needs_redraw = True

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.button_actions.on_button_north()
                    elif event.key == pygame.K_DOWN:
                        self.button_actions.on_button_south()
                    elif event.key == pygame.K_LEFT:
                        self.button_actions.on_button_west()
                    elif event.key == pygame.K_RIGHT:
                        self.button_actions.on_button_east()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()

                    cell = self._get_grid_cell_from_mouse(pos)
                    if cell:
                        row, col = cell
                        if self.grid[row][col] != GridState.WALL:
                            self.grid[row][col] = GridState.WALL
                            self.workspace.set_wall(Point(row, col), True)
                        else:
                            self.grid[row][col] = GridState.FREE
                            self.workspace.set_wall(Point(row, col), False)
                        self.grid_surface = None
                        self.needs_redraw = True
                        continue

                    for rect, key in self.solve_buttons:
                        if rect.collidepoint(pos):
                            (self.button_actions.clear_solution() if key is None
                             else self.button_actions.solve_maze(key))
                            break

                    for btn_rect, algo_name in self.algorithm_buttons:
                        if btn_rect.collidepoint(pos):
                            getattr(self.button_actions, {
                                'DFS': 'on_algorithm_dfs',
                                'BFS': 'on_algorithm_bfs',
                                'Prim': 'on_algorithm_prim',
                                'HK': 'on_algorithm_huntkill',
                            }[algo_name])()
                            break

                    for btn_rect, action in self.sim_buttons:
                        if btn_rect.collidepoint(pos):
                            self._handle_sim_action(action)
                            break

                    for btn_num, rect in self.button_rects.items():
                        if rect.collidepoint(pos):
                            self.event_handler.handle_click(btn_num)
                            break

            frame_count += 1
            if frame_count % 3 == 0 and self.warning_timer > 0:
                self.warning_timer -= 1
                if self.warning_timer == 0:
                    self.warning_active = False
                self.needs_redraw = True

            self.button_actions.update()
            self._update_display()
            clock.tick(Config.FRAME_RATE)

    def close(self):
        pygame.quit()
