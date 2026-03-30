from abc import ABC, abstractmethod
from typing import Any, List, Tuple, Set
import random


class MazeGenerator(ABC):
    def __init__(self, settings_dict: dict[str, Any]) -> None:
        self.width: int = int(settings_dict.get("width", 21))
        self.height: int = int(settings_dict.get("height", 21))
        self.entry: Tuple[int, int] = tuple(settings_dict.get("entry", (1, 1)))
        self.exit: Tuple[int, int] = tuple(settings_dict.get("exit", (self.width-2, self.height-2)))
        
        # Initialize maze with all walls (1 = wall)
        self.maze = [[1 for _ in range(self.height)] for _ in range(self.width)]
        
        # Open entry and exit
        ex, ey = self.entry
        self.maze[ex][ey] = 0
        ex, ey = self.exit
        self.maze[ex][ey] = 0
        
        self.visited: Set[Tuple[int, int]] = set()

    @abstractmethod
    def generate(self) -> None:
        raise NotImplementedError

    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int, str]]:
        """Get valid neighbors (2 steps away for carving)."""
        neighbors = []
        # North (up 2)
        if y - 2 >= 0:
            neighbors.append((x, y - 2, 'N'))
        # South (down 2)
        if y + 2 < self.height:
            neighbors.append((x, y + 2, 'S'))
        # West (left 2)
        if x - 2 >= 0:
            neighbors.append((x - 2, y, 'W'))
        # East (right 2)
        if x + 2 < self.width:
            neighbors.append((x + 2, y, 'E'))
        return neighbors

    def get_wall_between(self, x1: int, y1: int, x2: int, y2: int) -> Tuple[int, int]:
        """Get the wall cell between two cells."""
        return ((x1 + x2) // 2, (y1 + y2) // 2)

    def get_2d_array(self) -> List[List[int]]:
        """Return maze as 2D array (1=wall, 0=free)."""
        return self.maze