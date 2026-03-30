from typing import Any
from .maze_generator import MazeGenerator
import random
from collections import deque


class BFSGenerator(MazeGenerator):
    def __init__(self, settings_dict: dict[str, Any]) -> None:
        super().__init__(settings_dict)

    def generate(self) -> None:
        """Generate maze using BFS."""
        start_x, start_y = self.entry
        self.maze[start_x][start_y] = 0
        self.visited.add((start_x, start_y))
        
        queue = deque()
        
        # Add initial walls to queue
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            wx, wy = start_x + dx, start_y + dy
            if 0 <= wx < self.width and 0 <= wy < self.height:
                cx, cy = start_x + dx*2, start_y + dy*2
                if 0 <= cx < self.width and 0 <= cy < self.height:
                    queue.append((wx, wy, start_x, start_y, cx, cy))
        
        while queue:
            wx, wy, x1, y1, x2, y2 = queue.popleft()
            
            if (x2, y2) not in self.visited:
                self.maze[wx][wy] = 0
                self.maze[x2][y2] = 0
                self.visited.add((x2, y2))
                
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nwx, nwy = x2 + dx, y2 + dy
                    if 0 <= nwx < self.width and 0 <= nwy < self.height:
                        ncx, ncy = x2 + dx*2, y2 + dy*2
                        if 0 <= ncx < self.width and 0 <= ncy < self.height:
                            if (ncx, ncy) not in self.visited:
                                queue.append((nwx, nwy, x2, y2, ncx, ncy))