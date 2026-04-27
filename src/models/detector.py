import sys
import os
import importlib
import numpy as np

from src.utility.point import Point

_VENDOR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'vendor', 'ML_model_evaluation')
)

# Cell type labels
CELL_DEAD_END  = 1
CELL_CORRIDOR  = 2
CELL_TURN      = 3
CELL_JUNCTION  = 4


def _load_model(model_type):
    if not os.path.isdir(_VENDOR):
        raise RuntimeError("vendor/ not found — run 'make pull' first.")
    if _VENDOR not in sys.path:
        sys.path.insert(0, _VENDOR)
    if model_type == 'tree':
        mod = importlib.import_module('models.decision_tree')
        return mod.DecisionTreeModel(max_depth=5, debug=False)
    mod = importlib.import_module('models.svm')
    return mod.SVMModel(kernel='rbf', C=1.0, debug=False)


def _wall_flags(workspace, row, col):
    def walled(r, c):
        if r < 0 or r >= workspace.height or c < 0 or c >= workspace.width:
            return 1.0
        return 1.0 if workspace.is_wall(Point(r, c)) else 0.0
    return [walled(row - 1, col), walled(row + 1, col),
            walled(row, col + 1), walled(row, col - 1)]


def _cell_label(flags):
    n, s, e, w = flags
    walls = int(n + s + e + w)
    if walls >= 3:
        return CELL_DEAD_END
    if walls == 2:
        return CELL_CORRIDOR if (n and s) or (e and w) else CELL_TURN
    return CELL_JUNCTION


class CellDetector:
    """Uses an ML model from ML_model_evaluation to classify maze cells."""

    def __init__(self, workspace):
        self.workspace = workspace

    def detect(self, model_type='tree'):
        """
        Return dict {(row, col): label} for all non-wall free cells.
        Labels: CELL_DEAD_END, CELL_CORRIDOR, CELL_TURN, CELL_JUNCTION.
        """
        ws = self.workspace
        X, y_true, cells = [], [], []

        for row in range(ws.height):
            for col in range(ws.width):
                if ws.is_wall(Point(row, col)):
                    continue
                flags = _wall_flags(ws, row, col)
                X.append(flags)
                y_true.append(_cell_label(flags))
                cells.append((row, col))

        if not cells:
            return {}

        X_arr = np.array(X, dtype=float)
        y_arr = np.array(y_true)

        model = _load_model(model_type)
        model.train(X_arr, y_arr)
        predictions = model.predict(X_arr)

        return {cell: int(pred) for cell, pred in zip(cells, predictions)}
