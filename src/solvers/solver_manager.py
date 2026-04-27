import sys
import os

from .maze_adapter import MazeAdapter

_VENDOR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'vendor', 'A-maze-ing')
)

_ALGO_MAP = {'bfs': 'BFSolver', 'dfs': 'DFSolver', 'astar': 'AStarSolver'}


def _load_solver(algo):
    if not os.path.isdir(_VENDOR):
        raise RuntimeError("vendor/ not found — run 'make pull' first.")
    if _VENDOR not in sys.path:
        sys.path.insert(0, _VENDOR)
    mod_map = {
        'bfs':   ('mazegen.solvers.bfs_solver',   'BFSolver'),
        'dfs':   ('mazegen.solvers.dfs_solver',   'DFSolver'),
        'astar': ('mazegen.solvers.astar_solver', 'AStarSolver'),
    }
    mod_name, cls_name = mod_map[algo]
    import importlib
    mod = importlib.import_module(mod_name)
    return getattr(mod, cls_name)


class SolverManager:
    def __init__(self, workspace, start, goal):
        # Board uses (row, col); adapter needs (col, row)
        entry = (start[1], start[0])
        exit_pos = (goal[1], goal[0])
        self.adapter = MazeAdapter(workspace, entry, exit_pos)

    def solve(self, algo='bfs'):
        """Return list of (row, col) cells on the solution path."""
        solver_cls = _load_solver(algo)
        solver = solver_cls(self.adapter)
        solver.solve()
        # solution_cells are (col, row) — flip to (row, col) for board
        return [(row, col) for col, row in solver.solution_cells]
