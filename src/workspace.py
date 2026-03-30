from src.utility.point import Point


class Workspace:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
    
    def load_from_generator(self, generator):
        """
        Load maze from generator (hex format).
        Convert hex to 1=wall, 0=free for UI.
        """
        for x in range(self.width):
            for y in range(self.height):
                hex_val = generator.maze[x][y]
                # 0 = open cell, anything else = wall
                if hex_val == 0:
                    self.grid[y][x] = 0  # Free space
                else:
                    self.grid[y][x] = 1  # Wall
    
    def is_wall(self, point: Point) -> bool:
        """Check if a position contains a wall."""
        if 0 <= point.x < self.height and 0 <= point.y < self.width:
            return self.grid[point.x][point.y] == 1
        return True
    
    def set_wall(self, point: Point, is_wall: bool = True):
        """Set a cell as wall or free."""
        if 0 <= point.x < self.height and 0 <= point.y < self.width:
            self.grid[point.x][point.y] = 1 if is_wall else 0
    
    def load_from_maze(self, maze_grid):
        """Load a 2D maze grid (1=wall, 0=free)."""
        self.grid = maze_grid