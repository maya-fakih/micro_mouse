from dataclasses import dataclass
from enum import IntEnum
from typing import Literal


class Direction(IntEnum):
    NORTH = '0'
    WEST = '1'
    SOUTH = '2'
    EAST = '3'
