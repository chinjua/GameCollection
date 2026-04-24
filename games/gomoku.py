"""
五子棋游戏模块
"""
import pygame
from config import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, get_font
from ui import draw_gradient_background, draw_decorative_circle
from lang import get_text
from db import db

# 五子棋配置
GRID_COUNT = 14  # 14x14棋盘
CELL_SIZE = 30  # 格子大小
BOARD_PADDING = 30  # 棋盘边缘padding

# 玩家颜色
PLAYER_BLACK = 1
PLAYER_WHITE = 2


class Gomoku:
    """五子棋游戏类"""
    
    def __init__(self, screen):
        self.screen = screen
        # 计算棋盘位置（右侧留出200px给侧边栏，间距10px）
        board_width = GRID_COUNT * CELL_SIZE
        board_height = GRID_COUNT * CELL_SIZE
        # 侧边栏x=580, 间距10, 棋盘右侧=570
        # 棋盘宽度=450, offset_x=570-450=120
        self.offset_x = 110
        self.offset_y = 90  # 向下移动10像素
        self.reset()
        
    def reset(self, keep_ai=False):
        """初始化游戏"""
        old_ai = getattr(self, 'ai_enabled', True) if keep_ai else True
        # 15x15棋盘，0=空，1=黑，2=白
        self.board = [[0 for _ in range(GRID_COUNT)] for _ in range(GRID_COUNT)]
        self.current_player = PLAYER_BLACK  # 当前移动的玩家
        self.player_color = PLAYER_BLACK  # 玩家选择的颜色（黑或白）
        self.computer_color = PLAYER_WHITE  # 电脑颜色
        self.winner = None
        self.game_over = False
        self.paused = False
        self.score = 0
        self.start_time = None
        self.elapsed_time = 0
        self.show_rankings = False
        self.last_move_time = pygame.time.get_ticks()
        self.ai_enabled = old_ai
        
        # 如果电脑是黑子，电脑先手
        if self.ai_enabled and self.computer_color == PLAYER_BLACK and not self.game_over:
            self.computer_move()
        
    def handle_key(self, key):
        """处理按键"""
        # 排行榜窗口打开时按ESC关闭
        if getattr(self, 'show_rankings', False):
            if key == pygame.K_ESCAPE:
                self.show_rankings = False
            return
        
        # P键暂停
        if key == pygame.K_p:
            self.paused = not self.paused
            return
            
    def handle_click(self, pos, button=1):
        """处理点击"""
        # 如果排行榜窗口打开，先处理关闭按钮
        if getattr(self, 'show_rankings', False):
            win_width = 500
            win_height = 450
            win_x = (SCREEN_WIDTH - win_width) // 2
            win_y = (SCREEN_HEIGHT - win_height) // 2
            close_y = win_y + win_height - 50
            # 关闭按钮
            if win_x + win_width // 2 - 50 <= pos[0] <= win_x + win_width // 2 + 50 and \
               close_y <= pos[1] <= close_y + 35:
                self.show_rankings = False
            return
        
        # 侧边栏区域
        if pos[0] >= 580:
            # 暂停按钮 (600, 80, 80, 38)
            if 600 <= pos[0] <= 680 and 80 <= pos[1] <= 118:
                self.paused = not self.paused
                return
            
            # 新游戏按钮 (600, 125, 80, 38)
            if 600 <= pos[0] <= 680 and 125 <= pos[1] <= 163:
                self.reset()
                return
            
            # 切换玩家按钮 (600, 170, 165, 38)
            if 600 <= pos[0] <= 765 and 170 <= pos[1] <= 208:
                # 切换玩家颜色
                if self.player_color == PLAYER_BLACK:
                    self.player_color = PLAYER_WHITE
                    self.computer_color = PLAYER_BLACK
                else:
                    self.player_color = PLAYER_BLACK
                    self.computer_color = PLAYER_WHITE
                self.reset()
                return
            
            # AI模式复选框 (605, 220, ~90, 20)
            if 605 <= pos[0] <= 695 and 220 <= pos[1] <= 240:
                self.ai_enabled = not self.ai_enabled
                self.reset(keep_ai=True)
                return
            
            # 最快通关按钮 (600, 520, 165, 35)
            if 600 <= pos[0] <= 765 and 520 <= pos[1] <= 555:
                self.show_rankings = True
                return
            
            return
        
        # 检查是否点击棋盘
        board_x = self.offset_x
        board_y = self.offset_y
        board_size = GRID_COUNT * CELL_SIZE
        
        if not (board_x <= pos[0] <= board_x + board_size and 
                board_y <= pos[1] <= board_y + board_size):
            return
        
        if self.game_over or self.paused:
            return
        
        # 计算点击位置相对于棋盘左上角的偏移
        x_offset = pos[0] - board_x
        y_offset = pos[1] - board_y
        
        # 计算最近的交叉点坐标
        # 交叉点位置 = 偏移 / CELL_SIZE 的四舍五入
        col = round(x_offset / CELL_SIZE)
        row = round(y_offset / CELL_SIZE)
        
        # 确保在有效范围内
        if 0 <= col < GRID_COUNT and 0 <= row < GRID_COUNT:
            # 检查该位置是否为空
            if self.board[row][col] == 0:
                # 如果AI未启用，玩家可以自由落子（黑子或白子）
                if not self.ai_enabled:
                    # 玩家自由落子，轮流下黑子和白子
                    self.board[row][col] = self.current_player
                    
                    # 首次落子开始计时
                    if self.start_time is None:
                        self.start_time = pygame.time.get_ticks()
                    
                    # 检查当前玩家是否获胜
                    if self.check_win(row, col, self.current_player):
                        self.winner = self.current_player
                        self.game_over = True
                        db.save_score('gomoku', 'Player', self.score + 1, 0, 'normal')
                        return
                    
                    # 切换到另一方
                    self.current_player = PLAYER_WHITE if self.current_player == PLAYER_BLACK else PLAYER_BLACK
                    return
                
                # AI模式时检查是否是玩家回合
                if self.current_player != self.player_color:
                    return
                
                # 玩家落子
                self.board[row][col] = self.player_color
                
                # 首次落子开始计时
                if self.start_time is None:
                    self.start_time = pygame.time.get_ticks()
                
                # 检查玩家是否获胜
                if self.check_win(row, col, self.player_color):
                    self.winner = self.player_color
                    self.game_over = True
                    # 保存成绩
                    db.save_score('gomoku', 'Player', self.score + 1, 0, 'normal')
                    return
                
                # 切换到电脑回合
                self.current_player = self.computer_color
                
                # 电脑落子
                self.computer_move()
    
    def check_win(self, row, col, player=None):
        """检查是否五子连珠"""
        if player is None:
            player = self.board[row][col]
        
        # 四个方向：水平、垂直、对角线、反对角线
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            count = 1
            
            # 正方向
            x, y = col + dx, row + dy
            while 0 <= x < GRID_COUNT and 0 <= y < GRID_COUNT and self.board[y][x] == player:
                count += 1
                x += dx
                y += dy
            
            # 反方向
            x, y = col - dx, row - dy
            while 0 <= x < GRID_COUNT and 0 <= y < GRID_COUNT and self.board[y][x] == player:
                count += 1
                x -= dx
                y -= dy
            
            if count >= 5:
                return True
        
        return False
    
    def computer_move(self):
        """电脑落子 - 改进的AI"""
        if self.game_over or self.paused or not self.ai_enabled:
            return
        
        # 找到空位
        empty_positions = []
        for row in range(GRID_COUNT):
            for col in range(GRID_COUNT):
                if self.board[row][col] == 0:
                    empty_positions.append((row, col))
        
        if not empty_positions:
            return
        
        # 检查是否已有棋子
        has_any_piece = any(self.board[r][c] != 0 for r in range(GRID_COUNT) for c in range(GRID_COUNT))
        
        # 如果是第一步，下在中心
        if not has_any_piece:
            center = GRID_COUNT // 2
            self.board[center][center] = self.computer_color
            self.current_player = self.player_color
            return
        
        # 评估每个空位的分数
        best_move = None
        best_score = -float('inf')
        
        for row, col in empty_positions:
            # 评估攻击分数（电脑）
            attack_score = self.evaluate_position(row, col, self.computer_color)
            # 评估防守分数（玩家）
            defense_score = self.evaluate_position(row, col, self.player_color)
            
            # 综合分数：攻击和防守都很重要
            score = max(attack_score, defense_score * 1.1)  # 稍微偏向防守
            
            if score > best_score:
                best_score = score
                best_move = (row, col)
        
        if best_move:
            row, col = best_move
            self.board[row][col] = self.computer_color
            
            # 检查电脑是否获胜
            if self.check_win(row, col, self.computer_color):
                self.winner = self.computer_color
                self.game_over = True
                return
            
            # 切换回玩家回合
            self.current_player = self.player_color
    
    def evaluate_position(self, row, col, player):
        """评估某个位置的分数"""
        total_score = 0
        
        # 四个方向
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            line = self.get_line(row, col, dx, dy, player)
            score = self.evaluate_line(line, player)
            total_score += score
        
        return total_score
    
    def get_line(self, row, col, dx, dy, player):
        """获取指定方向的连线（包含该位置前后各4个位置）"""
        line = []
        
        # 前面4个位置
        for i in range(4, 0, -1):
            r, c = row - i * dy, col - i * dx
            if 0 <= r < GRID_COUNT and 0 <= c < GRID_COUNT:
                line.append(self.board[r][c])
            else:
                line.append(-1)  # 边界
        
        # 当前位置
        line.append(player)
        
        # 后面4个位置
        for i in range(1, 5):
            r, c = row + i * dy, col + i * dx
            if 0 <= r < GRID_COUNT and 0 <= c < GRID_COUNT:
                line.append(self.board[r][c])
            else:
                line.append(-1)  # 边界
        
        return line
    
    def evaluate_line(self, line, player):
        """评估连线的分数"""
        opponent = PLAYER_WHITE if player == PLAYER_BLACK else PLAYER_BLACK
        
        # 统计连续棋子数
        consecutive = 0
        open_ends = 0  # 两端是否空
        
        # 找到连续的棋子
        i = 4  # 当前位置
        # 向左检查
        j = i - 1
        while j >= 0 and line[j] == player:
            consecutive += 1
            j -= 1
        # 检查左端
        if j >= 0 and line[j] == 0:
            open_ends += 1
        elif j >= 0 and line[j] == -1:
            pass  # 边界，不算open
        
        # 向右检查
        j = i + 1
        while j < 9 and line[j] == player:
            consecutive += 1
            j += 1
        # 检查右端
        if j < 9 and line[j] == 0:
            open_ends += 1
        elif j < 9 and line[j] == -1:
            pass  # 边界
        
        # 根据连子数和两端情况给分
        if consecutive >= 4:
            return 100000  # 活四或以上，必胜
        elif consecutive == 3:
            if open_ends == 2:
                return 10000  # 活三
            elif open_ends == 1:
                return 1000  # 冲四
        elif consecutive == 2:
            if open_ends == 2:
                return 100  # 活二
            elif open_ends == 1:
                return 10   # 眠二
        elif consecutive == 1:
            if open_ends == 2:
                return 5    # 活一
        
        return 0
    
    def update(self):
        """更新游戏"""
        if self.game_over or self.paused:
            return
            
        if self.start_time:
            current_time = pygame.time.get_ticks()
            self.elapsed_time = (current_time - self.start_time) // 1000
    
    def draw(self):
        """绘制游戏"""
        draw_gradient_background(self.screen)
        draw_decorative_circle(self.screen, 50, 550, 50, (0, 0, 0), 20)
        draw_decorative_circle(self.screen, SCREEN_WIDTH - 50, 50, 40, (200, 200, 200), 20)
        
        self.draw_game_area()
        self.draw_sidebar()
        
        # 排行榜窗口
        if getattr(self, 'show_rankings', False):
            self.draw_rankings_window()
    
    def draw_game_area(self):
        """绘制棋盘"""
        # 标题
        font = get_font(36)
        text = font.render(get_text('gomoku'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(self.offset_x + GRID_COUNT * CELL_SIZE // 2, 40))
        self.screen.blit(text, text_rect)
        
        # 绘制棋盘背景
        board_x = self.offset_x
        board_y = self.offset_y
        board_size = GRID_COUNT * CELL_SIZE
        
        # 棋盘背景
        board_rect = pygame.Rect(board_x, board_y, board_size, board_size)
        pygame.draw.rect(self.screen, (210, 170, 100), board_rect, border_radius=5)
        
        # 绘制网格线
        for i in range(GRID_COUNT):
            # 横线
            start_pos = (board_x, board_y + i * CELL_SIZE)
            end_pos = (board_x + board_size, board_y + i * CELL_SIZE)
            pygame.draw.line(self.screen, (0, 0, 0), start_pos, end_pos, 1)
            
            # 竖线
            start_pos = (board_x + i * CELL_SIZE, board_y)
            end_pos = (board_x + i * CELL_SIZE, board_y + board_size)
            pygame.draw.line(self.screen, (0, 0, 0), start_pos, end_pos, 1)
        
        # 绘制边框
        pygame.draw.rect(self.screen, (0, 0, 0), board_rect, 2, border_radius=5)
        
        # 绘制行列标签 - 14x14棋盘有15条线
        font = get_font(12)
        
        # 顶部列标签 A-O（15条竖线用字母）
        cols = 'ABCDEFGHIJKLMNO'
        
        for c in range(GRID_COUNT + 1):
            x = board_x + c * CELL_SIZE
            y = board_y - 15
            text = font.render(cols[c], True, COLORS['TEXT_LIGHT'])
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)
        
        # 底部列标签 A-O
        for c in range(GRID_COUNT + 1):
            x = board_x + c * CELL_SIZE
            y = board_y + board_size + 8
            text = font.render(cols[c], True, COLORS['TEXT_LIGHT'])
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)
        
        # 左侧行标签（1-15，表示横线编号）
        for r in range(GRID_COUNT + 1):
            x = board_x - 15
            y = board_y + r * CELL_SIZE
            text = font.render(str(r + 1), True, COLORS['TEXT_LIGHT'])
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)
        
        # 右侧行标签（1-15）
        for r in range(GRID_COUNT + 1):
            x = board_x + board_size + 10
            y = board_y + r * CELL_SIZE
            text = font.render(str(r + 1), True, COLORS['TEXT_LIGHT'])
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)
        
        # 绘制星位（天元和星）- H8,D12,L12,D4,L4
        star_points = [(7, 7), (3, 11), (11, 11), (3, 3), (11, 3)]
        for x, y in star_points:
            px = board_x + x * CELL_SIZE
            py = board_y + y * CELL_SIZE
            pygame.draw.circle(self.screen, (0, 0, 0), (px, py), 4)  # 较大黑点
        
        # 绘制棋子
        for row in range(GRID_COUNT):
            for col in range(GRID_COUNT):
                if self.board[row][col] != 0:
                    px = board_x + col * CELL_SIZE
                    py = board_y + row * CELL_SIZE
                    
                    # 棋子阴影
                    pygame.draw.circle(self.screen, (180, 180, 180), (px + 2, py + 2), CELL_SIZE // 2 - 2)
                    
                    if self.board[row][col] == PLAYER_BLACK:
                        pygame.draw.circle(self.screen, (0, 0, 0), (px, py), CELL_SIZE // 2 - 2)
                    else:
                        pygame.draw.circle(self.screen, (255, 255, 255), (px, py), CELL_SIZE // 2 - 2)
                        pygame.draw.circle(self.screen, (0, 0, 0), (px, py), CELL_SIZE // 2 - 2, 1)
        
        # 暂停遮罩 - 黑色不透明
        if self.paused:
            overlay = pygame.Surface((board_size, board_size))
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (board_x, board_y))
            font = get_font(36)
            text = font.render(get_text('pause'), True, COLORS['TEXT_LIGHT'])
            text_rect = text.get_rect(center=(board_x + board_size // 2,
                                            board_y + board_size // 2))
            self.screen.blit(text, text_rect)
        
        # 游戏结束
        if self.game_over:
            overlay = pygame.Surface((board_size, board_size))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (board_x, board_y))
            font = get_font(32)
            winner_text = f"{'黑子' if self.winner == PLAYER_BLACK else '白子'}获胜!"
            text = font.render(winner_text, True, COLORS['GREEN_NEON'])
            text_rect = text.get_rect(center=(board_x + board_size // 2,
                                            board_y + board_size // 2 - 20))
            self.screen.blit(text, text_rect)
    
    def draw_sidebar(self):
        """绘制侧边栏"""
        # 侧边栏背景
        pygame.draw.rect(self.screen, COLORS['PANEL'], (580, 80, 200, 500), border_radius=10)
        
        font = get_font(14)
        
        # 暂停按钮
        btn_color = COLORS['ORANGE'] if self.paused else COLORS['GREEN']
        pygame.draw.rect(self.screen, btn_color, (600, 80, 80, 38), border_radius=5)
        text = font.render(get_text('pause') if not self.paused else get_text('resume'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(640, 99))
        self.screen.blit(text, text_rect)
        
        # 新游戏按钮
        pygame.draw.rect(self.screen, COLORS['PURPLE'], (600, 125, 80, 38), border_radius=5)
        text = font.render(get_text('new_game'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(640, 144))
        self.screen.blit(text, text_rect)
        
        # 切换玩家按钮
        player_color_text = get_text('black') if self.player_color == PLAYER_BLACK else get_text('white')
        pygame.draw.rect(self.screen, COLORS['BLUE'], (600, 170, 165, 38), border_radius=5)
        text = font.render(f"{get_text('you')}: {player_color_text}", True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(682, 189))
        self.screen.blit(text, text_rect)
        
        # AI模式复选框
        checkbox_x, checkbox_y, checkbox_size = 605, 220, 20
        pygame.draw.rect(self.screen, COLORS['TEXT_LIGHT'], (checkbox_x, checkbox_y, checkbox_size, checkbox_size), 2, border_radius=3)
        if self.ai_enabled:
            pygame.draw.rect(self.screen, COLORS['GREEN'], (checkbox_x + 4, checkbox_y + 4, checkbox_size - 8, checkbox_size - 8), border_radius=2)
        font = get_font(14)
        text = font.render(get_text('ai_mode'), True, COLORS['TEXT_LIGHT'])
        self.screen.blit(text, (checkbox_x + checkbox_size + 8, checkbox_y + 2))
        
        # 时间
        font = get_font(14)
        text = font.render(f"{get_text('time')}: {self.elapsed_time}{get_text('seconds')}", True, COLORS['TEXT_LIGHT'])
        self.screen.blit(text, (600, 260))
        
        # 当前回合/结果
        font = get_font(16)
        if self.game_over:
            winner_name = get_text('you_win_label') if self.winner == self.player_color else get_text('computer_wins')
            current_text = f"{get_text('result')}: {winner_name}"
            text = font.render(current_text, True, COLORS['GREEN_NEON'])
        elif self.paused:
            current_text = get_text('game_paused')
            text = font.render(current_text, True, COLORS['TEXT_LIGHT'])
        else:
            turn_text = get_text('your_turn') if self.current_player == self.player_color else get_text('computer_thinking')
            current_text = turn_text
            text = font.render(current_text, True, COLORS['GREEN'] if self.current_player == self.player_color else COLORS['ORANGE'])
        self.screen.blit(text, (600, 290))
        
        # 操作说明
        font = get_font(12)
        y = 340
        help_texts = [
            get_text('controls') + ':',
            get_text('mouse_place'),
            get_text('pause_game'),
        ]
        for txt in help_texts:
            text = font.render(txt, True, COLORS['TEXT_LIGHT'])
            self.screen.blit(text, (600, y))
            y += 20
        
        # 最快通关按钮
        pygame.draw.rect(self.screen, COLORS['CYAN'], (600, 520, 165, 35), border_radius=5)
        font = get_font(14)
        text = font.render(get_text('top_scores'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(682, 537))
        self.screen.blit(text, text_rect)
    
    def draw_rankings_window(self):
        """绘制排行榜窗口"""
        # 半透明遮罩
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # 窗口
        win_width = 500
        win_height = 450
        win_x = (SCREEN_WIDTH - win_width) // 2
        win_y = (SCREEN_HEIGHT - win_height) // 2
        pygame.draw.rect(self.screen, COLORS['PANEL'], (win_x, win_y, win_width, win_height), border_radius=15)
        pygame.draw.rect(self.screen, COLORS['BLUE'], (win_x, win_y, win_width, win_height), 2, border_radius=15)
        
        # 标题
        font = get_font(28)
        text = font.render(get_text('top_scores'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, win_y + 30))
        self.screen.blit(text, text_rect)
        
        # 关闭按钮
        close_y = win_y + win_height - 50
        pygame.draw.rect(self.screen, COLORS['RED'], (win_x + win_width // 2 - 50, close_y, 100, 35), border_radius=5)
        font = get_font(16)
        text = font.render(get_text('back'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(win_x + win_width // 2, close_y + 17))
        self.screen.blit(text, text_rect)
        
        # 排行榜内容
        list_y = win_y + 70
        scores = db.get_top_scores('gomoku', 50)
        font = get_font(14)
        
        if scores:
            for i, score in enumerate(scores):
                if i >= 15:
                    break
                rank_text = f"{i+1}. {score.get('wins', 0)}胜"
                color = COLORS['GREEN'] if i < 3 else COLORS['TEXT_LIGHT']
                text = font.render(rank_text, True, color)
                self.screen.blit(text, (win_x + 40, list_y + i * 22))
        else:
            text = font.render(get_text('no_records'), True, COLORS['TEXT_GRAY'])
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, list_y + 50))
            self.screen.blit(text, text_rect)


def create_game(screen):
    return Gomoku(screen)