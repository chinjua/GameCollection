"""
走迷宫游戏模块
"""
import pygame
from config import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, get_font
from ui import draw_gradient_background, draw_decorative_circle
from lang import get_text
from db import db

# 难度配置
DIFFICULTIES = {
    'easy': {'cols': 10, 'rows': 10, 'cell_size': 40},
    'medium': {'cols': 15, 'rows': 15, 'cell_size': 35},
    'hard': {'cols': 20, 'rows': 20, 'cell_size': 28},
    'very_hard': {'cols': 25, 'rows': 25, 'cell_size': 22},
    'impossible': {'cols': 30, 'rows': 30, 'cell_size': 18},
}

# 默认难度
DEFAULT_DIFFICULTY = 'easy'


class Maze:
    """走迷宫游戏类"""
    
    def __init__(self, screen):
        self.screen = screen
        self.difficulty = DEFAULT_DIFFICULTY
        self.set_difficulty(self.difficulty)
        self.reset()
        
    def set_difficulty(self, difficulty):
        """设置难度"""
        if difficulty in DIFFICULTIES:
            self.difficulty = difficulty
            config = DIFFICULTIES[difficulty]
            self.cols = config['cols']
            self.rows = config['rows']
            self.cell_size = config['cell_size']
            # 游戏区域右侧与侧边栏保持10px间距
            # 侧边栏x=SCREEN_WIDTH-190, 间距10, 游戏区域右侧=SCREEN_WIDTH-200
            self.offset_x = SCREEN_WIDTH - 200 - self.cols * self.cell_size
            self.offset_y = 70  # 向下移动10像素
            
    def reset(self):
        """初始化迷宫"""
        # 强制重新生成迷宫
        self.maze_ready = False
        self.generate_maze()
        self.player_x = 0
        self.player_y = 0
        self.goal_x = self.cols - 1
        self.goal_y = self.rows - 1
        self.start_time = None
        self.elapsed_time = 0
        self.won = False
        self.moves = 0
        self.paused = False
        self.pause_time = None  # 暂停开始时间
        self.solution_path = None  # 解决路径
        self.show_rankings = False
        self.player_path = [(0, 0)]  # 玩家走过的路径
        self.current_key = None  # 当前按住的键
        self.last_move_time = 0  # 上次移动时间
        self.move_repeat_start = 150  # 按住多久后开始连续移动（毫秒）
        self.move_repeat_interval = 80  # 连续移动间隔（毫秒）
        
    def solve_maze(self):
        """使用BFS找迷宫路径"""
        from collections import deque
        
        if not self.maze:
            return
        
        # BFS找路径
        queue = deque([(0, 0, [])])
        visited = {(0, 0)}
        
        while queue:
            x, y, path = queue.popleft()
            
            # 到达终点
            if x == self.goal_x and y == self.goal_y:
                self.solution_path = path + [(x, y)]
                return
            
            # 检查四个方向
            if not self.maze[y][x]['N'] and (x, y-1) not in visited:
                visited.add((x, y-1))
                queue.append((x, y-1, path + [(x, y)]))
            if not self.maze[y][x]['S'] and (x, y+1) not in visited:
                visited.add((x, y+1))
                queue.append((x, y+1, path + [(x, y)]))
            if not self.maze[y][x]['E'] and (x+1, y) not in visited:
                visited.add((x+1, y))
                queue.append((x+1, y, path + [(x, y)]))
            if not self.maze[y][x]['W'] and (x-1, y) not in visited:
                visited.add((x-1, y))
                queue.append((x-1, y, path + [(x, y)]))
        
    def generate_maze(self):
        """使用DFS生成迷宫"""
        import random as _random
        # 初始化迷宫，所有格子都有墙
        self.maze = [[{'N': True, 'S': True, 'E': True, 'W': True, 'visited': False} 
                      for _ in range(self.cols)] for _ in range(self.rows)]
        
        # DFS生成迷宫
        stack = []
        current = (0, 0)
        self.maze[0][0]['visited'] = True
        stack.append(current)
        
        directions = [('N', 0, -1), ('S', 0, 1), ('E', 1, 0), ('W', -1, 0)]
        
        while stack:
            current = stack[-1]
            x, y = current
            
            # 获取未访问的邻居
            neighbors = []
            if y > 0 and not self.maze[y-1][x]['visited']:
                neighbors.append(('N', x, y-1))
            if y < self.rows - 1 and not self.maze[y+1][x]['visited']:
                neighbors.append(('S', x, y+1))
            if x < self.cols - 1 and not self.maze[y][x+1]['visited']:
                neighbors.append(('E', x+1, y))
            if x > 0 and not self.maze[y][x-1]['visited']:
                neighbors.append(('W', x-1, y))
            
            if neighbors:
                # 随机选择邻居
                idx = _random.randint(0, len(neighbors) - 1)
                direction, nx, ny = neighbors[idx]
                
                # 移除墙壁
                if direction == 'N':
                    self.maze[y][x]['N'] = False
                    self.maze[ny][nx]['S'] = False
                elif direction == 'S':
                    self.maze[y][x]['S'] = False
                    self.maze[ny][nx]['N'] = False
                elif direction == 'E':
                    self.maze[y][x]['E'] = False
                    self.maze[ny][nx]['W'] = False
                elif direction == 'W':
                    self.maze[y][x]['W'] = False
                    self.maze[ny][nx]['E'] = False
                
                self.maze[ny][nx]['visited'] = True
                stack.append((nx, ny))
            else:
                stack.pop()
        # 标记迷宫已生成
        self.maze_ready = True
    
    def handle_key(self, key):
        """处理按键"""
        if self.won:
            return
        
        # P键暂停
        if key == pygame.K_p:
            if self.paused:
                # 恢复游戏，调整start_time，减去暂停时间
                if self.pause_time:
                    pause_duration = pygame.time.get_ticks() - self.pause_time
                    if self.start_time:
                        self.start_time += pause_duration
                self.paused = False
                self.pause_time = None
            else:
                # 暂停游戏，记录暂停开始时间
                self.paused = True
                self.pause_time = pygame.time.get_ticks()
            return
        
        # 暂停时不处理移动
        if self.paused:
            return
            
        # 首次移动时开始计时
        if self.start_time is None:
            self.start_time = pygame.time.get_ticks()
        
        x, y = self.player_x, self.player_y
        
        if key == pygame.K_UP or key == pygame.K_w:
            if not self.maze[y][x]['N']:
                self.player_y -= 1
                self.moves += 1
                new_pos = (self.player_x, self.player_y)
                # 如果后退到已走过的位置，截断路径
                if new_pos in self.player_path:
                    idx = self.player_path.index(new_pos)
                    self.player_path = self.player_path[:idx + 1]
                else:
                    self.player_path.append(new_pos)
        elif key == pygame.K_DOWN or key == pygame.K_s:
            if not self.maze[y][x]['S']:
                self.player_y += 1
                self.moves += 1
                new_pos = (self.player_x, self.player_y)
                if new_pos in self.player_path:
                    idx = self.player_path.index(new_pos)
                    self.player_path = self.player_path[:idx + 1]
                else:
                    self.player_path.append(new_pos)
        elif key == pygame.K_LEFT or key == pygame.K_a:
            if not self.maze[y][x]['W']:
                self.player_x -= 1
                self.moves += 1
                new_pos = (self.player_x, self.player_y)
                if new_pos in self.player_path:
                    idx = self.player_path.index(new_pos)
                    self.player_path = self.player_path[:idx + 1]
                else:
                    self.player_path.append(new_pos)
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            if not self.maze[y][x]['E']:
                self.player_x += 1
                self.moves += 1
                new_pos = (self.player_x, self.player_y)
                if new_pos in self.player_path:
                    idx = self.player_path.index(new_pos)
                    self.player_path = self.player_path[:idx + 1]
                else:
                    self.player_path.append(new_pos)
        
        # 检查是否到达终点
        if self.player_x == self.goal_x and self.player_y == self.goal_y:
            self.won = True
            if self.start_time:
                self.elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
            # 游戏停止，不再计时
            self.start_time = None
            # 游戏胜利时生成解决路径
            self.solve_maze()
            # 保存成绩 - 按难度分别保存（使用实际时间）
            db.save_score('maze', 'Player', 0, int(self.elapsed_time * 10), self.difficulty)

    def try_move(self, key):
        """尝试朝指定方向移动，返回是否成功"""
        if self.won or self.paused:
            return False

        x, y = self.player_x, self.player_y

        if key == pygame.K_UP or key == pygame.K_w:
            if not self.maze[y][x]['N']:
                self.player_y -= 1
                self.moves += 1
                self.record_move()
                return True
        elif key == pygame.K_DOWN or key == pygame.K_s:
            if not self.maze[y][x]['S']:
                self.player_y += 1
                self.moves += 1
                self.record_move()
                return True
        elif key == pygame.K_LEFT or key == pygame.K_a:
            if not self.maze[y][x]['W']:
                self.player_x -= 1
                self.moves += 1
                self.record_move()
                return True
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            if not self.maze[y][x]['E']:
                self.player_x += 1
                self.moves += 1
                self.record_move()
                return True
        return False

    def record_move(self):
        """记录移动，更新路径"""
        new_pos = (self.player_x, self.player_y)
        if new_pos in self.player_path:
            idx = self.player_path.index(new_pos)
            self.player_path = self.player_path[:idx + 1]
        else:
            self.player_path.append(new_pos)

        # 检查是否到达终点
        if self.player_x == self.goal_x and self.player_y == self.goal_y:
            self.won = True
            if self.start_time:
                self.elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
            self.start_time = None
            self.solve_maze()
            db.save_score('maze', 'Player', 0, int(self.elapsed_time * 10), self.difficulty)

    def handle_key_down(self, key):
        """处理按键按下"""
        if key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s,
                   pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
            if self.current_key != key:
                self.current_key = key
                self.last_move_time = pygame.time.get_ticks()
                # 立即尝试移动一次
                self.try_move(key)
        elif key == pygame.K_p:
            if self.paused:
                if self.pause_time:
                    pause_duration = pygame.time.get_ticks() - self.pause_time
                    if self.start_time:
                        self.start_time += pause_duration
                self.paused = False
                self.pause_time = None
            else:
                self.paused = True
                self.pause_time = pygame.time.get_ticks()

    def handle_key_up(self, key):
        """处理按键释放"""
        if key == self.current_key:
            self.current_key = None

    def handle_click(self, pos, button=1):
        """处理点击"""
        x, y = pos
        
        # 如果排行榜窗口打开，先处理关闭和难度切换
        if getattr(self, 'show_rankings', False):
            win_width = 750
            win_height = 500
            win_x = (SCREEN_WIDTH - win_width) // 2
            win_y = (SCREEN_HEIGHT - win_height) // 2
            
            # 关闭按钮
            close_y = win_y + win_height - 45
            if win_x + win_width // 2 - 50 <= x <= win_x + win_width // 2 + 50 and \
               close_y <= y <= close_y + 35:
                self.show_rankings = False
                return
            
            # 难度选项卡
            tab_y = win_y + 60
            tab_width = 120
            for i, diff in enumerate(['easy', 'medium', 'hard', 'very_hard', 'impossible']):
                tab_x = win_x + 25 + i * (tab_width + 10)
                if tab_x <= x <= tab_x + tab_width and tab_y <= y <= tab_y + 35:
                    self.difficulty = diff
                    self.reset()
                    return
            return
        
        sidebar_start = 70
        sidebar_height = 348
        sidebar_width = 180
        sidebar_x = SCREEN_WIDTH - sidebar_width - 10
        btn_x = sidebar_x + 20
        btn_width = 140
        row_height = 40
        gap = 8
        
        # ===== 第一行：暂停按钮 =====
        row1_y = sidebar_start + 15
        if btn_x <= x <= btn_x + btn_width and row1_y <= y <= row1_y + 32:
            if self.paused:
                if self.pause_time:
                    pause_duration = pygame.time.get_ticks() - self.pause_time
                    if self.start_time:
                        self.start_time += pause_duration
                self.paused = False
                self.pause_time = None
            else:
                self.paused = True
                self.pause_time = pygame.time.get_ticks()
            return
        
        # ===== 第二行：新游戏按钮 =====
        row2_y = row1_y + row_height + gap
        if btn_x <= x <= btn_x + btn_width and row2_y <= y <= row2_y + 32:
            self.reset()
            return
        
        # ===== 第三行：解决按钮 =====
        row3_y = row2_y + row_height + gap
        if btn_x <= x <= btn_x + btn_width and row3_y <= y <= row3_y + 32:
            self.solve_maze()
            return
        
        # ===== 第四行：难度按钮 =====
        row4_y = row3_y + row_height + gap
        diff_width = btn_width // 3 - 4
        for i, diff in enumerate(['easy', 'medium', 'hard']):
            dx = btn_x + i * (diff_width + 6)
            if dx <= x <= dx + diff_width and row4_y <= y <= row4_y + 32:
                self.set_difficulty(diff)
                self.reset()
                return
        
        # ===== 第五行：更高难度按钮 =====
        row5_y = row4_y + row_height + gap
        for i, diff in enumerate(['very_hard', 'impossible']):
            dx = btn_x + i * (diff_width + 6)
            if dx <= x <= dx + diff_width and row5_y <= y <= row5_y + 32:
                self.set_difficulty(diff)
                self.reset()
                return
        
        # ===== 第六行：时间 =====
        row6_y = row5_y + row_height + gap
        
        # ===== 第七行：步数 =====
        row7_y = row6_y + row_height + gap - 10
        
        # ===== 最快通关按钮 =====
        row_btn_y = row7_y + row_height + gap + 25  # 底部位置，与绘制一致
        if btn_x <= x <= btn_x + btn_width and row_btn_y <= y <= row_btn_y + 35:
            self.show_rankings = True
            return
        
        # 游戏胜利后，点击迷宫区域可以显示/隐藏解决路径
        if self.won:
            maze_end_x = self.offset_x + self.cols * self.cell_size
            maze_end_y = self.offset_y + self.rows * self.cell_size
            if self.offset_x <= x <= maze_end_x and self.offset_y <= y <= maze_end_y:
                if self.solution_path:
                    self.solution_path = None
                else:
                    self.solve_maze()
                return
    
    def update(self):
        """更新游戏"""
        # 暂停时不计时
        if self.paused or self.won:
            return
        if self.start_time:
            self.elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000

        # 处理连续移动
        if self.current_key is not None:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_move_time >= self.move_repeat_interval:
                # 尝试朝当前方向移动
                moved = self.try_move(self.current_key)
                if moved:
                    self.last_move_time = current_time
    
    def draw(self):
        """绘制游戏"""
        draw_gradient_background(self.screen)
        draw_decorative_circle(self.screen, 50, 550, 50, COLORS['PURPLE_NEON'], 20)
        draw_decorative_circle(self.screen, SCREEN_WIDTH - 50, 50, 40, COLORS['ORANGE_NEON'], 20)
        
        # 每次进入游戏都重新生成迷宫（清除旧的迷宫数据）
        if not hasattr(self, 'maze_ready') or not self.maze_ready:
            self.reset()
        
        self.draw_maze()
        self.draw_sidebar()
        
        # 最快通关窗口
        if getattr(self, 'show_rankings', False):
            self.draw_rankings_window()
    
    def draw_rankings_window(self):
        """绘制最快通关窗口 - 显示所有难度前50名"""
        # 半透明遮罩
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # 窗口 - 加宽以显示五个难度
        win_width = 750
        win_height = 500
        win_x = (SCREEN_WIDTH - win_width) // 2
        win_y = (SCREEN_HEIGHT - win_height) // 2
        pygame.draw.rect(self.screen, COLORS['PANEL'], (win_x, win_y, win_width, win_height), border_radius=15)
        pygame.draw.rect(self.screen, COLORS['BLUE'], (win_x, win_y, win_width, win_height), 2, border_radius=15)
        
        # 标题
        font = get_font(28)
        text = font.render(get_text('top_scores'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, win_y + 25))
        self.screen.blit(text, text_rect)
        
        # 难度选项卡 - 5列布局
        tab_y = win_y + 60
        tab_width = 120
        tab_height = 35
        difficulties = ['easy', 'medium', 'hard', 'very_hard', 'impossible']
        
        for i, diff in enumerate(difficulties):
            x = win_x + 25 + i * (tab_width + 10)
            bg = COLORS['GREEN'] if self.difficulty == diff else COLORS['BLUE']
            pygame.draw.rect(self.screen, bg, (x, tab_y, tab_width, tab_height), border_radius=5)
            font = get_font(12)
            text = font.render(get_text(diff), True, COLORS['TEXT_LIGHT'])
            text_rect = text.get_rect(center=(x + tab_width // 2, tab_y + tab_height // 2))
            self.screen.blit(text, text_rect)
        
        # 关闭按钮
        close_y = win_y + win_height - 45
        pygame.draw.rect(self.screen, COLORS['RED'], (win_x + win_width // 2 - 50, close_y, 100, 35), border_radius=5)
        font = get_font(16)
        text = font.render(get_text('back'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(win_x + win_width // 2, close_y + 17))
        self.screen.blit(text, text_rect)
        
        # 当前难度排行榜内容 - 显示前50名
        list_y = tab_y + 50
        scores = db.get_top_scores('maze', 50, self.difficulty)
        font = get_font(14)
        
        if scores:
            for i, score in enumerate(scores):
                if i >= 25:
                    break
                time_used = score.get('time_used', 0) or 0
                time_seconds = time_used / 10
                rank_text = f"{i+1}. {time_seconds:.1f}s"
                color = COLORS['GREEN'] if i < 3 else COLORS['TEXT_LIGHT']
                text = font.render(rank_text, True, color)
                self.screen.blit(text, (win_x + 40, list_y + i * 18))
        else:
            text = font.render(get_text('no_records'), True, COLORS['TEXT_GRAY'])
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, list_y + 50))
            self.screen.blit(text, text_rect)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, list_y + 50))
            self.screen.blit(text, text_rect)
        
    def draw_maze(self):
        """绘制迷宫"""
        # 标题 - 水平垂直居中
        font = get_font(40)
        text = font.render(get_text('maze'), True, COLORS['TEXT_LIGHT'])
        # 计算居中位置
        maze_width = self.cols * self.cell_size
        text_rect = text.get_rect(center=(self.offset_x + maze_width // 2, 40))
        self.screen.blit(text, text_rect)
        
        # 绘制迷宫墙壁
        for y in range(self.rows):
            for x in range(self.cols):
                cell = self.maze[y][x]
                px = self.offset_x + x * self.cell_size
                py = self.offset_y + y * self.cell_size
                
                # 绘制墙壁
                if cell['N']:
                    pygame.draw.line(self.screen, COLORS['TEXT_LIGHT'], 
                                   (px, py), (px + self.cell_size, py), 2)
                if cell['S']:
                    pygame.draw.line(self.screen, COLORS['TEXT_LIGHT'], 
                                   (px, py + self.cell_size), (px + self.cell_size, py + self.cell_size), 2)
                if cell['E']:
                    pygame.draw.line(self.screen, COLORS['TEXT_LIGHT'], 
                                   (px + self.cell_size, py), (px + self.cell_size, py + self.cell_size), 2)
                if cell['W']:
                    pygame.draw.line(self.screen, COLORS['TEXT_LIGHT'], 
                                   (px, py), (px, py + self.cell_size), 2)
        
        # 绘制起点
        start_rect = pygame.Rect(self.offset_x + 2, self.offset_y + 2, 
                                self.cell_size - 4, self.cell_size - 4)
        pygame.draw.rect(self.screen, COLORS['GREEN'], start_rect)
        
        # 绘制终点
        goal_rect = pygame.Rect(self.offset_x + self.goal_x * self.cell_size + 2, 
                               self.offset_y + self.goal_y * self.cell_size + 2,
                               self.cell_size - 4, self.cell_size - 4)
        pygame.draw.rect(self.screen, COLORS['RED'], goal_rect)
        
        # 绘制玩家
        player_rect = pygame.Rect(self.offset_x + self.player_x * self.cell_size + 5,
                                  self.offset_y + self.player_y * self.cell_size + 5,
                                  self.cell_size - 10, self.cell_size - 10)
        pygame.draw.rect(self.screen, COLORS['YELLOW'], player_rect, border_radius=5)
        
        # 绘制玩家走过的路径（绿色细线）
        if hasattr(self, 'player_path') and len(self.player_path) > 1:
            for i in range(len(self.player_path) - 1):
                x1, y1 = self.player_path[i]
                x2, y2 = self.player_path[i + 1]
                cx1 = self.offset_x + x1 * self.cell_size + self.cell_size // 2
                cy1 = self.offset_y + y1 * self.cell_size + self.cell_size // 2
                cx2 = self.offset_x + x2 * self.cell_size + self.cell_size // 2
                cy2 = self.offset_y + y2 * self.cell_size + self.cell_size // 2
                pygame.draw.line(self.screen, COLORS['GREEN'], (cx1, cy1), (cx2, cy2), 1)
        
        # 绘制解决路径（细线）
        if self.solution_path:
            for i in range(len(self.solution_path) - 1):
                x1, y1 = self.solution_path[i]
                x2, y2 = self.solution_path[i + 1]
                # 计算单元格中心
                cx1 = self.offset_x + x1 * self.cell_size + self.cell_size // 2
                cy1 = self.offset_y + y1 * self.cell_size + self.cell_size // 2
                cx2 = self.offset_x + x2 * self.cell_size + self.cell_size // 2
                cy2 = self.offset_y + y2 * self.cell_size + self.cell_size // 2
                pygame.draw.line(self.screen, COLORS['CYAN'], (cx1, cy1), (cx2, cy2), 3)
        
        # 暂停遮罩 (黑色不透明)
        if self.paused:
            overlay = pygame.Surface((self.cols * self.cell_size, self.rows * self.cell_size))
            overlay.set_alpha(255)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (self.offset_x, self.offset_y))
            font = get_font(36)
            text = font.render(get_text('pause'), True, COLORS['TEXT_LIGHT'])
            text_rect = text.get_rect(center=(self.offset_x + self.cols * self.cell_size // 2,
                                            self.offset_y + self.rows * self.cell_size // 2))
            self.screen.blit(text, text_rect)
        
        # 胜利信息
        if self.won:
            overlay = pygame.Surface((self.cols * self.cell_size, self.rows * self.cell_size))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (self.offset_x, self.offset_y))
            font = get_font(28)
            text = font.render(get_text('you_win'), True, COLORS['GREEN_NEON'])
            text_rect = text.get_rect(center=(self.offset_x + self.cols * self.cell_size // 2,
                                            self.offset_y + self.rows * self.cell_size // 2 - 20))
            self.screen.blit(text, text_rect)
            
            font = get_font(20)
            info = f"{get_text('time')}: {self.elapsed_time:.1f}s  {get_text('moves')}: {self.moves}"
            text = font.render(info, True, COLORS['TEXT_LIGHT'])
            text_rect = text.get_rect(center=(self.offset_x + self.cols * self.cell_size // 2,
                                            self.offset_y + self.rows * self.cell_size // 2 + 20))
            self.screen.blit(text, text_rect)
    
    def draw_sidebar(self):
        """绘制侧边栏 - 右侧，每行一个按钮"""
        # 与游戏区域顶部保持相同垂直位置 (offset_y=70)
        sidebar_start = 70
        # 按钮位置: y≈323, height=35, bottom≈358, 面板底部 = 358+20=378
        sidebar_height = 420
        sidebar_width = 180
        sidebar_x = SCREEN_WIDTH - sidebar_width - 10
        btn_x = sidebar_x + 20
        btn_width = 140
        row_height = 40
        gap = 8
        
        # 侧边栏背景
        pygame.draw.rect(self.screen, COLORS['PANEL'], (sidebar_x, sidebar_start, sidebar_width, sidebar_height), border_radius=10)
        
        # ===== 第一行：暂停按钮 =====
        row1_y = sidebar_start + 15
        btn_color = COLORS['ORANGE'] if self.paused else COLORS['GREEN']
        pygame.draw.rect(self.screen, btn_color, (btn_x, row1_y, btn_width, 32), border_radius=5)
        font = get_font(12)
        text = font.render(get_text('pause') if not self.paused else get_text('resume'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(btn_x + btn_width // 2, row1_y + 16))
        self.screen.blit(text, text_rect)
        
        # ===== 第二行：新游戏按钮 =====
        row2_y = row1_y + row_height + gap
        pygame.draw.rect(self.screen, COLORS['PURPLE'], (btn_x, row2_y, btn_width, 32), border_radius=5)
        text = font.render(get_text('new_game'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(btn_x + btn_width // 2, row2_y + 16))
        self.screen.blit(text, text_rect)
        
        # ===== 第三行：解决按钮 =====
        row3_y = row2_y + row_height + gap
        pygame.draw.rect(self.screen, COLORS['BLUE'], (btn_x, row3_y, btn_width, 32), border_radius=5)
        text = font.render(get_text('solve'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(btn_x + btn_width // 2, row3_y + 16))
        self.screen.blit(text, text_rect)
        
        # ===== 第四行：难度选择 =====
        row4_y = row3_y + row_height + gap
        diff_colors = {'easy': COLORS['GREEN'], 'medium': COLORS['ORANGE'], 'hard': COLORS['RED']}
        diff_width = btn_width // 3 - 4
        for i, diff in enumerate(['easy', 'medium', 'hard']):
            dx = btn_x + i * (diff_width + 6)
            color = diff_colors[diff] if self.difficulty == diff else COLORS['TEXT_GRAY']
            pygame.draw.rect(self.screen, color, (dx, row4_y, diff_width, 32), border_radius=5)
            font = get_font(11)
            text = font.render(get_text(diff), True, COLORS['TEXT_LIGHT'])
            text_rect = text.get_rect(center=(dx + diff_width // 2, row4_y + 16))
            self.screen.blit(text, text_rect)
        
        # ===== 第五行：更高难度 =====
        row5_y = row4_y + row_height + gap
        diff_colors2 = {'very_hard': COLORS['PURPLE'], 'impossible': COLORS['RED']}
        for i, diff in enumerate(['very_hard', 'impossible']):
            dx = btn_x + i * (diff_width + 6)
            color = diff_colors2[diff] if self.difficulty == diff else COLORS['TEXT_GRAY']
            pygame.draw.rect(self.screen, color, (dx, row5_y, diff_width, 32), border_radius=5)
            font = get_font(10)
            text = font.render(get_text(diff), True, COLORS['TEXT_LIGHT'])
            text_rect = text.get_rect(center=(dx + diff_width // 2, row5_y + 16))
            self.screen.blit(text, text_rect)
        
        # ===== 第六行：时间 =====
        row6_y = row5_y + row_height + gap
        font = get_font(14)
        current_time = self.elapsed_time if self.start_time else 0
        text = font.render(f"{get_text('time')}: {current_time:.1f}s", True, COLORS['GREEN_NEON'])
        self.screen.blit(text, (btn_x, row6_y))
        
        # ===== 第七行：步数 =====
        row7_y = row6_y + row_height + gap - 10
        text = font.render(f"{get_text('moves')}: {self.moves}", True, COLORS['TEXT_LIGHT'])
        self.screen.blit(text, (btn_x, row7_y))
        
        # ===== 最快通关按钮 - 底部 =====
        row_btn_y = row7_y + row_height + gap + 25
        pygame.draw.rect(self.screen, COLORS['CYAN'], (btn_x, row_btn_y, btn_width, 35), border_radius=5)
        font = get_font(12)
        text = font.render(get_text('top_scores'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(btn_x + btn_width // 2, row_btn_y + 17))
        self.screen.blit(text, text_rect)


def create_game(screen):
    return Maze(screen)
