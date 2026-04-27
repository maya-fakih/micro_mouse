# Micro Mouse Maze

A pygame maze simulation where an agent navigates procedurally generated mazes, solves them with pathfinding algorithms, and classifies objects spawned from real datasets using machine learning.

Part of the ML lab course — a starting ground for building a space-exploring ML platform for agent AI robots.

## Quick Start

```bash
make pull        # clone vendor dependencies
python run_gui.py
```

Controls: **arrow keys** or D-pad buttons to move · click grid cells to toggle walls.

---

## Architecture

```
micro_mouse/
├── run_gui.py                   entry point
├── config.json                  runtime config (dataset, model, n_objects…)
├── data/                        CSV datasets for simulation
│   ├── Iris.csv
│   └── wdbc.data.csv
├── src/
│   ├── workspace.py             grid state (1=wall, 0=free)
│   ├── car.py                   agent: position, direction, movement
│   ├── simulation.py            spawn_objects() generator
│   ├── generators/
│   │   └── amazeing_bridge.py   vendor wrapper — get_generator(), to_grid()
│   ├── solvers/
│   │   ├── maze_adapter.py      bridges Workspace → vendor solver interface
│   │   └── solver_manager.py    BFS / DFS / A* via vendor, returns (row,col) path
│   ├── models/
│   │   └── object_classifier.py trains on CSV, predicts target column
│   └── gui/
│       ├── board.py             pygame main loop + rendering
│       └── button_actions.py    controller callbacks
└── vendor/                      populated by `make pull`
    ├── A-maze-ing/              maze generation + pathfinding
    └── ML_model_evaluation/     DecisionTree + SVM models
```

---

## Module Dependency Graph

```mermaid
graph TD
    GUI["board.py\npygame loop"]
    BA["button_actions.py"]
    WS["workspace.py"]
    CAR["car.py"]
    SIM["simulation.py"]
    BRIDGE["amazeing_bridge.py"]
    ADAPT["maze_adapter.py"]
    MGR["solver_manager.py"]
    CLF["object_classifier.py"]
    VEND_MAZE["vendor/A-maze-ing"]
    VEND_ML["vendor/ML_model_evaluation"]
    DATA["data/*.csv"]

    GUI --> BA
    GUI --> WS
    GUI --> CAR
    BA --> BRIDGE
    BA --> MGR
    BA --> CLF
    BA --> SIM
    BRIDGE --> VEND_MAZE
    MGR --> ADAPT
    ADAPT --> WS
    MGR --> VEND_MAZE
    CLF --> VEND_ML
    CLF --> DATA
    SIM --> DATA
    SIM --> WS
    CAR --> WS
```

---

## Flow 1 — Maze Generation

```mermaid
sequenceDiagram
    participant User
    participant GUI as board.py
    participant BA as button_actions.py
    participant Bridge as amazeing_bridge.py
    participant Vendor as vendor/A-maze-ing
    participant WS as workspace.py

    User->>GUI: click DFS / BFS / Prim / HK
    GUI->>BA: generate_maze(algo)
    BA->>Bridge: get_generator(algo, rows, cols, perfect=False)
    Bridge->>Vendor: instantiate generator with no-logo mixin
    Bridge-->>BA: generator instance
    BA->>Vendor: generator.generate()
    Vendor-->>BA: gen.maze[x][y] bitmask grid
    BA->>Bridge: to_grid(gen, rows, cols)
    Note over Bridge: logical cell (x,y) maps to grid[2y+1][2x+1]<br/>EAST / SOUTH bits open passage walls
    Bridge-->>BA: grid[row][col]  (1=wall 0=free)
    BA->>WS: set_wall() for each cell
    BA->>GUI: reset agent + redraw
```

---

## Flow 2 — Pathfinding

```mermaid
sequenceDiagram
    participant User
    participant GUI as board.py
    participant BA as button_actions.py
    participant MGR as solver_manager.py
    participant ADAPT as maze_adapter.py
    participant Vendor as vendor/A-maze-ing

    User->>GUI: click BFS / DFS / A*
    GUI->>BA: solve_maze(algo)
    BA->>MGR: SolverManager(workspace, start, goal)
    MGR->>ADAPT: build adapter with entry/exit in col,row coords
    BA->>MGR: solve(algo)
    MGR->>Vendor: instantiate solver with adapter
    Vendor->>ADAPT: get_neighbors(cell), has_wall(cell, dir)
    ADAPT-->>Vendor: neighbour list
    Vendor-->>MGR: solution_cells as (col, row) list
    MGR-->>BA: path as (row, col) list
    BA->>GUI: solution_path = path — draw green overlay
```

---

## Flow 3 — Simulation & ML Classification

```mermaid
sequenceDiagram
    participant User
    participant GUI as board.py
    participant BA as button_actions.py
    participant SIM as simulation.py
    participant CLF as object_classifier.py
    participant Vendor as vendor/ML_model_evaluation
    participant CSV as data/*.csv

    User->>GUI: pick dataset, set N, click SPAWN
    GUI->>BA: spawn_simulation()
    BA->>CLF: ObjectClassifier(dataset_path, model_type)
    CLF->>CSV: read all rows
    Note over CLF: features = all columns except last<br/>target  = last column
    CLF->>Vendor: model.train(X, y)
    CLF-->>BA: trained classifier
    BA->>SIM: spawn_objects(workspace, dataset_path, N)
    SIM->>CSV: build per-column value pools
    SIM->>SIM: random sample N free cells
    SIM-->>BA: yield (row, col, data_dict)
    BA->>GUI: store as white dots — no label shown yet

    Note over GUI: agent navigates with arrow keys

    User->>GUI: agent steps onto an object cell
    GUI->>CLF: classifier.predict(data_dict)
    CLF->>Vendor: model.predict(features)
    Vendor-->>CLF: class index
    CLF-->>GUI: predicted label e.g. "Iris-setosa"
    GUI->>GUI: INFO panel shows attributes + prediction
```

---

## Vendor Dependencies

| Repo | What it provides |
|---|---|
| [maya-fakih/A-maze-ing](https://github.com/maya-fakih/A-maze-ing) | Maze generators (DFS, BFS, Prim, Hunt-and-Kill) and pathfinding solvers (BFS, DFS, A*). Cells encoded as bitmasks; supports perfect (spanning-tree) or loopy mazes. |
| [maya-fakih/ML_model_evaluation](https://github.com/maya-fakih/ML_model_evaluation) | Decision Tree and SVM classifiers with a unified `.train(X, y)` / `.predict(X)` interface built on numpy. |

Run `make pull` to clone both into `vendor/`.

---

## Config

`config.json` controls the simulation defaults loaded at startup:

```json
{
    "dataset":      "Iris.csv",
    "model":        "tree",
    "n_objects":    20,
    "maze_algo":    "DFS",
    "perfect_maze": false
}
```

`perfect_maze: false` produces loopy mazes with multiple paths between cells.  
`perfect_maze: true` gives a strict spanning-tree maze (one unique path everywhere).
