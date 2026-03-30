"""Constants for Maze GUI"""

import os

class GridState:
    WALL = 1
    FREE = 0
    GOAL = -1
    SOLUTION = 2
    EXPLORED = 3


class Color:
    """Professional dark theme"""
    BACKGROUND = (18, 18, 18)
    PANEL_BG = (28, 28, 30)
    BORDER = (58, 58, 60)
    
    WALL_COLOR = (35, 35, 35)
    FREE_COLOR = (35, 45, 98)
    GOAL_COLOR = (255, 69, 58)
    SOLUTION_COLOR = (48, 209, 88)
    EXPLORED_COLOR = (10, 132, 255)
    
    BUTTON_BG = (44, 44, 46)
    BUTTON_HOVER = (64, 64, 66)
    BUTTON_ACTIVE = (0, 122, 255)
    ARROW = (255, 255, 255)
    
    TEXT_PRIMARY = (255, 255, 255)
    TEXT_SECONDARY = (142, 142, 147)
    WARNING = (255, 69, 58)
    
    # Legacy colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREY = (75, 75, 75)
    RED = (220, 0, 0)
    BLUE = (0, 150, 255)
    GREEN = (0, 150, 0)


class Config:
    BUTTON_SIZE = 70
    BUTTON_MARGIN = 15
    GRID_MARGIN = 1
    
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    AGENT_IMAGE_PATH = os.path.join(CURRENT_DIR, 'images', 'mouse.png')
    
    DEFAULT_SPEED = 0.2
    FRAME_RATE = 60
    MAZE_SIZE = 21
    
    WARNING_FLASH_DURATION = 30
    WARNING_LIGHT_SIZE = 50