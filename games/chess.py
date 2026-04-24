"""
国际象棋游戏模块
"""
import pygame
import os
import sys
from config import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, get_font
from ui import draw_gradient_background
from lang import get_text
from db import db

# 象棋配置
CELL_SIZE = 50
BOARD_OFFSET_X = 150
BOARD_OFFSET_Y = 120
BOARD_SIZE = 8

def get_icons_dir():
    """获取图标目录，兼容 PyInstaller 打包"""
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), 'icons', 'chess')
    else:
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons', 'chess')

# 图标文件夹
ICONS_DIR = get_icons_dir()

# 图标文件映射
ICON_FILES = {
    'K': ('w_king.png', 'b_king.png'),
    'Q': ('w_queen.png', 'b_queen.png'),
    'R': ('w_rook.png', 'b_rook.png'),
    'B': ('w_bishop.png', 'b_bishop.png'),
    'N': ('w_knight.png', 'b_knight.png'),
    'P': ('w_pawn.png', 'b_pawn.png'),
}

# 加载图标
def load_chess_icons():
    """加载棋子图标"""
    icons = {}
    icons_dir = get_icons_dir()
    for piece_type, (white_file, black_file) in ICON_FILES.items():
        white_path = os.path.join(icons_dir, white_file)
        black_path = os.path.join(icons_dir, black_file)
        
        if os.path.exists(white_path):
            try:
                icons[f'{piece_type}_w'] = pygame.image.load(white_path)
                icons[f'{piece_type}_w'] = pygame.transform.smoothscale(icons[f'{piece_type}_w'], (CELL_SIZE - 8, CELL_SIZE - 8))
            except:
                icons[f'{piece_type}_w'] = None
        else:
            icons[f'{piece_type}_w'] = None
            
        if os.path.exists(black_path):
            try:
                icons[f'{piece_type}_b'] = pygame.image.load(black_path)
                icons[f'{piece_type}_b'] = pygame.transform.smoothscale(icons[f'{piece_type}_b'], (CELL_SIZE - 8, CELL_SIZE - 8))
            except:
                icons[f'{piece_type}_b'] = None
        else:
            icons[f'{piece_type}_b'] = None
    
    return icons

CHESS_ICONS = load_chess_icons()
HAS_CUSTOM_ICONS = any(CHESS_ICONS.values())

# 棋子价值（用于AI评估）
PIECE_VALUES = {
    'P': 10, 'N': 30, 'B': 30, 'R': 50, 'Q': 90, 'K': 900,
    'p': 10, 'n': 30, 'b': 30, 'r': 50, 'q': 90, 'k': 900,
}

# 玩家颜色
PLAYER_WHITE = (240, 240, 240)
PLAYER_BLACK = (50, 50, 50)

# 棋子标识
PIECES = {
    'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',  # 白方
    'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟',  # 黑方
}

# 初始棋盘 (使用FEN记号法简化版)
INITIAL_BOARD = [
    ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
    ['', '', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
]


class InternationalChess:
    """国际象棋游戏类"""
    
    def __init__(self, screen):
        self.screen = screen
        self.offset_x = BOARD_OFFSET_X
        self.offset_y = BOARD_OFFSET_Y
        self.cell_size = CELL_SIZE
        self.board_size = BOARD_SIZE
        self.ai_move_timer = 0
        self.ai_move_delay = 500
        self.reset()
        
    def reset(self, keep_ai=False):
        """初始化游戏"""
        old_ai = self.ai_enabled if keep_ai else True  # 默认开启AI
        self.board = [row[:] for row in INITIAL_BOARD]
        
        self.current_player = True  # True=白方, False=黑方
        self.selected = None
        self.game_over = False
        self.winner = None
        self.paused = False
        self.show_rankings = False
        self.possible_moves = []
        self.captured_pieces = {'white': [], 'black': []}
        self.move_count = 0
        self.ai_enabled = old_ai
        self.ai_thinking = False
        self.ai_move_timer = 0
        self.ai_move_delay = 500  # AI移动延迟（毫秒）
    
    def enable_ai(self, enable=True):
        """开启/关闭AI"""
        self.ai_enabled = enable
    
    def make_ai_move(self):
        """AI下一两步"""
        if not self.ai_enabled or self.current_player or self.game_over or self.paused:
            return
        
        self.ai_thinking = True
        
        # 获取黑方所有合法移动
        moves = self.get_all_moves(False)
        if not moves:
            self.ai_thinking = False
            return
        
        # 简单AI：评估每一步，选择最好的一步
        best_move = None
        best_score = -99999
        
        for move in moves:
            from_row, from_col, to_row, to_col = move
            score = self.evaluate_move(from_row, from_col, to_row, to_col, False)
            if score > best_score:
                best_score = score
                best_move = move
        
        if best_move:
            from_row, from_col, to_row, to_col = best_move
            self.move_piece(from_row, from_col, to_row, to_col)
        
        self.ai_thinking = False
    
    def get_all_moves(self, player):
        """获取玩家所有合法移动"""
        moves = []
        for r in range(self.board_size):
            for c in range(self.board_size):
                piece = self.board[r][c]
                if piece and self.get_piece_player(piece) == player:
                    for tr in range(self.board_size):
                        for tc in range(self.board_size):
                            if self.can_move(r, c, tr, tc):
                                moves.append((r, c, tr, tc))
        return moves
    
    def evaluate_move(self, from_row, from_col, to_row, to_col, player):
        """评估一步移动的价值"""
        # 复制棋盘进行模拟
        old_piece = self.board[to_row][to_col]
        piece = self.board[from_row][from_col]
        
        # 执行移动
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = ''
        
        # 评估位置
        score = 0
        
        # 1. 吃掉对方子的价值
        if old_piece:
            score += PIECE_VALUES.get(old_piece, 0)
        
        # 2. 位置奖励（靠近中心更好）
        center_bonus = 0
        if piece.upper() == 'P':  # 兵推进奖励
            if not player:  # 黑方推进
                center_bonus = to_row * 2
            else:  # 白方推进
                center_bonus = (7 - to_row) * 2
        score += center_bonus
        
        # 3. 保护王安全
        if not self.is_in_check(player):
            score += 5
        
        # 还原棋盘
        self.board[from_row][from_col] = piece
        self.board[to_row][to_col] = old_piece
        
        return score
    
    def evaluate_board(self, player):
        """评估整个棋盘"""
        score = 0
        for r in range(self.board_size):
            for c in range(self.board_size):
                piece = self.board[r][c]
                if piece:
                    value = PIECE_VALUES.get(piece, 0)
                    if self.is_white_piece(piece):
                        score += value
                    else:
                        score -= value
        return score
    
    def is_white_piece(self, piece):
        return piece and piece.isupper()
    
    def is_black_piece(self, piece):
        return piece and piece.islower()
    
    def get_piece_player(self, piece):
        if not piece:
            return None
        return self.is_white_piece(piece)
    
    def is_valid_pos(self, row, col):
        return 0 <= row < self.board_size and 0 <= col < self.board_size
    
    def can_move(self, from_row, from_col, to_row, to_col):
        """检查移动是否合法"""
        piece = self.board[from_row][from_col]
        if not piece:
            return False
        
        target = self.board[to_row][to_col]
        target_player = self.get_piece_player(target)
        current_player = self.get_piece_player(piece)
        
        if target_player == current_player:
            return False
        
        row_diff = to_row - from_row
        col_diff = to_col - from_col
        abs_row = abs(row_diff)
        abs_col = abs(col_diff)
        piece_type = piece.upper()
        
        # 王：横、竖、斜走一格
        if piece_type == 'K':
            return abs_row <= 1 and abs_col <= 1
        
        # 后：横、竖、斜任意格
        if piece_type == 'Q':
            if row_diff != 0 and col_diff != 0 and abs_row != abs_col:
                return False
            return self._path_clear(from_row, from_col, to_row, to_col)
        
        # 车：横、竖任意格
        if piece_type == 'R':
            if row_diff != 0 and col_diff != 0:
                return False
            return self._path_clear(from_row, from_col, to_row, to_col)
        
        # 象：斜任意格
        if piece_type == 'B':
            if abs_row != abs_col:
                return False
            return self._path_clear(from_row, from_col, to_row, to_col)
        
        # 马：日字形
        if piece_type == 'N':
            return (abs_row == 2 and abs_col == 1) or (abs_row == 1 and abs_col == 2)
        
        # 兵：首步可走2格，平时走1格，吃子斜走1格
        if piece_type == 'P':
            direction = -1 if current_player else 1  # 白方向上，黑方向下
            start_row = 6 if current_player else 1
            
            # 吃子移动
            if target:
                return row_diff == direction and abs_col == 1
            
            # 普通移动
            if from_row != start_row:
                return row_diff == direction and col_diff == 0
            
            # 首步可走2格
            return (row_diff == direction or row_diff == 2 * direction) and col_diff == 0
        
        return False
    
    def _path_clear(self, from_row, from_col, to_row, to_col):
        """检查路径上是否有子"""
        if from_row == to_row:
            step = 1 if to_col > from_col else -1
            for c in range(from_col + step, to_col, step):
                if self.board[from_row][c]:
                    return False
        elif from_col == to_col:
            step = 1 if to_row > from_row else -1
            for r in range(from_row + step, to_row, step):
                if self.board[r][from_col]:
                    return False
        else:  # 斜线
            row_step = 1 if to_row > from_row else -1
            col_step = 1 if to_col > from_col else -1
            r, c = from_row + row_step, from_col + col_step
            while (r, c) != (to_row, to_col):
                if self.board[r][c]:
                    return False
                r += row_step
                c += col_step
        return True
    
    def is_in_check(self, player):
        """检查是否在将军"""
        # 找王的位置
        king = 'K' if player else 'k'
        king_pos = None
        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.board[r][c] == king:
                    king_pos = (r, c)
                    break
            if king_pos:
                break
        
        if not king_pos:
            return True
        
        # 检查是否被攻击
        opponent = not player
        for r in range(self.board_size):
            for c in range(self.board_size):
                piece = self.board[r][c]
                if piece and self.get_piece_player(piece) == opponent:
                    if self._can_attack(r, c, king_pos[0], king_pos[1]):
                        return True
        return False
    
    def _can_attack(self, from_row, from_col, to_row, to_col):
        """检查是否能够攻击目标位置"""
        piece = self.board[from_row][from_col]
        if not piece:
            return False
        
        piece_type = piece.upper()
        row_diff = to_row - from_row
        col_diff = to_col - from_col
        abs_row = abs(row_diff)
        abs_col = abs(col_diff)
        
        if piece_type == 'K':
            return abs_row <= 1 and abs_col <= 1
        if piece_type == 'Q':
            return (row_diff == 0 or col_diff == 0 or abs_row == abs_col) and self._path_clear(from_row, from_col, to_row, to_col)
        if piece_type == 'R':
            return (row_diff == 0 or col_diff == 0) and self._path_clear(from_row, from_col, to_row, to_col)
        if piece_type == 'B':
            return abs_row == abs_col and self._path_clear(from_row, from_col, to_row, to_col)
        if piece_type == 'N':
            return (abs_row == 2 and abs_col == 1) or (abs_row == 1 and abs_col == 2)
        if piece_type == 'P':
            direction = -1 if self.is_white_piece(piece) else 1
            return row_diff == direction and abs_col == 1
        
        return False
    
    def move_piece(self, from_row, from_col, to_row, to_col):
        """移动棋子"""
        piece = self.board[from_row][from_col]
        target = self.board[to_row][to_col]
        
        # 记录被吃的子
        if target:
            player = 'white' if self.is_black_piece(target) else 'black'
            self.captured_pieces[player].append(target)
        
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = ''
        self.move_count += 1
        
        # 兵升变（简化为自动升后）
        piece_type = piece.upper()
        if piece_type == 'P':
            if (self.current_player and to_row == 0) or (not self.current_player and to_row == 7):
                self.board[to_row][to_col] = 'Q' if self.current_player else 'q'
        
        self.current_player = not self.current_player
        self.selected = None
        self.possible_moves = []
        
        # 检查是否胜利
        self.check_win()
    
    def update(self):
        """更新游戏状态"""
        # AI移动（带延迟）
        if self.ai_enabled and self.current_player == False and not self.game_over and not self.paused:
            self.ai_move_timer += 16  # 约16ms一帧
            if self.ai_move_timer >= self.ai_move_delay:
                self.ai_move_timer = 0
                # 延迟后执行AI移动
                moves = self.get_all_moves(False)
                if moves:
                    best_move = None
                    best_score = -99999
                    for move in moves:
                        from_r, from_c, to_r, to_c = move
                        score = self.evaluate_move(from_r, from_c, to_r, to_c, False)
                        if score > best_score:
                            best_score = score
                            best_move = move
                    if best_move:
                        from_r, from_c, to_r, to_c = best_move
                        self.move_piece(from_r, from_c, to_r, to_c)
    
    def check_win(self):
        """检查是否胜利"""
        # 检查王是否被吃
        has_white_king = any('K' in row for row in self.board)
        has_black_king = any('k' in row for row in self.board)
        
        if not has_white_king:
            self.game_over = True
            self.winner = '黑方'
        elif not has_black_king:
            self.game_over = True
            self.winner = '白方'
    
    def select_piece(self, row, col):
        """选中棋子"""
        piece = self.board[row][col]
        if not piece:
            self.selected = None
            self.possible_moves = []
            return
        
        piece_player = self.get_piece_player(piece)
        if piece_player != self.current_player:
            return
        
        self.selected = (row, col)
        
        # 计算合法移动
        self.possible_moves = []
        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.can_move(row, col, r, c):
                    self.possible_moves.append((r, c))
    
    def handle_click(self, pos):
        """处理点击"""
        x, y = pos
        
        # 排行榜窗口
        if getattr(self, 'show_rankings', False):
            win_w, win_h = 500, 450
            win_x = (SCREEN_WIDTH - win_w) // 2
            win_y = (SCREEN_HEIGHT - win_h) // 2
            close_y = win_y + win_h - 50
            if win_x + win_w//2 - 50 <= x <= win_x + win_w//2 + 50 and close_y <= y <= close_y + 35:
                self.show_rankings = False
            return
        
        # 侧边栏按钮处理
        if x >= 580:
            # 暂停按钮
            if 600 <= x <= 680 and 70 <= y <= 105:
                self.paused = not self.paused
                return
            
# 新游戏按钮
            if 600 <= x <= 680 and 115 <= y <= 150:
                self.reset(keep_ai=True)
                return
            
            # AI模式复选框
            if 605 <= x <= 705 and 162 <= y <= 182:
                self.ai_enabled = not self.ai_enabled
                return
            
            # 最快通关按钮
            if 600 <= x <= 765 and 520 <= y <= 555:
                self.show_rankings = not self.show_rankings
                return
            
            return
        
        # 棋盘区域
        board_w = self.board_size * self.cell_size
        board_h = self.board_size * self.cell_size
        
        if self.offset_x <= x <= self.offset_x + board_w and \
           self.offset_y <= y <= self.offset_y + board_h:
            col = (x - self.offset_x) // self.cell_size
            row = (y - self.offset_y) // self.cell_size
            
            if 0 <= row < self.board_size and 0 <= col < self.board_size:
                if not self.game_over and not self.paused:
                    self._handle_click_cell(row, col)
    
    def _handle_click_cell(self, row, col):
        """处理棋盘格点击"""
        if self.selected:
            if (row, col) in self.possible_moves:
                from_row, from_col = self.selected
                self.move_piece(from_row, from_col, row, col)
                return
            
            if self.get_piece_player(self.board[row][col]) == self.current_player:
                self.select_piece(row, col)
                return
            
            self.selected = None
            self.possible_moves = []
        else:
            self.select_piece(row, col)
    
    def handle_key(self, key):
        if getattr(self, 'show_rankings', False):
            if key == pygame.K_ESCAPE:
                self.show_rankings = False
            return
        
        if key == pygame.K_p:
            self.paused = not self.paused
    
    def draw(self):
        draw_gradient_background(self.screen)
        self.draw_game_area()
        self.draw_sidebar()
        
        if self.show_rankings:
            self.draw_rankings_window()
    
    def draw_game_area(self):
        # 标题
        font = get_font(32)
        text = font.render("国际象棋", True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(self.offset_x + self.board_size * self.cell_size // 2, 50))
        self.screen.blit(text, text_rect)
        
        # 当前玩家
        player_text = "白方回合" if self.current_player else "黑方回合"
        player_color = PLAYER_WHITE if self.current_player else PLAYER_BLACK
        font = get_font(16)
        text = font.render(player_text, True, player_color)
        text_rect = text.get_rect(center=(self.offset_x + self.board_size * self.cell_size // 2, 80))
        self.screen.blit(text, text_rect)
        
        # 绘制棋盘
        for r in range(self.board_size):
            for c in range(self.board_size):
                x = self.offset_x + c * self.cell_size
                y = self.offset_y + r * self.cell_size
                
                # 棋格颜色
                is_light = (r + c) % 2 == 0
                color = (240, 230, 200) if is_light else (100, 80, 50)
                pygame.draw.rect(self.screen, color, (x, y, self.cell_size, self.cell_size))
                pygame.draw.rect(self.screen, (60, 40, 20), (x, y, self.cell_size, self.cell_size), 1)
        
        # 绘制行列标签
        font = get_font(14)
        cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        
        # 顶列标签（A-H）
        for c in range(self.board_size):
            x = self.offset_x + c * self.cell_size + self.cell_size // 2
            y = self.offset_y - 15
            text = font.render(cols[c], True, COLORS['TEXT_LIGHT'])
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)
        
        # 右侧行标签（8-1）
        for r in range(self.board_size):
            x = self.offset_x + self.board_size * self.cell_size + 15
            y = self.offset_y + r * self.cell_size + self.cell_size // 2 + 5
            text = font.render(str(8 - r), True, COLORS['TEXT_LIGHT'])
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)
        
        # 底列标签（A-H）
        for c in range(self.board_size):
            x = self.offset_x + c * self.cell_size + self.cell_size // 2
            y = self.offset_y + self.board_size * self.cell_size + 30
            text = font.render(cols[c], True, COLORS['TEXT_LIGHT'])
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)
        
        # 左边行标签（1-8）
        for r in range(self.board_size):
            x = self.offset_x - 15
            y = self.offset_y + r * self.cell_size + self.cell_size // 2 + 5
            text = font.render(str(8 - r), True, COLORS['TEXT_LIGHT'])
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)
        
        # 棋子图例（棋盘下方）
        legend_y = self.offset_y + self.board_size * self.cell_size + 70
        legend_font = get_font(12)
        pieces_info = [
            ('K', '王', 0), ('Q', '后', 1), ('R', '车', 2),
            ('B', '象', 3), ('N', '马', 4), ('P', '兵', 5),
        ]
        
        for piece, name, idx in pieces_info:
            x = self.offset_x + idx * 65 + 30
            icon_size = 18
            # 绘制白色背景圆
            pygame.draw.circle(self.screen, (255, 255, 255), (x, legend_y), 12)
            pygame.draw.circle(self.screen, COLORS['TEXT_DARK'], (x, legend_y), 12, 1)
            
            # 尝试使用自定义图标
            icon_key = f'{piece}_w'
            icon = CHESS_ICONS.get(icon_key)
            
            if icon and HAS_CUSTOM_ICONS:
                # 缩放图标
                small_icon = pygame.transform.smoothscale(icon, (icon_size, icon_size))
                icon_rect = small_icon.get_rect(center=(x, legend_y))
                self.screen.blit(small_icon, icon_rect)
            else:
                # 绘制字母
                font_legend = get_font(10)
                text = font_legend.render(piece, True, PLAYER_BLACK)
                text_rect = text.get_rect(center=(x, legend_y))
                self.screen.blit(text, text_rect)
            
            # 绘制名称
            font_name = get_font(11)
            text = font_name.render(name, True, COLORS['TEXT_LIGHT'])
            text_rect = text.get_rect(center=(x, legend_y + 18))
            self.screen.blit(text, text_rect)
        
        # 绘制合法移动标记
        for (r, c) in self.possible_moves:
            cx = self.offset_x + c * self.cell_size + self.cell_size // 2
            cy = self.offset_y + r * self.cell_size + self.cell_size // 2
            pygame.draw.circle(self.screen, COLORS['GREEN'], (cx, cy), 8, 2)
        
        # 绘制选中标记
        if self.selected:
            r, c = self.selected
            x = self.offset_x + c * self.cell_size
            y = self.offset_y + r * self.cell_size
            pygame.draw.rect(self.screen, COLORS['YELLOW'], (x, y, self.cell_size, self.cell_size), 3)
        
        # 绘制棋子
        for r in range(self.board_size):
            for c in range(self.board_size):
                piece = self.board[r][c]
                if piece:
                    self.draw_piece(r, c, piece)
        
        # 暂停遮罩（不透明黑色）
        if self.paused:
            board_w = self.board_size * self.cell_size
            board_h = self.board_size * self.cell_size
            overlay = pygame.Surface((board_w, board_h))
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (self.offset_x, self.offset_y))
            
            font = get_font(32)
            text = font.render("暂停", True, COLORS['GREEN_NEON'])
            text_rect = text.get_rect(center=(self.offset_x + board_w // 2, self.offset_y + board_h // 2))
            self.screen.blit(text, text_rect)
        
        # 游戏结束遮罩
        if self.game_over:
            self._draw_overlay(f"{self.winner}获胜!")
    
    def draw_piece(self, row, col, piece):
        x = self.offset_x + col * self.cell_size + self.cell_size // 2
        y = self.offset_y + row * self.cell_size + self.cell_size // 2
        radius = self.cell_size // 2 - 3
        
        is_white = piece.isupper()
        piece_type = piece.upper()
        
        # 尝试使用自定义图标
        icon_key = f'{piece_type}_w' if is_white else f'{piece_type}_b'
        icon = CHESS_ICONS.get(icon_key)
        
        if icon and HAS_CUSTOM_ICONS:
            # 绘制自定义图标（居中）
            icon_rect = icon.get_rect(center=(x, y))
            self.screen.blit(icon, icon_rect)
        else:
            # 使用默认绘制方法
            piece_color = PLAYER_WHITE if is_white else PLAYER_BLACK
            outline_color = COLORS['TEXT_DARK']
            
            # 绘制棋子底座
            pygame.draw.circle(self.screen, piece_color, (x, y), radius)
            pygame.draw.circle(self.screen, outline_color, (x, y), radius, 2)
            
            if piece_type == 'K':  # 王 - 皇冠
                self._draw_king(x, y, radius - 4, outline_color if is_white else piece_color)
            elif piece_type == 'Q':  # 后 - 皇冠形
                self._draw_queen(x, y, radius - 4, outline_color if is_white else piece_color)
            elif piece_type == 'R':  # 车 - 城堡
                self._draw_rook(x, y, radius - 4, outline_color if is_white else piece_color)
            elif piece_type == 'B':  # 象 - 主教帽
                self._draw_bishop(x, y, radius - 4, outline_color if is_white else piece_color)
            elif piece_type == 'N':  # 马 - 马头
                self._draw_knight(x, y, radius - 4, outline_color if is_white else piece_color)
            elif piece_type == 'P':  # 兵 - 简单圆形
                self._draw_pawn(x, y, radius - 4, outline_color if is_white else piece_color)
    
    def _draw_king(self, cx, cy, r, color):
        """绘制王棋子在"""
        # 皇冠形状
        points = [
            (cx - r, cy + r//2),
            (cx - r, cy - r//3),
            (cx - r//2, cy - r//2),
            (cx, cy - r),
            (cx + r//2, cy - r//2),
            (cx + r, cy - r//3),
            (cx + r, cy + r//2),
        ]
        pygame.draw.polygon(self.screen, color, points, 2)
        # 十字
        pygame.draw.line(self.screen, color, (cx, cy - r//2), (cx, cy + r//2), 2)
        pygame.draw.line(self.screen, color, (cx - r//2, cy), (cx + r//2, cy), 2)
    
    def _draw_queen(self, cx, cy, r, color):
        """绘制后棋子"""
        # 锯齿皇冠
        points = [
            (cx - r, cy + r//2),
            (cx - r, cy - r//3),
            (cx - r*0.7, cy - r//2),
            (cx - r*0.35, cy - r*0.8),
            (cx, cy - r//2),
            (cx + r*0.35, cy - r*0.8),
            (cx + r*0.7, cy - r//2),
            (cx + r, cy - r//3),
            (cx + r, cy + r//2),
        ]
        pygame.draw.polygon(self.screen, color, points, 2)
    
    def _draw_rook(self, cx, cy, r, color):
        """行车棋"""
        # 城堡塔楼
        rect = pygame.Rect(cx - r + 2, cy - r, r * 2 - 4, r * 1.5)
        pygame.draw.rect(self.screen, color, rect, 2)
        # 齿
        for i in range(3):
            x = cx - r + 2 + i * (r - 2)
            pygame.draw.rect(self.screen, color, (x, cy - r - 3, r//3, 4), 2)
    
    def _draw_bishop(self, cx, cy, r, color):
        """绘制象棋"""
        # 主教帽形状
        points = [
            (cx - r, cy + r//2),
            (cx - r//2, cy),
            (cx - r//2, cy - r//2),
            (cx, cy - r),
            (cx + r//2, cy - r//2),
            (cx + r//2, cy),
            (cx + r, cy + r//2),
        ]
        pygame.draw.polygon(self.screen, color, points, 2)
        # 圆点
        pygame.draw.circle(self.screen, color, (cx, cy), 3, 1)
    
    def _draw_knight(self, cx, cy, r, color):
        """绘制马棋子"""
        # 马头形状
        points = [
            (cx - r + 2, cy + r//2),
            (cx - r + 2, cy - r//2),
            (cx - r//3, cy - r),
            (cx + r//2, cy - r//2),
            (cx + r, cy),
            (cx + r - 2, cy + r//2),
        ]
        pygame.draw.polygon(self.screen, color, points, 2)
        # 眼睛
        pygame.draw.circle(self.screen, color, (cx - r//4, cy - r//4), 2, 1)
    
    def _draw_pawn(self, cx, cy, r, color):
        """绘制兵棋子"""
        # 简单圆点
        pygame.draw.circle(self.screen, color, (cx, cy), r//2, 2)
        # 向下标记
        pygame.draw.line(self.screen, color, (cx, cy + r//3), (cx, cy + r - 2), 2)
    
    def _draw_overlay(self, msg):
        board_w = self.board_size * self.cell_size
        board_h = self.board_size * self.cell_size
        overlay = pygame.Surface((board_w, board_h))
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (self.offset_x, self.offset_y))
        
        font = get_font(32)
        text = font.render(msg, True, COLORS['GREEN_NEON'])
        text_rect = text.get_rect(center=(self.offset_x + board_w // 2, self.offset_y + board_h // 2))
        self.screen.blit(text, text_rect)
    
    def draw_sidebar(self):
        pygame.draw.rect(self.screen, COLORS['PANEL'], (580, 60, 200, 540), border_radius=10)
        
        font = get_font(14)
        
        # 暂停按钮
        btn_color = COLORS['ORANGE'] if self.paused else COLORS['GREEN']
        pygame.draw.rect(self.screen, btn_color, (600, 70, 80, 35), border_radius=5)
        text = font.render(get_text('pause') if not self.paused else get_text('resume'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(640, 87))
        self.screen.blit(text, text_rect)
        
        # 新游戏按钮
        pygame.draw.rect(self.screen, COLORS['PURPLE'], (600, 115, 80, 35), border_radius=5)
        text = font.render(get_text('new_game'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(640, 132))
        self.screen.blit(text, text_rect)
        
        # AI模式复选框
        checkbox_x, checkbox_y, checkbox_size = 605, 162, 20
        # 复选框背景
        pygame.draw.rect(self.screen, COLORS['PANEL'], (checkbox_x - 3, checkbox_y - 3, checkbox_size + 80, checkbox_size + 10), border_radius=3)
        # 复选框
        pygame.draw.rect(self.screen, COLORS['TEXT_LIGHT'], (checkbox_x, checkbox_y, checkbox_size, checkbox_size), 2, border_radius=3)
        if self.ai_enabled:
            pygame.draw.rect(self.screen, COLORS['GREEN'], (checkbox_x + 4, checkbox_y + 4, checkbox_size - 8, checkbox_size - 8), border_radius=2)
        font = get_font(14)
        text = font.render(get_text('chess_ai_mode'), True, COLORS['TEXT_LIGHT'])
        self.screen.blit(text, (checkbox_x + checkbox_size + 8, checkbox_y + 2))
        
        # 当前玩家
        font = get_font(16)
        player_text = get_text('white') if self.current_player else get_text('black')
        text = font.render(f"{get_text('current_player')}: {player_text}", True, COLORS['TEXT_LIGHT'])
        self.screen.blit(text, (600, 200))
        
        # 步数
        font = get_font(14)
        text = font.render(f"{get_text('moves')}: {self.move_count}", True, COLORS['TEXT_LIGHT'])
        self.screen.blit(text, (600, 225))
        
        # 被吃的子
        y = 260
        font = get_font(12)
        
        pygame.draw.rect(self.screen, COLORS['TEXT_DARK'], (590, y, 180, 25), border_radius=3)
        capt_white = f"{get_text('white')}{get_text('captured')}:"
        text = font.render(capt_white, True, COLORS['TEXT_LIGHT'])
        self.screen.blit(text, (595, y + 5))
        y += 30
        
        white_captured = ''.join(self.captured_pieces['white'])
        if white_captured:
            text = font.render(white_captured, True, COLORS['TEXT_LIGHT'])
            self.screen.blit(text, (595, y))
        else:
            text = font.render(get_text('none'), True, COLORS['TEXT_LIGHT'])
            self.screen.blit(text, (595, y))
        y += 25
        
        pygame.draw.rect(self.screen, COLORS['TEXT_DARK'], (590, y, 180, 25), border_radius=3)
        capt_black = f"{get_text('black')}{get_text('captured')}:"
        text = font.render(capt_black, True, COLORS['TEXT_LIGHT'])
        self.screen.blit(text, (595, y + 5))
        y += 30
        
        black_captured = ''.join(self.captured_pieces['black'])
        if black_captured:
            text = font.render(black_captured, True, COLORS['TEXT_LIGHT'])
            self.screen.blit(text, (595, y))
        else:
            text = font.render(get_text('none'), True, COLORS['TEXT_LIGHT'])
            self.screen.blit(text, (595, y))
        
        # 操作说明
        font = get_font(12)
        y = 450
        help_texts = [
            get_text('controls') + ':',
            get_text('click_piece'),
            get_text('click_destination'),
            f"{get_text('white')}{get_text('first')}",
        ]
        for txt in help_texts:
            text = font.render(txt, True, COLORS['TEXT_LIGHT'])
            self.screen.blit(text, (600, y))
            y += 18
        
        # 最快通关按钮
        pygame.draw.rect(self.screen, COLORS['CYAN'], (600, 520, 165, 35), border_radius=5)
        font = get_font(14)
        text = font.render(get_text('top_scores'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(682, 537))
        self.screen.blit(text, text_rect)
    
    def draw_rankings_window(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        win_w, win_h = 500, 450
        win_x = (SCREEN_WIDTH - win_w) // 2
        win_y = (SCREEN_HEIGHT - win_h) // 2
        pygame.draw.rect(self.screen, COLORS['PANEL'], (win_x, win_y, win_w, win_h), border_radius=15)
        pygame.draw.rect(self.screen, COLORS['BLUE'], (win_x, win_y, win_w, win_h), 2, border_radius=15)
        
        font = get_font(28)
        text = font.render(get_text('top_scores'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, win_y + 30))
        self.screen.blit(text, text_rect)
        
        close_y = win_y + win_h - 50
        pygame.draw.rect(self.screen, COLORS['RED'], (win_x + win_w // 2 - 50, close_y, 100, 35), border_radius=5)
        font = get_font(16)
        text = font.render(get_text('back'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(win_x + win_w // 2, close_y + 17))
        self.screen.blit(text, text_rect)
        
        list_y = win_y + 70
        scores = db.get_top_scores('intl_chess', 50)
        font = get_font(14)
        
        if scores:
            for i, score in enumerate(scores[:15]):
                diff = score.get('difficulty', '')
                rank_text = f"{i+1}. {diff}"
                color = COLORS['GREEN'] if i < 3 else COLORS['TEXT_LIGHT']
                text = font.render(rank_text, True, color)
                self.screen.blit(text, (win_x + 40, list_y + i * 22))
        else:
            text = font.render(get_text('no_records'), True, COLORS['TEXT_GRAY'])
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, list_y + 50))
            self.screen.blit(text, text_rect)


def create_game(screen):
    return InternationalChess(screen)