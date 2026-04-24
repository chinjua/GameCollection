"""
游戏合集配置文件
包含颜色、尺寸等常量
"""
import os
import sys
import pygame

# 屏幕设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 750
FPS = 60

# 颜色方案
COLORS = {
    # 主色调 - 渐变背景
    'BG': (236, 240, 241),           # 背景浅灰白
    'BG_DARK': (44, 62, 80),         # 深蓝灰背景
    'BG_GRADIENT_START': (30, 41, 55),  # 渐变起始
    'BG_GRADIENT_END': (15, 25, 40),  # 渐变结束
    
    # 强调色 - 霓虹色系
    'RED': (231, 76, 60),
    'RED_NEON': (255, 89, 94),
    'GREEN': (39, 174, 96),
    'GREEN_NEON': (46, 234, 122),
    'BLUE': (52, 152, 219),
    'BLUE_NEON': (69, 170, 218),
    'ORANGE': (230, 126, 34),
    'ORANGE_NEON': (255, 150, 50),
    'PURPLE': (155, 89, 182),
    'PURPLE_NEON': (190, 100, 218),
    'YELLOW': (241, 196, 15),
    'YELLOW_NEON': (255, 220, 50),
    'CYAN': (26, 188, 156),
    'CYAN_NEON': (40, 255, 220),
    'BRASS': (181, 166, 99),  # 黄铜色
    
    # 文字色
    'TEXT_DARK': (44, 62, 80),
    'TEXT_LIGHT': (255, 255, 255),
    'TEXT_GRAY': (127, 140, 141),
    
    # 游戏专用色
    'BUTTON': (52, 152, 219),
    'BUTTON_HOVER': (41, 128, 185),
    'BUTTON_PRESSED': (30, 102, 163),
    'PANEL': (44, 62, 80),
    'GRID_LINE': (189, 195, 199),
    
    # 扫雷颜色
    'MINE_BG': (189, 195, 199),
    'MINE_REVEALED': (236, 240, 241),
    'MINE_1': (52, 152, 219),
    'MINE_2': (39, 174, 96),
    'MINE_3': (231, 76, 60),
    'MINE_4': (155, 89, 182),
    'MINE_5': (230, 126, 34),
    'MINE_6': (26, 188, 156),
    'MINE_7': (44, 62, 80),
    'MINE_8': (149, 165, 166),
    
    # 俄罗斯方块颜色 - 霓虹风格
    'TETRIS_I': (26, 188, 156),
    'TETRIS_O': (241, 196, 15),
    'TETRIS_T': (155, 89, 182),
    'TETRIS_S': (39, 174, 96),
    'TETRIS_Z': (231, 76, 60),
    'TETRIS_J': (52, 152, 219),
    'TETRIS_L': (230, 126, 34),
    
    # 游戏框架颜色
    'FRAME': (44, 62, 80),          # 框架边框
    'SHADOW': (30, 41, 55),          # 阴影
    'HIGHLIGHT': (255, 255, 255, 50),  # 高光
}

# 字体设置
import os

# 查找支持中文的系统字体
WINDOWS_FONT_DIR = os.environ.get("WINDIR", "C:\\Windows") + "\\Fonts"

# 尝试常见的中文字体文件
CHINESE_FONTS = [
    os.path.join(WINDOWS_FONT_DIR, "simhei.ttf"),       # 黑体
    os.path.join(WINDOWS_FONT_DIR, "MicrosoftYaHei.ttf"),  # 微软雅黑
    os.path.join(WINDOWS_FONT_DIR, "simsun.ttc"),       # 宋体
    os.path.join(WINDOWS_FONT_DIR, "msyh.ttc"),        # 微软雅黑
]

# 找到第一个可用的字体
_CHINESE_FONT_PATH = None
for font_path in CHINESE_FONTS:
    if os.path.exists(font_path):
        _CHINESE_FONT_PATH = font_path
        break

def get_font(size):
    """获取支持中文的字体"""
    if _CHINESE_FONT_PATH:
        return pygame.font.Font(_CHINESE_FONT_PATH, size)
    else:
        # 备用方案：使用默认字体
        return pygame.font.Font(None, size)

# 为兼容而保留
FONT_PATH = _CHINESE_FONT_PATH

FONT_SMALL = 24
FONT_MIDDLE = 32
FONT_LARGE = 40
FONT_TITLE = 56

# 按钮尺寸
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50

# 扫雷设置
MINESWEEPER_EASY_SIZE = 9
MINESWEEPER_EASY_MINES = 10
MINESWEEPER_MED_SIZE = 16
MINESWEEPER_MED_MINES = 40

# 数独设置
SUDOKU_CELL_SIZE = 50
SUDOKU_GRID_SIZE = 9

# 俄罗斯方块设置
TETRIS_BLOCK_SIZE = 30
TETRIS_WIDTH = 10
TETRIS_HEIGHT = 20

# 数据库路径
if getattr(sys, 'frozen', False):
    DB_PATH = os.path.join(os.path.dirname(sys.executable), 'game_data.db')
else:
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'game_data.db')