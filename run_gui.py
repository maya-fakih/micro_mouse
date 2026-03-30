#!/usr/bin/env python3
"""Main entry point to run the Maze GUI."""

import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.gui import Board

def main():
    """Main function to run the GUI."""
    num_rows = 21
    num_cols = 21
    
    print("=" * 60)
    print("🐭 MICRO MOUSE MAZE - Professional Edition")
    print("=" * 60)
    print("Controls:")
    print("  🎮 Directional Pad - Move the mouse")
    print("  🔄 RESET - Return to start position")
    print("  📍 STATUS - Show current position")
    print("  🗺️ Algorithm Buttons - Generate different mazes")
    print("  🖱️ Click on grid - Add/remove walls")
    print("=" * 60)
    
    # Create board with professional gamepad-style controller
    board = Board(
        start=(1, 1),
        goal=(num_rows-2, num_cols-2),
        num_rows=num_rows,
        num_cols=num_cols,
        win_w=1000,
        win_h=720
    )
    
    try:
        board.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    finally:
        board.close()

if __name__ == "__main__":
    main()