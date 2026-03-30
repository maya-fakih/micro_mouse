from src.utility.point import Point
from src.utility.direction import Direction
from src.workspace import Workspace


class Car:
    def __init__(self, position: Point, direction: Direction, workspace: Workspace):
        self.position = position
        self.direction = direction
        self.workspace = workspace
        self.last_move_successful = True
        self.rotation_angle = 0

    def move(self, direction: Direction):
        """Move the car in the specified direction."""
        # Calculate rotation needed
        current = int(self.direction.value)
        target = int(direction.value)
        cw_dist = (target - current) % 4
        ccw_dist = (current - target) % 4
        
        # Determine shortest rotation
        if cw_dist <= ccw_dist:
            rotation_steps = cw_dist
            rotation_dir = 1  # Clockwise
        else:
            rotation_steps = ccw_dist
            rotation_dir = -1  # Counter-clockwise
        
        # Apply rotation
        for _ in range(rotation_steps):
            if rotation_dir == 1:
                self.rotate_cw()
            else:
                self.rotate_ccw()
        
        # Calculate new position
        new_position = Point(self.position.x, self.position.y)
        if self.direction == Direction.NORTH:
            new_position.x -= 1
        elif self.direction == Direction.SOUTH:
            new_position.x += 1
        elif self.direction == Direction.WEST:
            new_position.y -= 1
        elif self.direction == Direction.EAST:
            new_position.y += 1
        
        # Check bounds and walls
        if not (0 <= new_position.x < self.workspace.height and 0 <= new_position.y < self.workspace.width):
            self.last_move_successful = False
            return False
        
        if self.workspace.is_wall(new_position):
            self.last_move_successful = False
            return False
        
        # Perform move
        self.position = new_position
        self.last_move_successful = True
        return True

    def rotate_cw(self):
        self.direction = Direction((int(self.direction.value) + 1) % 4)
        self.rotation_angle = (self.rotation_angle + 90) % 360

    def rotate_ccw(self):
        self.direction = Direction((int(self.direction.value) - 1) % 4)
        self.rotation_angle = (self.rotation_angle - 90) % 360
    
    def get_position(self):
        return (self.position.x, self.position.y)
    
    def get_rotation_angle(self):
        return self.rotation_angle
    
    def was_move_successful(self):
        return self.last_move_successful