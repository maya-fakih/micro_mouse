"""Button Actions - Gamepad-style controller"""

from src.utility.direction import Direction
from src.utility.point import Point


class ButtonActions:
    def __init__(self, board):
        self.board = board
        self.message_timer = 0
        self.current_message = ""

    def show_message(self, message, is_error=False):
        self.current_message = message
        self.message_timer = 90
        if is_error:
            self.board.show_warning(True)
            print(f"Warning: {message}")
        else:
            print(f"OK: {message}")

    # ── D-pad ─────────────────────────────────────────────────────────────────

    def on_button_north(self):
        if self.board.agent:
            if self.board.agent.move(Direction.NORTH):
                self.show_message("Moving NORTH", False)
            else:
                self.show_message("WALL! Cannot move NORTH!", True)
            self.board.draw_grid()

    def on_button_east(self):
        if self.board.agent:
            if self.board.agent.move(Direction.EAST):
                self.show_message("Moving EAST", False)
            else:
                self.show_message("WALL! Cannot move EAST!", True)
            self.board.draw_grid()

    def on_button_south(self):
        if self.board.agent:
            if self.board.agent.move(Direction.SOUTH):
                self.show_message("Moving SOUTH", False)
            else:
                self.show_message("WALL! Cannot move SOUTH!", True)
            self.board.draw_grid()

    def on_button_west(self):
        if self.board.agent:
            if self.board.agent.move(Direction.WEST):
                self.show_message("Moving WEST", False)
            else:
                self.show_message("WALL! Cannot move WEST!", True)
            self.board.draw_grid()

    def on_button_reset(self):
        self.board.reset_agent()
        self.show_message("Agent reset to start!", False)
        self.board.draw_grid()

    def on_button_status(self):
        if self.board.agent:
            pos = self.board.agent.get_position()
            direction = self.board.agent.direction.name
            self.show_message(f"Pos:({pos[0]},{pos[1]}) Dir:{direction}", False)
            self.board.draw_grid()

    # ── Maze generation ───────────────────────────────────────────────────────

    def generate_maze(self, algo_name):
        from src.generators.amazeing_bridge import get_generator, to_grid
        self.show_message(f"Generating {algo_name}...", False)
        self.board.solution_path = []
        self.board.detected_cells = {}
        self.board.spawned_objects = []

        perfect = getattr(self.board, 'perfect_maze', False)
        try:
            gen = get_generator(algo_name, self.board.num_rows, self.board.num_cols, perfect=perfect)
            gen.generate()
            grid = to_grid(gen, self.board.num_rows, self.board.num_cols)
        except Exception as e:
            self.show_message(f"Gen error: {e}", True)
            return

        for i in range(self.board.num_rows):
            for j in range(self.board.num_cols):
                self.board.grid[i][j] = grid[i][j]
                self.board.workspace.set_wall(Point(i, j), grid[i][j] == 1)

        self.board.reset_agent()
        self.board.grid_surface = None
        self.board.draw_grid()
        self.show_message(f"{algo_name} maze generated!", False)

    def on_algorithm_dfs(self):      self.generate_maze('DFS')
    def on_algorithm_bfs(self):      self.generate_maze('BFS')
    def on_algorithm_prim(self):     self.generate_maze('Prim')
    def on_algorithm_huntkill(self): self.generate_maze('HuntKill')

    # ── Solver ────────────────────────────────────────────────────────────────

    def solve_maze(self, algo):
        from src.solvers import SolverManager
        self.show_message(f"Solving ({algo.upper()})...", False)
        self.board.detected_cells = {}
        try:
            mgr = SolverManager(self.board.workspace, self.board.start, self.board.goal)
            path = mgr.solve(algo)
            if path:
                self.board.solution_path = path
                self.board.needs_redraw = True
                self.show_message(f"{algo.upper()} done! {len(path)} cells", False)
            else:
                self.show_message("No solution found!", True)
        except RuntimeError as e:
            self.show_message(str(e), True)
        except Exception as e:
            self.show_message(f"Solver error: {e}", True)

    def clear_solution(self):
        self.board.solution_path = []
        self.board.needs_redraw = True
        self.show_message("Solution cleared", False)

    # ── Detector ─────────────────────────────────────────────────────────────

    def detect_cells(self, model_type):
        from src.models import CellDetector
        label = "DecisionTree" if model_type == 'tree' else "SVM"
        self.show_message(f"Detecting ({label})...", False)
        self.board.solution_path = []
        try:
            detector = CellDetector(self.board.workspace)
            self.board.detected_cells = detector.detect(model_type)
            self.board.needs_redraw = True
            self.show_message(f"{label} detection done!", False)
        except RuntimeError as e:
            self.show_message(str(e), True)
        except Exception as e:
            self.show_message(f"Detector error: {e}", True)

    def clear_detection(self):
        self.board.detected_cells = {}
        self.board.needs_redraw = True
        self.show_message("Detection cleared", False)

    # ── Simulation ────────────────────────────────────────────────────────────

    def spawn_simulation(self):
        from src.simulation import spawn_objects, get_data_path
        from src.models import ObjectClassifier

        datasets = self.board.datasets
        if not datasets:
            self.show_message("No datasets in /data!", True)
            return

        dataset_file = datasets[self.board.dataset_idx]
        dataset_path = get_data_path(dataset_file)
        n = self.board.n_objects
        model_type = self.board.sim_model

        self.show_message(f"Spawning {n} objects...", False)
        self.board.solution_path = []
        self.board.detected_cells = {}
        self.board.spawned_objects = []
        self.board.current_obj_info = None

        try:
            # Train classifier once; predict lazily when agent reaches each object
            self.board.classifier = ObjectClassifier(dataset_path, model_type)
            objects = list(spawn_objects(self.board.workspace, dataset_path, n))
            self.board.spawned_objects = objects   # (row, col, data_dict) — no label yet
            self.board.needs_redraw = True
            self.show_message(f"Spawned {len(objects)} objects!", False)
        except RuntimeError as e:
            self.show_message(str(e), True)
        except Exception as e:
            self.show_message(f"Sim error: {e}", True)

    def clear_simulation(self):
        self.board.spawned_objects = []
        self.board.needs_redraw = True
        self.show_message("Simulation cleared", False)

    # ─────────────────────────────────────────────────────────────────────────

    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0:
                self.current_message = ""
                self.board.show_warning(False)

    def get_current_message(self):
        return self.current_message

    def get_callbacks(self):
        return {
            1: self.on_button_north,
            2: self.on_button_east,
            3: self.on_button_south,
            4: self.on_button_west,
            5: self.on_button_reset,
            6: self.on_button_status,
        }
