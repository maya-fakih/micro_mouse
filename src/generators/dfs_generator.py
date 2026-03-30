from typing import Any
from .maze_generator import MazeGenerator
import random


class DFSGenerator(MazeGenerator):
    def __init__(self, settings_dict: dict[str, Any]) -> None:
        super().__init__(settings_dict)

    def generate(self) -> None:
        """Generate maze using DFS."""
        start_x, start_y = self.entry
        self.visited.add((start_x, start_y))
        self._carve(start_x, start_y)
    
    def _carve(self, x: int, y: int) -> None:
        """Recursive carving."""
        # Get all possible directions
        directions = ['N', 'S', 'W', 'E']
        random.shuffle(directions)
        
        for direction in directions:
            if direction == 'N' and y - 2 >= 0:
                nx, ny = x, y - 2
                if (nx, ny) not in self.visited:
                    # Remove wall between
                    self.maze[x][y-1] = 0
                    self.maze[nx][ny] = 0
                    self.visited.add((nx, ny))
                    self._carve(nx, ny)
                    
            elif direction == 'S' and y + 2 < self.height:
                nx, ny = x, y + 2
                if (nx, ny) not in self.visited:
                    self.maze[x][y+1] = 0
                    self.maze[nx][ny] = 0
                    self.visited.add((nx, ny))
                    self._carve(nx, ny)
                    
            elif direction == 'W' and x - 2 >= 0:
                nx, ny = x - 2, y
                if (nx, ny) not in self.visited:
                    self.maze[x-1][y] = 0
                    self.maze[nx][ny] = 0
                    self.visited.add((nx, ny))
                    self._carve(nx, ny)
                    
            elif direction == 'E' and x + 2 < self.width:
                nx, ny = x + 2, y
                if (nx, ny) not in self.visited:
                    self.maze[x+1][y] = 0
                    self.maze[nx][ny] = 0
                    self.visited.add((nx, ny))
                    self._carve(nx, ny)