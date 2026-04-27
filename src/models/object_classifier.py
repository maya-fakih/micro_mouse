import sys
import os
import importlib
import csv
import numpy as np

_VENDOR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'vendor', 'ML_model_evaluation')
)


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


class ObjectClassifier:
    """
    Trains on a CSV dataset (features = all cols except last, target = last col)
    and classifies spawned objects by predicted label.
    """

    def __init__(self, dataset_path, model_type='tree'):
        self.model_type = model_type
        self.classes = []
        self._feature_cols = []
        self._col_encoders = {}
        self._model = None
        self._train(dataset_path)

    def _train(self, dataset_path):
        rows = []
        with open(dataset_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)

        if not rows:
            raise ValueError(f"Dataset is empty: {dataset_path}")

        cols = list(rows[0].keys())
        self._feature_cols = cols[:-1]
        target_col = cols[-1]

        col_encoders = {}
        X = []
        for row in rows:
            feat = []
            for col in self._feature_cols:
                val = row[col]
                try:
                    feat.append(float(val))
                except ValueError:
                    if col not in col_encoders:
                        col_encoders[col] = {}
                    enc = col_encoders[col]
                    if val not in enc:
                        enc[val] = len(enc)
                    feat.append(float(enc[val]))
            X.append(feat)

        raw_targets = [row[target_col] for row in rows]
        unique = list(dict.fromkeys(raw_targets))
        self.classes = unique
        target_enc = {v: i for i, v in enumerate(unique)}
        y = np.array([target_enc[t] for t in raw_targets])

        self._col_encoders = col_encoders
        self._model = _load_model(self.model_type)
        self._model.train(np.array(X, dtype=float), y)

    def predict(self, data_dict):
        """Return predicted class label (string) for a single data_dict object."""
        feat = []
        for col in self._feature_cols:
            val = data_dict.get(col, '')
            try:
                feat.append(float(val))
            except ValueError:
                enc = self._col_encoders.get(col, {})
                feat.append(float(enc.get(val, 0)))
        pred_idx = int(self._model.predict(np.array([feat], dtype=float))[0])
        if 0 <= pred_idx < len(self.classes):
            return self.classes[pred_idx]
        return 'unknown'
