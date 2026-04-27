"""
Thin wrappers around vendor/A-maze-ing generators.
Disables the 42-logo and provides a helper to convert the bitmask maze
to the micro_mouse 0/1 grid format.
"""
import sys
import os

_VENDOR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'vendor', 'A-maze-ing')
)


def _ensure_vendor():
    if not os.path.isdir(_VENDOR):
        raise RuntimeError("vendor/ not found — run 'make pull' first.")
    if _VENDOR not in sys.path:
        sys.path.insert(0, _VENDOR)


class _NoLogo:
    """Mixin: replace the 42-logo with a no-op so it doesn't block cells."""
    def add_42_logo(self):
        self.logo_cells = set()


def _make_bridge(base_cls_name):
    _ensure_vendor()
    import importlib
    mod_map = {
        'DFSGenerator':      'mazegen.generators.dfs_generator',
        'BFSGenerator':      'mazegen.generators.bfs_generator',
        'PrimGenerator':     'mazegen.generators.prim_generator',
        'HuntKillGenerator': 'mazegen.generators.huntkill_generator',
    }
    mod = importlib.import_module(mod_map[base_cls_name])
    base = getattr(mod, base_cls_name)
    return type(f'Bridge{base_cls_name}', (_NoLogo, base), {})


def get_generator(algo, num_rows, num_cols, perfect=False):
    """
    Return a ready-to-use A-maze-ing generator instance.

    algo     : 'DFS' | 'BFS' | 'Prim' | 'HuntKill'
    num_rows / num_cols : board grid dimensions (e.g. 21×21)
    perfect  : True = spanning-tree maze, False = add random loops
    """
    cls_map = {
        'DFS': 'DFSGenerator', 'BFS': 'BFSGenerator',
        'Prim': 'PrimGenerator', 'HuntKill': 'HuntKillGenerator',
    }
    bridge_cls = _make_bridge(cls_map[algo])
    w = (num_cols - 1) // 2
    h = (num_rows - 1) // 2
    settings = {
        "width":                w,
        "height":               h,
        "entry":                (0, 0),
        "exit":                 (w - 1, h - 1),
        "perfect":              perfect,
        "generation_algorithm": algo.lower(),
        "solver_algorithm":     "bfs",
        "display_mode":         "ascii",
        "shape":                "square",
    }
    return bridge_cls(settings)


def to_grid(gen, num_rows, num_cols):
    """
    Convert A-maze-ing bitmask maze → micro_mouse 0/1 grid[row][col].
    1 = wall, 0 = free.
    """
    EAST  = 0b0010
    SOUTH = 0b0100

    grid = [[1] * num_cols for _ in range(num_rows)]

    for x in range(gen.width):      # col in logical maze
        for y in range(gen.height):  # row in logical maze
            gr, gc = 2 * y + 1, 2 * x + 1
            if 0 <= gr < num_rows and 0 <= gc < num_cols:
                grid[gr][gc] = 0    # navigable cell

            cell_val = gen.maze[x][y]

            # East passage → remove wall between (x,y) and (x+1,y)
            if x + 1 < gen.width and not (cell_val & EAST):
                if gc + 1 < num_cols:
                    grid[gr][gc + 1] = 0

            # South passage → remove wall between (x,y) and (x,y+1)
            if y + 1 < gen.height and not (cell_val & SOUTH):
                if gr + 1 < num_rows:
                    grid[gr + 1][gc] = 0

    return grid
