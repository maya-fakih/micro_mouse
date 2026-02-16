from src import Car, Workspace, Point, Direction


def main():
    workspace = Workspace(5, 5)
    car = Car(Point(0, 0), Direction.NORTH, workspace)
    car.move(Direction.EAST)
    car.move(Direction.SOUTH)
    car.move(Direction.WEST)
    car.move(Direction.NORTH)


if __name__ == "__main__":
    main()
