import csv
import os
import random

from src.utility.point import Point


def list_datasets():
    data_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    if not os.path.isdir(data_dir):
        return []
    return sorted(f for f in os.listdir(data_dir) if f.endswith('.csv'))


def get_data_path(filename):
    return os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'data', filename))


def spawn_objects(workspace, dataset_path, n_objects):
    """
    Generator yielding (row, col, data_dict) for n_objects objects placed on
    free cells with attributes sampled from the dataset's value pools.
    """
    rows = []
    with open(dataset_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    if not rows:
        return

    columns = list(rows[0].keys())
    pools = {col: [r[col] for r in rows] for col in columns}

    free_cells = [
        (r, c)
        for r in range(workspace.height)
        for c in range(workspace.width)
        if not workspace.is_wall(Point(r, c))
    ]

    if not free_cells:
        return

    chosen = random.sample(free_cells, min(n_objects, len(free_cells)))
    for row, col in chosen:
        data = {col: random.choice(pools[col]) for col in columns}
        yield (row, col, data)
