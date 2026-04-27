#!/usr/bin/env python3
"""Main entry point to run the Maze GUI."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.gui import Board


def main():
    board = Board(
        start=(1, 1),
        num_rows=21,
        num_cols=21,
        win_w=1280,
        win_h=900,
    )
    try:
        board.run()
    except KeyboardInterrupt:
        pass
    finally:
        board.close()


if __name__ == "__main__":
    main()
