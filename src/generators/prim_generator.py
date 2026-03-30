from typing import Any
from .maze_generator import MazeGenerator
import random


class PrimGenerator(MazeGenerator):
    def __init__(self, settings_dict: dict[str, Any]) -> None:
        super().__init__(settings_dict)

    def generate(self) -> None:
        """Generate maze using Prim's algorithm."""
        start_x, start_y = self.entry
        self.maze[start_x][start_y] = 0
        self.visited.add((start_x, start_y))
        
        # Frontier list: (wall_x, wall_y, cell1_x, cell1_y, cell2_x, cell2_y)
        frontier = []
        
        # Add initial frontier walls
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            wx, wy = start_x + dx, start_y + dy
            if 0 <= wx < self.width and 0 <= wy < self.height:
                cx, cy = start_x + dx*2, start_y + dy*2
                if 0 <= cx < self.width and 0 <= cy < self.height:
                    frontier.append((wx, wy, start_x, start_y, cx, cy))
        
        while frontier:
            # Pick random frontier wall
            idx = random.randint(0, len(frontier) - 1)
            wx, wy, x1, y1, x2, y2 = frontier.pop(idx)
            
            # If the second cell is not visited
            if (x2, y2) not in self.visited:
                # Remove the wall
                self.maze[wx][wy] = 0
                self.maze[x2][y2] = 0
                self.visited.add((x2, y2))
                
                # Add new frontier walls around the new cell
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nwx, nwy = x2 + dx, y2 + dy
                    if 0 <= nwx < self.width and 0 <= nwy < self.height:
                        ncx, ncy = x2 + dx*2, y2 + dy*2
                        if 0 <= ncx < self.width and 0 <= ncy < self.height:
                            if (ncx, ncy) not in self.visited:
                                frontier.append((nwx, nwy, x2, y2, ncx, ncy))