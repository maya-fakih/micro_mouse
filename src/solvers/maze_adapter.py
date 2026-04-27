from src.utility.point import Point


class MazeAdapter:
    """Bridges micro_mouse Workspace to the A-maze-ing MazeSolver interface."""

    _DELTAS = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}

    def __init__(self, workspace, entry, exit_pos):
        # entry / exit_pos in (col, row) — matches generator convention
        self.workspace = workspace
        self.entry = entry
        self.exit = exit_pos
        self.width = workspace.width
        self.height = workspace.height

    def get_neighbors(self, cell):
        col, row = cell
        result = []
        for d, (dc, dr) in self._DELTAS.items():
            nc, nr = col + dc, row + dr
            if 0 <= nc < self.width and 0 <= nr < self.height:
                result.append((nc, nr, d))
        return result

    def has_wall(self, cell, direction):
        col, row = cell
        dc, dr = self._DELTAS[direction]
        nc, nr = col + dc, row + dr
        if not (0 <= nc < self.width and 0 <= nr < self.height):
            return True
        return self.workspace.is_wall(Point(nr, nc))
