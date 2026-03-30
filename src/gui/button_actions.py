"""Button Actions - Gamepad-style controller"""

from src.utility.direction import Direction
from src.utility.point import Point  # Add this import!
from src.generators import DFSGenerator, BFSGenerator, PrimGenerator, HuntKillGenerator


class ButtonActions:
    def __init__(self, board):
        self.board = board
        self.message_timer = 0
        self.current_message = ""
    
    def show_message(self, message, is_error=False):
        self.current_message = message
        self.message_timer = 60
        if is_error:
            self.board.show_warning(True)
            print(f"⚠️ {message}")
        else:
            print(f"✅ {message}")
    
    def on_button_north(self):
        if self.board.agent:
            if self.board.agent.move(Direction.NORTH):
                self.show_message("⬆️ Moving NORTH", False)
                self.board.draw_grid()
            else:
                self.show_message("🧱 WALL! Cannot move NORTH!", True)
                self.board.draw_grid()
    
    def on_button_east(self):
        if self.board.agent:
            if self.board.agent.move(Direction.EAST):
                self.show_message("➡️ Moving EAST", False)
                self.board.draw_grid()
            else:
                self.show_message("🧱 WALL! Cannot move EAST!", True)
                self.board.draw_grid()
    
    def on_button_south(self):
        if self.board.agent:
            if self.board.agent.move(Direction.SOUTH):
                self.show_message("⬇️ Moving SOUTH", False)
                self.board.draw_grid()
            else:
                self.show_message("🧱 WALL! Cannot move SOUTH!", True)
                self.board.draw_grid()
    
    def on_button_west(self):
        if self.board.agent:
            if self.board.agent.move(Direction.WEST):
                self.show_message("⬅️ Moving WEST", False)
                self.board.draw_grid()
            else:
                self.show_message("🧱 WALL! Cannot move WEST!", True)
                self.board.draw_grid()
    
    def on_button_reset(self):
        self.board.reset_agent()
        self.show_message("🔄 Agent reset to start!", False)
        self.board.draw_grid()
    
    def on_button_status(self):
        if self.board.agent:
            pos = self.board.agent.get_position()
            direction = self.board.agent.direction.name
            self.show_message(f"📍 Position: ({pos[0]}, {pos[1]}) | 🧭 Facing: {direction}", False)
            self.board.draw_grid()
    
    def generate_maze(self, algo_name):
        self.show_message(f"🔄 Generating {algo_name} maze...", False)
        
        settings = {
            "width": self.board.num_cols,
            "height": self.board.num_rows,
            "entry": self.board.start,
            "exit": self.board.goal,
            "perfect": False
        }
        
        if algo_name == 'DFS':
            generator = DFSGenerator(settings)
        elif algo_name == 'BFS':
            generator = BFSGenerator(settings)
        elif algo_name == 'Prim':
            generator = PrimGenerator(settings)
        elif algo_name == 'HuntKill':
            generator = HuntKillGenerator(settings)
        else:
            generator = DFSGenerator(settings)
        
        generator.generate()
        maze_array = generator.get_2d_array()
        
        for i in range(self.board.num_rows):
            for j in range(self.board.num_cols):
                self.board.grid[i][j] = maze_array[j][i]
                self.board.workspace.set_wall(Point(i, j), maze_array[j][i] == 1)
        
        self.board.reset_agent()
        self.board.grid_surface = None
        self.board.draw_grid()
        self.show_message(f"✅ {algo_name} maze generated!", False)
    
    def on_algorithm_dfs(self):
        self.generate_maze('DFS')
    
    def on_algorithm_bfs(self):
        self.generate_maze('BFS')
    
    def on_algorithm_prim(self):
        self.generate_maze('Prim')
    
    def on_algorithm_huntkill(self):
        self.generate_maze('HuntKill')
    
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