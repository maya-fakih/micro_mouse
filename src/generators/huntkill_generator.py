from typing import Any, Tuple, Optional, List
from .maze_generator import MazeGenerator
import random


class HuntKillGenerator(MazeGenerator):
    def __init__(self, settings_dict: dict[str, Any]) -> None:
        super().__init__(settings_dict)

    def get_unvisited_neighbors(self, x: int, y: int) -> List[Tuple[int, int, int, int]]:
        """Get unvisited cells that are 2 steps away."""
        neighbors = []
        
        # North
        if y - 2 >= 0 and self.maze[x][y-2] == 1:
            neighbors.append((x, y-2, x, y-1))
        # South
        if y + 2 < self.height and self.maze[x][y+2] == 1:
            neighbors.append((x, y+2, x, y+1))
        # West
        if x - 2 >= 0 and self.maze[x-2][y] == 1:
            neighbors.append((x-2, y, x-1, y))
        # East
        if x + 2 < self.width and self.maze[x+2][y] == 1:
            neighbors.append((x+2, y, x+1, y))
        
        return neighbors

    def hunt(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Scan the ENTIRE maze to find an unvisited cell adjacent to a visited cell.
        Returns (nx, ny, wx, wy) where (nx, ny) is the unvisited cell and
        (wx, wy) is the wall between it and the visited neighbor.
        """
        for y in range(1, self.height-1, 2):
            for x in range(1, self.width-1, 2):
                # Only consider unvisited cells (still a wall)
                if self.maze[x][y] == 1:
                    # Check all four directions for a VISITED cell 2 steps away
                    # North
                    if y - 2 >= 0 and self.maze[x][y-2] == 0:
                        return (x, y, x, y-1)
                    # South
                    if y + 2 < self.height and self.maze[x][y+2] == 0:
                        return (x, y, x, y+1)
                    # West
                    if x - 2 >= 0 and self.maze[x-2][y] == 0:
                        return (x, y, x-1, y)
                    # East
                    if x + 2 < self.width and self.maze[x+2][y] == 0:
                        return (x, y, x+1, y)
        return None

    def generate(self) -> None:
        """Generate maze using Hunt and Kill algorithm."""
        # Start from entry
        current_x, current_y = self.entry
        self.maze[current_x][current_y] = 0
        
        iterations = 0
        max_iterations = (self.width * self.height) * 2
        
        while iterations < max_iterations:
            iterations += 1
            
            # KILL PHASE - Try to extend current path
            neighbors = self.get_unvisited_neighbors(current_x, current_y)
            
            if neighbors:
                # Randomly pick an unvisited neighbor
                nx, ny, wx, wy = random.choice(neighbors)
                # Carve the path
                self.maze[wx][wy] = 0
                self.maze[nx][ny] = 0
                current_x, current_y = nx, ny
                continue
            
            # HUNT PHASE - Find any unvisited cell connected to visited area
            hunt_result = self.hunt()
            if hunt_result:
                nx, ny, wx, wy = hunt_result
                # Connect it to the visited area
                self.maze[wx][wy] = 0
                self.maze[nx][ny] = 0
                current_x, current_y = nx, ny
            else:
                # No more cells to hunt, we're done
                break
        
        # Ensure exit is open
        ex, ey = self.exit
        self.maze[ex][ey] = 0
        
        # Add some loops to make it interesting (optional)
        self._add_loops()
    
    def _add_loops(self):
        """Add random extra openings to create loops."""
        for _ in range(self.width * self.height // 20):
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            
            # Check if this is a wall cell
            if self.maze[x][y] == 1:
                # Count how many open neighbors
                open_count = 0
                if self.maze[x-1][y] == 0:
                    open_count += 1
                if self.maze[x+1][y] == 0:
                    open_count += 1
                if self.maze[x][y-1] == 0:
                    open_count += 1
                if self.maze[x][y+1] == 0:
                    open_count += 1
                
                # If it has at least 2 open neighbors, make it open
                if open_count >= 2:
                    self.maze[x][y] = 0