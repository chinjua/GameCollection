"""
扫雷游戏模块
"""
import pygame
import random
from config import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, get_font
from ui import draw_gradient_background, draw_decorative_circle
from lang import get_text
from db import db

class Minesweeper:
    """扫雷游戏类"""
    
    # 难度配置
    DIFFICULTIES = {
        'easy': {'width': 9, 'height': 9, 'mines': 10, 'name': 'Easy'},
        'medium': {'width': 16, 'height': 16, 'mines': 40, 'name': 'Medium'},
        'hard': {'width': 20, 'height': 16, 'mines': 60, 'name': 'Hard'},
    }
    
    def __init__(self, screen):
        self.screen = screen
        self.difficulty = 'easy'
        config = self.DIFFICULTIES['easy']
        self.width = config['width']
        self.height = config['height']
        self.mines = config['mines']
        self.cell_size = 36  # 增加格子大小
        self.reset()
        
    def set_difficulty(self, difficulty):
        config = self.DIFFICULTIES[difficulty]
        self.width = config['width']
        self.height = config['height']
        self.mines = config['mines']
        self.difficulty = difficulty
        if difficulty == 'easy':
            self.cell_size = 36
        elif difficulty == 'medium':
            self.cell_size = 30
        else:  # hard
            self.cell_size = 28
        self.reset()
        
    def reset(self):
        # 游戏区域居中
        game_width = self.width * self.cell_size
        game_height = self.height * self.cell_size
        self.offset_x = (SCREEN_WIDTH - game_width) // 2
        self.offset_y = 105  # 向上移动5像素
        
        # 计算网格底部位置
        self.grid_bottom = self.offset_y + game_height
        
        self.game_over = False
        self.win = False
        self.paused = False
        self.first_click = True
        self.start_time = None
        self.elapsed_time = 0
        self.paused_time = 0
        self.show_rankings = False
        
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.revealed = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.flagged = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.marked = [[False for _ in range(self.width)] for _ in range(self.height)]  # 问号标记
        self.mine_count = self.mines
        
        self.font = get_font(36)
        self.small_font = get_font(24)
        
    def place_mines(self, exclude_x, exclude_y):
        positions = set()
        while len(positions) < self.mines:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if abs(x - exclude_x) <= 1 and abs(y - exclude_y) <= 1:
                continue
            positions.add((x, y))
            
        for x, y in positions:
            self.grid[y][x] = -1
            
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] != -1:
                    self.grid[y][x] = self.count_mines(x, y)
                    
    def count_mines(self, x, y):
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.grid[ny][nx] == -1:
                        count += 1
        return count
        
    def reveal(self, x, y):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        if self.revealed[y][x] or self.flagged[y][x]:
            return
            
        self.revealed[y][x] = True
        
        if self.grid[y][x] == -1:
            self.game_over = True
            self.win = False
            self.reveal_all_mines()
            self.save_result()
            return
            
        if self.grid[y][x] == 0:
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if not self.revealed[ny][nx] and not self.flagged[ny][nx]:
                            self.reveal(nx, ny)
        self.check_win()
        
    def toggle_flag(self, x, y):
        """切换标记状态：无 -> 旗帜 -> 问号 -> 无"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        if self.revealed[y][x]:
            return
        
        # 状态转换：无 -> 旗 -> 问号 -> 无
        if self.flagged[y][x]:
            # 旗 -> 问号
            self.flagged[y][x] = False
            self.marked[y][x] = True
            self.mine_count += 1  # 取消旗，加回地雷数
        elif self.marked[y][x]:
            # 问号 -> 无
            self.marked[y][x] = False
        else:
            # 无 -> 旗
            self.flagged[y][x] = True
            self.mine_count -= 1  # 标记旗，减少地雷数
            
    def reveal_all_mines(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == -1:
                    self.revealed[y][x] = True
                    
    def check_win(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] != -1 and not self.revealed[y][x]:
                    return
        self.win = True
        self.game_over = True
        self.save_result()
        
    def save_result(self):
        db.save_score('minesweeper', 'Player', 0, self.elapsed_time, self.difficulty)
        
    def update(self):
        if self.paused:
            return
        if self.start_time and not self.game_over:
            import time
            self.elapsed_time = int(time.time() - self.start_time)
            
    def handle_key(self, key):
        """处理按键"""
        # 排行榜窗口打开时按ESC关闭
        if getattr(self, 'show_rankings', False):
            if key == pygame.K_ESCAPE:
                self.show_rankings = False
            return
        
        # P键暂停
        if key == pygame.K_p:
            if self.paused:
                # 恢复游戏
                import time
                self.start_time = time.time() - self.paused_time
                self.paused = False
            else:
                # 暂停游戏
                self.paused = True
                self.paused_time = self.elapsed_time
            return
            
    def handle_click(self, pos, button):
        # 网格布局参数
        cols = 4
        rows = 2
        btn_width = 85
        btn_height = 35
        spacing_x = 15  # 与draw_bottom_panel一致
        spacing_y = 15
        
        # 按钮区域尺寸
        btn_area_width = cols * btn_width + (cols - 1) * spacing_x
        btn_area_height = rows * btn_height + (rows - 1) * spacing_y
        
        # 面板尺寸
        panel_width = 450
        panel_height = 130
        
        # 面板位置（网格底部下方固定间距）
        grid_to_panel_gap = 30
        panel_y = getattr(self, 'grid_bottom', 490) + grid_to_panel_gap
        
        # 面板水平居中
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        
        # 按钮起始位置（面板内居中）
        btn_start_x = panel_x + (panel_width - btn_area_width) // 2
        btn_start_y = panel_y + (panel_height - btn_area_height) // 2
        
        # ===== 排行榜窗口点击处理 =====
        if getattr(self, 'show_rankings', False):
            win_width = 600
            win_height = 450
            win_x = (SCREEN_WIDTH - win_width) // 2
            win_y = (SCREEN_HEIGHT - win_height) // 2
            
            # 关闭按钮
            close_y = win_y + win_height - 50
            if win_x + win_width // 2 - 50 <= pos[0] <= win_x + win_width // 2 + 50 and close_y <= pos[1] <= close_y + 35:
                self.show_rankings = False
                return
            
            # 难度选项卡点击
            tab_y = win_y + 70
            tab_width = 180
            for i, diff in enumerate(['easy', 'medium', 'hard']):
                x = win_x + 30 + i * (tab_width + 10)
                if x <= pos[0] <= x + tab_width and tab_y <= pos[1] <= tab_y + 35:
                    self.difficulty = diff
                    return
            return
        
        # ===== 4x2 网格按钮点击 =====
        buttons = [
            ('pause', 'pause'),
            ('new_game', 'new_game'),
            ('rankings', 'rankings'),
            ('solve', 'solve'),
            ('easy', 'easy'),
            ('medium', 'medium'),
            ('hard', 'hard'),
        ]
        
        for i, (_, action) in enumerate(buttons):
            row = i // cols
            col = i % cols
            x = btn_start_x + col * (btn_width + spacing_x)
            y = btn_start_y + row * (btn_height + spacing_y)
            
            if x <= pos[0] <= x + btn_width and y <= pos[1] <= y + btn_height:
                if action == 'pause':
                    self.paused = not self.paused
                    if self.paused:
                        self.paused_time = self.elapsed_time
                    else:
                        import time
                        self.start_time = time.time() - self.paused_time
                elif action == 'new_game':
                    self.reset()
                elif action == 'rankings':
                    self.show_rankings = True
                elif action == 'solve':
                    self.solve()
                elif action in ('easy', 'medium', 'hard'):
                    self.set_difficulty(action)
                return
        
        if self.game_over or self.paused:
            return
            
        x = (pos[0] - self.offset_x) // self.cell_size
        y = (pos[1] - self.offset_y) // self.cell_size
        
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
            
        if button == 1:
            if self.first_click:
                self.place_mines(x, y)
                self.first_click = False
                import time
                self.start_time = time.time()
            self.reveal(x, y)
        elif button == 3:
            self.toggle_flag(x, y)
            
    def solve(self):
        """自动揭示所有地雷"""
        if self.game_over or self.win or self.paused:
            return
        if self.first_click:
            # 需要先点击一次才能布雷
            return
        # 直接揭开所有格子，不通过reveal()，避免触发check_win()保存成绩
        for y in range(self.height):
            for x in range(self.width):
                self.revealed[y][x] = True
        self.win = True
        self.game_over = True
        # 自动扫雷不计入排行榜
    
    def draw(self):
        """绘制游戏"""
        draw_gradient_background(self.screen)
        
        # 绘制游戏区域
        self.draw_game_area()
        
        # 绘制底部面板
        self.draw_bottom_panel()
        
        # 绘制排行榜窗口
        if getattr(self, 'show_rankings', False):
            self.draw_rankings_window()
    
    def draw_game_area(self):
        """绘制游戏区域"""
        draw_decorative_circle(self.screen, 20, 550, 40, COLORS['BLUE_NEON'], 15)
        
        # 标题
        font = get_font(36)
        text = font.render(get_text('minesweeper'), True, COLORS['TEXT_LIGHT'])
        game_width = self.width * self.cell_size
        text_rect = text.get_rect(center=(self.offset_x + game_width // 2, 40))
        self.screen.blit(text, text_rect)
        
        # 地雷数量和时间
        font = get_font(18)
        info_text = f"{get_text('mines')}: {self.mine_count}  |  {get_text('time')}: {self.elapsed_time}{get_text('seconds')}"
        text = font.render(info_text, True, COLORS['GREEN'])
        text_rect = text.get_rect(center=(self.offset_x + game_width // 2, 75))
        self.screen.blit(text, text_rect)
        
        if self.paused:
            overlay = pygame.Surface((self.width * self.cell_size, self.height * self.cell_size))
            overlay.set_alpha(255)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (self.offset_x, self.offset_y))
            font = get_font(32)
            text = font.render(get_text('pause'), True, COLORS['TEXT_LIGHT'])
            text_rect = text.get_rect(center=(self.offset_x + self.width * self.cell_size // 2, 
                                            self.offset_y + self.height * self.cell_size // 2))
            self.screen.blit(text, text_rect)
            return
            
        if self.game_over:
            overlay = pygame.Surface((self.width * self.cell_size, self.height * self.cell_size))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (self.offset_x, self.offset_y))
        
        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect(
                    self.offset_x + x * self.cell_size,
                    self.offset_y + y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                
                if self.revealed[y][x]:
                    if self.grid[y][x] == -1:
                        color = (50, 60, 75)
                    else:
                        color = (50, 60, 75)
                    pygame.draw.rect(self.screen, color, rect)
                    pygame.draw.rect(self.screen, COLORS['FRAME'], rect, 1)
                    
                    # 游戏结束时用旗帜显示地雷
                    if self.game_over and self.grid[y][x] == -1:
                        center = rect.center
                        pygame.draw.line(self.screen, COLORS['RED'], 
                                 (center[0], center[1] - 8),
                                 (center[0], center[1] + 8), 2)
                        pts = [(center[0], center[1] - 8), (center[0] + 6, center[1] - 3), (center[0], center[1])]
                        pygame.draw.polygon(self.screen, COLORS['RED'], pts)
                    
                    if self.grid[y][x] > 0:
                        num = self.grid[y][x]
                        color = COLORS.get(f'MINE_{num}', COLORS['TEXT_LIGHT'])
                        font = get_font(self.cell_size - 6)
                        text = font.render(str(num), True, color)
                        text_rect = text.get_rect(center=rect.center)
                        self.screen.blit(text, text_rect)
                else:
                    pygame.draw.rect(self.screen, COLORS['PANEL'], rect)
                    pygame.draw.rect(self.screen, COLORS['BLUE'], rect, 1)
                    
                    if self.flagged[y][x]:
                        # 绘制旗帜
                        center = rect.center
                        pygame.draw.line(self.screen, COLORS['RED'], 
                                 (center[0], center[1] - 8),
                                 (center[0], center[1] + 8), 2)
                        pts = [(center[0], center[1] - 8), (center[0] + 6, center[1] - 3), (center[0], center[1])]
                        pygame.draw.polygon(self.screen, COLORS['RED'], pts)
                    elif self.marked[y][x]:
                        # 绘制问号
                        font = get_font(self.cell_size - 8)
                        text = font.render("?", True, COLORS['YELLOW'])
                        text_rect = text.get_rect(center=rect.center)
                        self.screen.blit(text, text_rect)

    def draw_rankings_window(self):
        """绘制排行榜窗口"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        win_width = 600
        win_height = 450
        win_x = (SCREEN_WIDTH - win_width) // 2
        win_y = (SCREEN_HEIGHT - win_height) // 2
        pygame.draw.rect(self.screen, COLORS['PANEL'], (win_x, win_y, win_width, win_height), border_radius=15)
        pygame.draw.rect(self.screen, COLORS['BLUE'], (win_x, win_y, win_width, win_height), 2, border_radius=15)
        
        font = get_font(28)
        text = font.render(get_text('top_scores'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, win_y + 30))
        self.screen.blit(text, text_rect)
        
        tab_y = win_y + 70
        tab_width = 180
        tab_height = 35
        
        for i, diff in enumerate(['easy', 'medium', 'hard']):
            x = win_x + 30 + i * (tab_width + 10)
            bg = COLORS['GREEN'] if self.difficulty == diff else COLORS['BLUE']
            pygame.draw.rect(self.screen, bg, (x, tab_y, tab_width, tab_height), border_radius=5)
            font = get_font(14)
            text = font.render(get_text(diff), True, COLORS['TEXT_LIGHT'])
            text_rect = text.get_rect(center=(x + tab_width // 2, tab_y + tab_height // 2))
            self.screen.blit(text, text_rect)
        
        list_y = tab_y + 50
        scores = db.get_top_scores('minesweeper', 50, self.difficulty)
        font = get_font(14)
        
        if scores:
            for i, score in enumerate(scores):
                if i >= 18:
                    break
                time_val = score.get('time_used', 0) or 0
                rank_text = f"{i+1}. {time_val:.1f}s"
                color = COLORS['GREEN'] if i < 3 else COLORS['TEXT_LIGHT']
                text = font.render(rank_text, True, color)
                self.screen.blit(text, (win_x + 40, list_y + i * 22))
        else:
            text = font.render(get_text('no_records'), True, COLORS['TEXT_GRAY'])
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, list_y + 50))
            self.screen.blit(text, text_rect)
        
        close_y = win_y + win_height - 50
        pygame.draw.rect(self.screen, COLORS['RED'], (win_x + win_width // 2 - 50, close_y, 100, 35), border_radius=5)
        font = get_font(16)
        text = font.render(get_text('back'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(win_x + win_width // 2, close_y + 17))
        self.screen.blit(text, text_rect)
    
    def draw_bottom_panel(self):
        """绘制底部按钮栏 - 2行4列，底部区域内居中"""
        # 网格布局参数
        cols = 4
        rows = 2
        btn_width = 85
        btn_height = 35
        spacing_x = 15  # 按钮水平间距
        spacing_y = 15  # 按钮垂直间距
        
        # 按钮区域尺寸
        btn_area_width = cols * btn_width + (cols - 1) * spacing_x
        btn_area_height = rows * btn_height + (rows - 1) * spacing_y
        
        # 面板尺寸
        panel_width = 450
        panel_height = 130  # 固定高度
        
        # 面板位置（网格底部下方固定间距）
        grid_to_panel_gap = 30  # # 网格与底部区域固定垂直间距
        panel_y = getattr(self, 'grid_bottom', 490) + grid_to_panel_gap
        
        # 面板水平居中
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        
        # 绘制底部面板
        pygame.draw.rect(self.screen, COLORS['PANEL'], (panel_x, panel_y, panel_width, panel_height), border_radius=10)
        
        # 2行4列按钮布局（在面板内居中）
        buttons = [
            (get_text('pause') if not self.paused else get_text('resume'), COLORS['ORANGE'] if self.paused else COLORS['GREEN']),
            (get_text('new_game'), COLORS['PURPLE']),
            (get_text('top_scores'), COLORS['CYAN']),
            (get_text('solve'), COLORS['RED']),
            (get_text('easy'), COLORS['GREEN'] if self.difficulty == 'easy' else COLORS['BLUE']),
            (get_text('medium'), COLORS['GREEN'] if self.difficulty == 'medium' else COLORS['BLUE']),
            (get_text('hard'), COLORS['GREEN'] if self.difficulty == 'hard' else COLORS['BLUE']),
        ]
        
        # 按钮起始位置（面板内居中）
        btn_start_x = panel_x + (panel_width - btn_area_width) // 2
        btn_start_y = panel_y + (panel_height - btn_area_height) // 2
        
        font = get_font(12)
        for i, (label, color) in enumerate(buttons):
            row = i // cols
            col = i % cols
            x = btn_start_x + col * (btn_width + spacing_x)
            y = btn_start_y + row * (btn_height + spacing_y)
            pygame.draw.rect(self.screen, color, (x, y, btn_width, btn_height), border_radius=5)
            text = font.render(label, True, COLORS['TEXT_LIGHT'])
            text_rect = text.get_rect(center=(x + btn_width // 2, y + btn_height // 2))
            self.screen.blit(text, text_rect)
    
    def create_game(screen):
        return Minesweeper(screen)