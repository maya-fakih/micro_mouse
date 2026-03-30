"""Maze GUI - Professional with Circular Arrow Buttons"""

import pygame
import math
from src.utility.point import Point
from src.utility.direction import Direction
from src.car import Car
from src.workspace import Workspace
from .constants import GridState, Color, Config
from .button_events import ButtonEventHandler
from .button_actions import ButtonActions


class Board:
    def __init__(self, start=(1, 1), goal=None, maze=None, num_rows=21, num_cols=21,
                 win_w=1000, win_h=720, margin=Config.GRID_MARGIN):
        
        self.start = start
        self.goal = goal or (num_rows - 2, num_cols - 2)
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.margin = margin
        
        self.controller_width = 280
        self.grid_w = win_w - self.controller_width
        self.grid_h = win_h
        
        self.cell_w = int((self.grid_w - (margin * (num_cols + 1))) / num_cols)
        self.cell_h = int((self.grid_h - (margin * (num_rows + 1))) / num_rows)
        
        if maze:
            self.grid = maze
        else:
            self.grid = [[0 for _ in range(num_cols)] for _ in range(num_rows)]
            for i in range(num_rows):
                self.grid[i][0] = GridState.WALL
                self.grid[i][num_cols - 1] = GridState.WALL
            for j in range(num_cols):
                self.grid[0][j] = GridState.WALL
                self.grid[num_rows - 1][j] = GridState.WALL
        
        self.workspace = Workspace(num_cols, num_rows)
        self.workspace.load_from_maze(self.grid)
        
        car_position = Point(start[0], start[1])
        self.car = Car(car_position, Direction.NORTH, self.workspace)
        
        self.warning_active = False
        self.warning_timer = 0
        self.grid_surface = None
        self.needs_redraw = True
        
        self._load_agent_image()
        
        pygame.init()
        self.screen = pygame.display.set_mode([win_w, win_h])
        pygame.display.set_caption("🐭 Micro Mouse Maze - Professional")
        
        self.font = pygame.font.Font(None, 20)
        self.title_font = pygame.font.Font(None, 28)
        self.message_font = pygame.font.Font(None, 24)
        
        self.button_actions = ButtonActions(self)
        self.event_handler = ButtonEventHandler()
        for btn_num, callback in self.button_actions.get_callbacks().items():
            self.event_handler.register_callback(btn_num, callback)
        
        self.button_rects = {}
        self.algorithm_buttons = []
        self.initialized = True
    
    def _load_agent_image(self):
        max_size_w = self.cell_w - 10
        max_size_h = self.cell_h - 10
        
        try:
            original_img = pygame.image.load(Config.AGENT_IMAGE_PATH)
            orig_w, orig_h = original_img.get_rect().size
            if orig_w > orig_h:
                self.img_w = max_size_w
                self.img_h = int(max_size_w * orig_h / orig_w)
            else:
                self.img_h = max_size_h
                self.img_w = int(max_size_h * orig_w / orig_h)
            self.original_img = pygame.transform.scale(original_img, (self.img_w, self.img_h))
        except:
            self.img_w = max_size_w
            self.img_h = max_size_h
            self.original_img = pygame.Surface((self.img_w, self.img_h), pygame.SRCALPHA)
            pygame.draw.circle(self.original_img, (139, 69, 19), (self.img_w//2, self.img_h//2), self.img_w//2)
            pygame.draw.circle(self.original_img, (0, 0, 0), (self.img_w//3, self.img_h//3), self.img_w//8)
        
        self.agent_img = self.original_img
    
    @property
    def agent(self):
        return self.car
    
    def reset_agent(self):
        self.car.position = Point(self.start[0], self.start[1])
        self.car.direction = Direction.NORTH
        self.needs_redraw = True
    
    def reset_grid(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid[i][j] != GridState.WALL:
                    self.grid[i][j] = GridState.FREE
                    self.workspace.set_wall(Point(i, j), False)
        self.grid_surface = None
        self.needs_redraw = True
    
    def show_warning(self, active):
        self.warning_active = active
        self.warning_timer = Config.WARNING_FLASH_DURATION if active else 0
        self.needs_redraw = True
    
    def _draw_circular_arrow_button(self, cx, cy, radius, direction):
        mouse_pos = pygame.mouse.get_pos()
        dist = math.sqrt((mouse_pos[0] - cx)**2 + (mouse_pos[1] - cy)**2)
        is_hover = dist <= radius
        
        btn_color = Color.BUTTON_HOVER if is_hover else Color.BUTTON_BG
        pygame.draw.circle(self.screen, btn_color, (cx, cy), radius)
        pygame.draw.circle(self.screen, Color.BORDER, (cx, cy), radius, 2)
        
        aw = int(radius * 0.35)
        ah = int(radius * 0.45)
        sw = int(radius * 0.15)
        
        if direction == "N":
            tip = (cx, cy - ah)
            bl = (cx - aw, cy)
            br = (cx + aw, cy)
            stem = [(cx - sw, cy), (cx + sw, cy), (cx + sw, cy + ah), (cx - sw, cy + ah)]
        elif direction == "S":
            tip = (cx, cy + ah)
            bl = (cx + aw, cy)
            br = (cx - aw, cy)
            stem = [(cx - sw, cy - ah), (cx + sw, cy - ah), (cx + sw, cy), (cx - sw, cy)]
        elif direction == "E":
            tip = (cx + ah, cy)
            bl = (cx, cy - aw)
            br = (cx, cy + aw)
            stem = [(cx - ah, cy - sw), (cx, cy - sw), (cx, cy + sw), (cx - ah, cy + sw)]
        else:
            tip = (cx - ah, cy)
            bl = (cx, cy + aw)
            br = (cx, cy - aw)
            stem = [(cx, cy - sw), (cx + ah, cy - sw), (cx + ah, cy + sw), (cx, cy + sw)]
        
        pygame.draw.polygon(self.screen, Color.ARROW, [tip, bl, br])
        pygame.draw.polygon(self.screen, Color.ARROW, stem)
        return pygame.Rect(cx - radius, cy - radius, radius * 2, radius * 2)
    
    def _draw_round_button(self, cx, cy, radius, text, color=Color.BUTTON_BG):
        mouse_pos = pygame.mouse.get_pos()
        dist = math.sqrt((mouse_pos[0] - cx)**2 + (mouse_pos[1] - cy)**2)
        is_hover = dist <= radius
        
        btn_color = Color.BUTTON_HOVER if is_hover else color
        pygame.draw.circle(self.screen, btn_color, (cx, cy), radius)
        pygame.draw.circle(self.screen, Color.BORDER, (cx, cy), radius, 2)
        
        text_surface = self.font.render(text, True, Color.TEXT_PRIMARY)
        text_rect = text_surface.get_rect(center=(cx, cy))
        self.screen.blit(text_surface, text_rect)
        return pygame.Rect(cx - radius, cy - radius, radius * 2, radius * 2)
    
    def _draw_controller(self):
        controller_x = self.grid_w + (self.controller_width // 2)
        center_y = self.grid_h // 2
        
        bg_rect = pygame.Rect(self.grid_w, 0, self.controller_width, self.grid_h)
        pygame.draw.rect(self.screen, Color.PANEL_BG, bg_rect)
        pygame.draw.rect(self.screen, Color.BORDER, bg_rect, 2)
        
        title = self.title_font.render("🐭 CONTROLLER", True, Color.TEXT_PRIMARY)
        title_rect = title.get_rect(center=(controller_x, 45))
        self.screen.blit(title, title_rect)
        
        dpad_y = center_y - 45
        btn_radius = 38
        
        north = self._draw_circular_arrow_button(controller_x, dpad_y - 55, btn_radius, "N")
        east = self._draw_circular_arrow_button(controller_x + 55, dpad_y, btn_radius, "E")
        south = self._draw_circular_arrow_button(controller_x, dpad_y + 55, btn_radius, "S")
        west = self._draw_circular_arrow_button(controller_x - 55, dpad_y, btn_radius, "W")
        
        self.button_rects[1] = north
        self.button_rects[2] = east
        self.button_rects[3] = south
        self.button_rects[4] = west
        
        action_y = center_y + 70
        small_radius = 30
        
        reset = self._draw_round_button(controller_x - 70, action_y + 30, small_radius, "RESET")
        status = self._draw_round_button(controller_x + 70, action_y + 30, small_radius, "STATUS")
        
        self.button_rects[5] = reset
        self.button_rects[6] = status
        
        algo_y = action_y + 95
        algo_text = self.font.render("MAZE GENERATION", True, Color.TEXT_SECONDARY)
        algo_rect = algo_text.get_rect(center=(controller_x, algo_y))
        self.screen.blit(algo_text, algo_rect)
        
        algo_btns_y = algo_y + 28
        algos = [('DFS', 0), ('BFS', 1), ('Prim', 2), ('HK', 3)]
        self.algorithm_buttons = []
        
        for name, idx in algos:
            btn_x = controller_x - 85 + (idx * 55)
            btn_rect = self._draw_round_button(btn_x, algo_btns_y, 24, name, Color.BUTTON_BG)
            self.algorithm_buttons.append((btn_rect, name))
        
        warning_y = algo_btns_y + 50
        warning_color = Color.WARNING if self.warning_active and (self.warning_timer // 5) % 2 == 0 else Color.BUTTON_BG
        pygame.draw.circle(self.screen, warning_color, (controller_x, warning_y), 28)
        pygame.draw.circle(self.screen, Color.BORDER, (controller_x, warning_y), 28, 2)
        
        if self.warning_active:
            warn_text = self.message_font.render("!", True, Color.WHITE)
            warn_rect = warn_text.get_rect(center=(controller_x, warning_y))
            self.screen.blit(warn_text, warn_rect)
        
        message = self.button_actions.get_current_message()
        if message:
            msg_y = warning_y + 50
            msg_bg = pygame.Rect(self.grid_w + 15, msg_y - 15, self.controller_width - 30, 55)
            pygame.draw.rect(self.screen, (0, 0, 0), msg_bg)
            pygame.draw.rect(self.screen, Color.BORDER, msg_bg, 1)
            
            if len(message) > 28:
                lines = [message[:28], message[28:]]
                for i, line in enumerate(lines):
                    msg_surface = self.font.render(line, True, Color.TEXT_PRIMARY)
                    msg_rect = msg_surface.get_rect(center=(controller_x, msg_y + i * 22))
                    self.screen.blit(msg_surface, msg_rect)
            else:
                msg_surface = self.font.render(message, True, Color.TEXT_PRIMARY)
                msg_rect = msg_surface.get_rect(center=(controller_x, msg_y))
                self.screen.blit(msg_surface, msg_rect)
    
    def _get_agent_position(self):
        row, col = self.car.get_position()
        x = (self.margin + self.cell_w) * col + self.margin
        y = (self.margin + self.cell_h) * row + self.margin
        img_x = x + int((self.cell_w - self.img_w) / 2)
        img_y = y + int((self.cell_h - self.img_h) / 2)
        
        angle = self.car.get_rotation_angle()
        if angle != 0:
            rotated_img = pygame.transform.rotate(self.original_img, -angle)
            new_rect = rotated_img.get_rect(center=(img_x + self.img_w//2, img_y + self.img_h//2))
            return rotated_img, new_rect.x, new_rect.y
        return self.original_img, img_x, img_y
    
    def _create_grid_surface(self):
        surface = pygame.Surface((self.grid_w, self.grid_h))
        surface.fill(Color.BACKGROUND)
        
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                x = (self.margin + self.cell_w) * col + self.margin
                y = (self.margin + self.cell_h) * row + self.margin
                
                if self.grid[row][col] == GridState.WALL:
                    color = Color.WALL_COLOR
                else:
                    color = Color.FREE_COLOR
                
                pygame.draw.rect(surface, color, (x, y, self.cell_w, self.cell_h))
        
        return surface
    
    def _get_grid_cell_from_mouse(self, mouse_pos):
        x, y = mouse_pos
        if x >= self.grid_w:
            return None
        col = x // (self.cell_w + self.margin)
        row = y // (self.cell_h + self.margin)
        if 0 <= row < self.num_rows and 0 <= col < self.num_cols:
            return (row, col)
        return None
    
    def draw_grid(self):
        self.needs_redraw = True
    
    def _update_display(self):
        if not self.needs_redraw:
            return
        
        self.screen.fill(Color.BACKGROUND)
        
        if self.grid_surface is None:
            self.grid_surface = self._create_grid_surface()
        self.screen.blit(self.grid_surface, (0, 0))
        
        goal_x, goal_y = self.goal
        gx = (self.margin + self.cell_w) * goal_y + self.margin
        gy = (self.margin + self.cell_h) * goal_x + self.margin
        pygame.draw.rect(self.screen, Color.GOAL_COLOR, (gx, gy, self.cell_w, self.cell_h))
        
        agent_img, img_x, img_y = self._get_agent_position()
        self.screen.blit(agent_img, (img_x, img_y))
        
        self._draw_controller()
        pygame.display.update()
        self.needs_redraw = False
    
    def run(self):
        done = False
        clock = pygame.time.Clock()
        frame_count = 0
        self.needs_redraw = True
        
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    
                    grid_cell = self._get_grid_cell_from_mouse(pos)
                    if grid_cell:
                        row, col = grid_cell
                        if self.grid[row][col] != GridState.WALL:
                            self.grid[row][col] = GridState.WALL
                            self.workspace.set_wall(Point(row, col), True)
                        else:
                            self.grid[row][col] = GridState.FREE
                            self.workspace.set_wall(Point(row, col), False)
                        self.grid_surface = None
                        self.needs_redraw = True
                        continue
                    
                    for btn_rect, algo_name in self.algorithm_buttons:
                        if btn_rect.collidepoint(pos):
                            if algo_name == 'DFS':
                                self.button_actions.on_algorithm_dfs()
                            elif algo_name == 'BFS':
                                self.button_actions.on_algorithm_bfs()
                            elif algo_name == 'Prim':
                                self.button_actions.on_algorithm_prim()
                            elif algo_name == 'HK':
                                self.button_actions.on_algorithm_huntkill()
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
                elif self.warning_active:
                    self.needs_redraw = True
            
            self.button_actions.update()
            self._update_display()
            clock.tick(Config.FRAME_RATE)
    
    def close(self):
        pygame.quit()