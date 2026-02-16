from src.utility import Point, Direction
from typing import List
from src.workspace import Workspace


class Car:
    def __init__(self, position: Point, direction: Direction, workspace: Workspace):
        self.position = position
        self.direction = direction
        self.workspace = workspace

    def move(self, direction: Direction):
        current = int(self.direction.value)
        target = int(direction.value)
        cw_dist = (target - current) % 4
        ccw_dist = (current - target) % 4
        if cw_dist <= ccw_dist:
            for _ in range(cw_dist):
                self.rotate_cw()
        else:
            for _ in range(ccw_dist):
                self.rotate_ccw()
        if self.direction == Direction.NORTH:
            self.position.x -= 1
        elif self.direction == Direction.SOUTH:
            self.position.x += 1
        elif self.direction == Direction.WEST:
            self.position.y -= 1
        elif self.direction == Direction.EAST:
            self.position.y += 1
        if not (0 <= self.position.x < self.workspace.height and 0 <= self.position.y < self.workspace.width):
            raise ValueError("Out of workspace bounds")
        print(f"Moved to {self.position} facing {self.direction.name}")

    def rotate_cw(self):
        self.direction = Direction((int(self.direction.value) + 1) % 4)
        print(f"Rotated CW to {self.direction.name}")

    def rotate_ccw(self):
        self.direction = Direction((int(self.direction.value) - 1) % 4)
        print(f"Rotated CCW to {self.direction.name}")

