"""
游戏包初始化
"""
from .minesweeper import Minesweeper
from .sudoku import Sudoku
from .tetris import Tetris
from .maze import Maze
from .snake import Snake
from .gomoku import Gomoku
from .chess import InternationalChess

__all__ = ['Minesweeper', 'Sudoku', 'Tetris', 'Maze', 'Snake', 'Gomoku', 'InternationalChess']