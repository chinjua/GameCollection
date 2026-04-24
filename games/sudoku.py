"""
数独游戏模块
"""
import pygame
import random
from config import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, get_font
from ui import draw_gradient_background, draw_decorative_circle
from lang import get_text
from db import db

# 数独游戏配置 - 表格样式
GRID_COLORS = {
    'normal': (0, 0, 0),          # 普通格子边界 - 黑色
    'special': (200, 0, 0),       # 3x3宫边界 - 红色粗线
    'selected': (52, 152, 219),   # 选中格子背景 - 蓝色
    'error': (255, 200, 200),     # 错误数字背景 - 浅红色（数字重复）
    'duplicate': (255, 255, 0),   # 重复数字格子背景 - 黄色
    'bg': (255, 255, 255),        # 格子背景 - 白色
    'fixed': (30, 30, 30),        # 固定数字颜色 - 深黑色
    'user': (155, 89, 182),      # 用户输入颜色 - 紫色
    'custom_user': (0, 0, 0),      # 自定义模式用户输入 - 黑色
    'error_text': (200, 0, 0),    # 错误数字颜色 - 红色
    'selected_text': (255, 255, 255),  # 选中格子数字 - 白色
    'win': (39, 174, 96),        # 完成时背景 - 绿色
}

# 难度配置 (挖空数量)
DIFFICULTY_HOLES = {
    'easy': 35,       # 简单 - 35个空
    'medium': 45,    # 中等 - 45个空
    'hard': 55,      # 困难 - 55个空
    'very_hard': 59, # 极难 - 59个空
    'impossible': 64,  # 不可能 - 64个空
}

# 难度显示名称
DIFFICULTY_ORDER = ['easy', 'medium', 'hard', 'very_hard', 'impossible']

class Sudoku:
    """数独游戏类"""
    
    def __init__(self, screen):
        self.screen = screen
        self.cell_size = 40
        # 游戏区域右侧与侧边栏保持10px间距
        # 侧边栏x=580, 间距10, 游戏区域右侧=570
        # 9*40=360, grid_offset_x=570-360=210
        self.grid_offset_x = 210
        self.grid_offset_y = 120  # 网格起始y坐标，向下移动50像素
        self.difficulty = 'easy'  # 默认难度
        self.custom_mode = False  # 自定义模式
        self.custom_solved = False  # 自定义模式是否已求解
        self.custom_user_input = None  # 解决前保存用户输入
        self.ranking_selected_difficulty = 'easy'  # 排行榜选中的难度
        self.reset()
        
    def reset(self):
        """初始化游戏"""
        self.game_over = False
        self.win = False
        self.paused = False
        self.start_time = None
        self.elapsed_time = 0
        self.paused_time = 0
        self.show_rankings = False
        self.custom_solved = False  # 重置求解状态
        self.custom_user_input = None  # 重置用户输入记录
        self.ranking_selected_difficulty = 'easy'  # 排行榜选中的难度
        
        # 右侧按钮区域
        self.btn_x = 600
        self.btn_width = 80
        
        self.solution = self.generate_sudoku()
        holes = DIFFICULTY_HOLES.get(self.difficulty, 40)
        self.board = self.create_puzzle(self.solution, holes)
        
        # 标记哪些格子是固定的（题目预设的）
        self.fixed = [[self.board[r][c] != 0 for c in range(9)] for r in range(9)]
        
        # 默认选中第一个空格
        self.selected = self.find_first_empty()
        self.errors = [[False for _ in range(9)] for _ in range(9)]
    
    def find_first_empty(self):
        """找到第一个空格位置"""
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    return (r, c)
        return (0, 0)  # 如果没有空格，默认选中(0,0)
    
    def set_difficulty(self, diff):
        """设置难度"""
        if diff in DIFFICULTY_HOLES:
            self.difficulty = diff
            self.reset()
        
    def generate_sudoku(self):
        """生成完整的数独"""
        board = [[0 for _ in range(9)] for _ in range(9)]
        self.solve_sudoku(board)
        return board
        
    def solve_sudoku(self, board):
        """使用回溯算法求解数独"""
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    nums = list(range(1, 10))
                    random.shuffle(nums)
                    for num in nums:
                        if self.is_valid(board, row, col, num):
                            board[row][col] = num
                            if self.solve_sudoku(board):
                                return True
                            board[row][col] = 0
                    return False
        return True
        
    def is_valid(self, board, row, col, num):
        """检查数字是否有效"""
        for c in range(9):
            if board[row][c] == num:
                return False
        for r in range(9):
            if board[r][col] == num:
                return False
        r0, c0 = (row // 3) * 3, (col // 3) * 3
        for r in range(r0, r0 + 3):
            for c in range(c0, c0 + 3):
                if board[r][c] == num:
                    return False
        return True
        
    def create_puzzle(self, solution, holes):
        """创建数独谜题"""
        board = [row[:] for row in solution]
        positions = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(positions)
        for i, (r, c) in enumerate(positions[:holes]):
            board[r][c] = 0
        return board
        
    def select_cell(self, x, y):
        """选择格子"""
        if 0 <= x < 9 and 0 <= y < 9:
            self.selected = (y, x)
            
    def input_number(self, num):
        """输入数字"""
        if self.selected:
            row, col = self.selected
            
            if self.custom_mode:
                # 自定义模式：直接写入 user_grid，不检查 fixed
                self.user_grid[row][col] = num
                # 检查重复
                self.find_all_duplicates_user()
                # 开始计时
                if self.start_time is None:
                    import time
                    self.start_time = time.time()
            else:
                # 正常模式：只能修改非固定的格子
                if not self.fixed[row][col]:
                    self.board[row][col] = num
                    # 检查整行和整列的重复数字
                    self.find_all_duplicates()
                    # 第一次输入时开始计时
                    if self.start_time is None:
                        import time
                        self.start_time = time.time()
                    self.check_win()
    
    def find_all_duplicates(self):
        """找出所有重复的数字格子"""
        self.errors = [[False for _ in range(9)] for _ in range(9)]
        
        # 检查每一行
        for row in range(9):
            counts = {}
            for c in range(9):
                if self.board[row][c] != 0:
                    num = self.board[row][c]
                    counts[num] = counts.get(num, 0) + 1
            # 标记重复的数字
            for c in range(9):
                if self.board[row][c] != 0 and counts[self.board[row][c]] > 1:
                    self.errors[row][c] = True
                    
        # 检查每一列
        for col in range(9):
            counts = {}
            for r in range(9):
                if self.board[r][col] != 0:
                    num = self.board[r][col]
                    counts[num] = counts.get(num, 0) + 1
            # 标记重复的数字
            for r in range(9):
                if self.board[r][col] != 0 and counts[self.board[r][col]] > 1:
                    self.errors[r][col] = True
    
    def find_all_duplicates_user(self):
        """找出自定义模式下 user_grid 的重复数字"""
        self.errors = [[False for _ in range(9)] for _ in range(9)]
        
        # 检查每一行
        for row in range(9):
            counts = {}
            for c in range(9):
                if self.user_grid[row][c] != 0:
                    num = self.user_grid[row][c]
                    counts[num] = counts.get(num, 0) + 1
            # 标记重复的数字
            for c in range(9):
                if self.user_grid[row][c] != 0 and counts[self.user_grid[row][c]] > 1:
                    self.errors[row][c] = True
                    
        # 检查每一列
        for col in range(9):
            counts = {}
            for r in range(9):
                if self.user_grid[r][col] != 0:
                    num = self.user_grid[r][col]
                    counts[num] = counts.get(num, 0) + 1
            # 标记重复的数字
            for r in range(9):
                if self.user_grid[r][col] != 0 and counts[self.user_grid[r][col]] > 1:
                    self.errors[r][col] = True
    
    def check_duplicate(self, row, col, num):
        """检查该行/列是否有重复数字"""
        if num == 0:
            return False
        # 检查同一行
        for c in range(9):
            if c != col and self.board[row][c] == num:
                return True
        # 检查同一列
        for r in range(9):
            if r != row and self.board[r][col] == num:
                return True
        return False
    
    def solve_game(self):
        """自动解决游戏 - 用答案填充所有空格"""
        if self.custom_mode:
            # 保存用户输入
            self.custom_user_input = [row[:] for row in self.user_grid]
            # 自定义模式：从用户输入的格子求解
            board = [row[:] for row in self.user_grid]
            if self.solve_sudoku(board):
                for r in range(9):
                    for c in range(9):
                        self.user_grid[r][c] = board[r][c]
                self.custom_solved = True  # 标记为已求解
        else:
            # 正常模式：将答案复制到当前棋盘
            for r in range(9):
                for c in range(9):
                    self.board[r][c] = self.solution[r][c]
        self.errors = [[False for _ in range(9)] for _ in range(9)]
        self.game_over = False
        self.win = False
        self.selected = (0, 0)
        self.start_time = None
        self.paused_time = 0
        self.paused_time = 0
                
    def check_win(self):
        """检查胜利"""
        for r in range(9):
            for c in range(9):
                if self.board[r][c] != self.solution[r][c]:
                    return
        self.win = True
        self.game_over = True
        self.game_won = True  # 游戏胜利，格子为绿色
        self.showing_complete = True  # 显示完成文字
        # 只有时间大于0才记录排行榜
        if self.elapsed_time > 0:
            db.save_score('sudoku', 'Player', 0, self.elapsed_time, self.difficulty)
        
    def update(self):
        if self.paused:
            return
        if self.start_time and not self.game_over:
            import time
            self.elapsed_time = int(time.time() - self.start_time)
            
    def handle_click(self, pos):
        """处理点击"""
        # 如果排行榜窗口打开，先处理关闭按钮
        if getattr(self, 'show_rankings', False):
            win_width = 500
            win_height = 450
            win_x = (SCREEN_WIDTH - win_width) // 2
            win_y = (SCREEN_HEIGHT - win_height) // 2
            close_y = win_y + win_height - 50
            
            # 检查难度选项卡
            tab_y = win_y + 65
            tab_width = 95
            tab_height = 30
            tab_start_x = win_x + 15
            difficulties = ['easy', 'medium', 'hard', 'very_hard', 'impossible']
            for i, diff in enumerate(difficulties):
                tx = tab_start_x + i * (tab_width + 5)
                if tx <= pos[0] <= tx + tab_width and tab_y <= pos[1] <= tab_y + tab_height:
                    self.ranking_selected_difficulty = diff
                    return
            
            # 关闭按钮
            if win_x + win_width // 2 - 50 <= pos[0] <= win_x + win_width // 2 + 50 and \
               close_y <= pos[1] <= close_y + 35:
                self.show_rankings = False
            return
        
        # 如果游戏已胜利，点击任意位置关闭"完成"文字
        if getattr(self, 'game_won', False) and getattr(self, 'showing_complete', False):
            self.showing_complete = False
            return
            
        # 如果游戏已胜利，点击按钮恢复默认背景
        if getattr(self, 'game_won', False):
            self.game_won = False
            
        # 暂停按钮 (600, 130, 80, 38)
        if 600 <= pos[0] <= 680 and 130 <= pos[1] <= 168:
            self.paused = not self.paused
            if self.paused:
                self.paused_time = self.elapsed_time
            else:
                import time
                self.start_time = time.time() - self.paused_time
            return
            
        # 难度选择按钮区域 - 3行布局
        btn_w, btn_h = 80, 35
        gap = 10
        
        diff_positions = [
            ('easy', 600, 200, btn_w, btn_h),
            ('medium', 600 + btn_w + gap, 200, btn_w, btn_h),
            ('hard', 600, 240, btn_w, btn_h),
            ('very_hard', 600 + btn_w + gap, 240, btn_w, btn_h),
            ('impossible', 600 + btn_w // 2 + gap // 2, 280, btn_w, btn_h),
        ]
        
        for diff, x, y, w, h in diff_positions:
            if x <= pos[0] <= x + w and y <= pos[1] <= y + h:
                self.difficulty = diff
                self.custom_mode = False  # 退出自定义模式
                self.reset()
                return
        
        # 新游戏按钮 (600, 325, 80, 35)
        if 600 <= pos[0] <= 680 and 325 <= pos[1] <= 360:
            self.custom_mode = False  # 退出自定义模式
            self.reset()
            return
        
        # 解决按钮 (690, 325, 80, 35)
        if 690 <= pos[0] <= 770 and 325 <= pos[1] <= 360:
            self.solve_game()
            # 自定义模式下不退出自定义模式，以便显示解题结果
            if not self.custom_mode:
                self.custom_mode = False
            return
        
        # 自定义按钮 (600, 368, 165, 32)
        if 600 <= pos[0] <= 765 and 368 <= pos[1] <= 400:
            # 清空整个网格
            self.board = [[0 for _ in range(9)] for _ in range(9)]
            self.fixed = [[False for _ in range(9)] for _ in range(9)]
            self.user_grid = [[0 for _ in range(9)] for _ in range(9)]
            self.selected = (0, 0)
            self.custom_mode = True
            self.custom_solved = False  # 重置求解状态
            self.custom_user_input = None  # 重置用户输入
            return
        
        # 最快通关按钮 - y位置与draw_sidebar一致
        # 动态计算位置：操作说明后 + 10
        ranking_btn_y = 410 + 18 * 4 + 10  # 492
        if 600 <= pos[0] <= 765 and ranking_btn_y <= pos[1] <= ranking_btn_y + 35:
            self.show_rankings = True
            return
        
        # 网格区域
        x = (pos[0] - self.grid_offset_x) // self.cell_size
        y = (pos[1] - self.grid_offset_y) // self.cell_size
        self.select_cell(x, y)
        
    def handle_key(self, key):
        """处理键盘"""
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
        
        if self.game_over or self.paused:
            return
        
        if not self.selected:
            return
            
        row, col = self.selected
        
        # 方向键移动选中格子
        if key == pygame.K_UP:
            row = (row - 1) % 9
            self.selected = (row, col)
            return
        elif key == pygame.K_DOWN:
            row = (row + 1) % 9
            self.selected = (row, col)
            return
        elif key == pygame.K_LEFT:
            col = (col - 1) % 9
            self.selected = (row, col)
            return
        elif key == pygame.K_RIGHT:
            col = (col + 1) % 9
            self.selected = (row, col)
            return
        
        # 数字键输入（主键盘和小键盘）
        num = None
        if key == pygame.K_1 or key == pygame.K_KP1:
            num = 1
        elif key == pygame.K_2 or key == pygame.K_KP2:
            num = 2
        elif key == pygame.K_3 or key == pygame.K_KP3:
            num = 3
        elif key == pygame.K_4 or key == pygame.K_KP4:
            num = 4
        elif key == pygame.K_5 or key == pygame.K_KP5:
            num = 5
        elif key == pygame.K_6 or key == pygame.K_KP6:
            num = 6
        elif key == pygame.K_7 or key == pygame.K_KP7:
            num = 7
        elif key == pygame.K_8 or key == pygame.K_KP8:
            num = 8
        elif key == pygame.K_9 or key == pygame.K_KP9:
            num = 9
        
        if num is not None:
            self.input_number(num)
            return
        
        # 清空键
        if key in (pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_0, pygame.K_KP0):
            if self.custom_mode:
                # 自定义模式：清除 user_grid
                self.user_grid[row][col] = 0
                self.find_all_duplicates_user()
            else:
                # 正常模式：只能清除非固定的格子
                if not self.fixed[row][col]:
                    self.board[row][col] = 0
                    # 重新检查所有重复格子
                    self.find_all_duplicates()
            return
                
    def draw(self):
        """绘制游戏"""
        draw_gradient_background(self.screen)
        
        # 左侧游戏区域
        self.draw_game_area()
        
        # 右侧按钮栏
        self.draw_sidebar()
        
        # 最快通关窗口
        if getattr(self, 'show_rankings', False):
            self.draw_rankings_window()
    
    def draw_rankings_window(self):
        """绘制最快通关窗口"""
        from config import SCREEN_WIDTH, SCREEN_HEIGHT
        from ui import get_font
        from lang import get_text
        from db import db
        
        # 半透明遮罩
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # 窗口
        win_width = 550
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
        
        # 难度选项卡
        difficulties = ['easy', 'medium', 'hard', 'very_hard', 'impossible']
        tab_y = win_y + 65
        tab_width = 95
        tab_height = 30
        tab_start_x = win_x + 15
        tab_gap = 5
        
        self.ranking_tabs = []  # 保存选项卡区域，供点击检测用
        for i, diff in enumerate(difficulties):
            tx = tab_start_x + i * (tab_width + tab_gap)
            self.ranking_tabs.append((tx, tab_y, tab_width, tab_height, diff))
            color = COLORS['BLUE'] if self.ranking_selected_difficulty == diff else COLORS['TEXT_DARK']
            pygame.draw.rect(self.screen, color, (tx, tab_y, tab_width, tab_height), border_radius=5)
            font = get_font(12)
            text = font.render(get_text(diff), True, COLORS['TEXT_LIGHT'])
            text_rect = text.get_rect(center=(tx + tab_width // 2, tab_y + tab_height // 2))
            self.screen.blit(text, text_rect)
        
        # 关闭按钮
        close_y = win_y + win_height - 50
        pygame.draw.rect(self.screen, COLORS['RED'], (win_x + win_width // 2 - 50, close_y, 100, 35), border_radius=5)
        font = get_font(16)
        text = font.render(get_text('back'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(win_x + win_width // 2, close_y + 17))
        self.screen.blit(text, text_rect)
        
        # 排行榜内容
        list_y = win_y + 110
        scores = db.get_top_scores('sudoku', 50, self.ranking_selected_difficulty)
        font = get_font(14)
        
        if scores:
            for i, score in enumerate(scores):
                if i >= 12:
                    break
                time_val = score.get('time_used', 0) or 0
                rank_text = f"{i+1}. {time_val}s"
                color = COLORS['GREEN'] if i < 3 else COLORS['TEXT_LIGHT']
                text = font.render(rank_text, True, color)
                self.screen.blit(text, (win_x + 40, list_y + i * 22))
        else:
            text = font.render(get_text('no_records'), True, COLORS['TEXT_GRAY'])
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, list_y + 50))
            self.screen.blit(text, text_rect)
        
    def draw_game_area(self):
        """绘制游戏区域"""
        # 装饰
        draw_decorative_circle(self.screen, 50, 550, 50, GRID_COLORS['special'], 20)
        
        # ===== 顶部标签区域 =====
        # 标题居中显示在网格上方
        font = get_font(36)
        title_text = get_text('sudoku')
        text = font.render(title_text, True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(self.grid_offset_x + 9 * self.cell_size // 2, 60))
        self.screen.blit(text, text_rect)
        
        # 难度等级和计时器放在同一行，都用绿色，居中显示
        y_info = 90
        font = get_font(18)  # 增大字体
        
        # 合并成一行文本 - 自定义模式显示"自定义"
        diff_text = get_text('custom') if self.custom_mode else get_text(self.difficulty)
        info_text = f"{get_text('difficulty')}: {diff_text}  |  {get_text('time')}: {self.elapsed_time}{get_text('seconds')}"
        text = font.render(info_text, True, COLORS['GREEN'])
        text_rect = text.get_rect(center=(self.grid_offset_x + 9 * self.cell_size // 2, y_info))
        self.screen.blit(text, text_rect)
        
        # ===== 绘制网格 =====
        self.draw_grid()
        
        # 暂停遮罩 - 黑色不透明
        if self.paused:
            overlay = pygame.Surface((9 * self.cell_size, 9 * self.cell_size))
            overlay.set_alpha(255)  # 黑色不透明
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (self.grid_offset_x, self.grid_offset_y))
            font = get_font(36)
            text = font.render(get_text('pause'), True, COLORS['TEXT_LIGHT'])
            text_rect = text.get_rect(center=(self.grid_offset_x + 9 * self.cell_size // 2, 
                                            self.grid_offset_y + 9 * self.cell_size // 2))
            self.screen.blit(text, text_rect)
            
    def draw_sidebar(self):
        """绘制右侧按钮栏"""
        # 与游戏区域顶部保持相同垂直位置
        # 游戏区域 grid_offset_y = 120
        pygame.draw.rect(self.screen, COLORS['PANEL'], (580, 120, 200, 420), border_radius=10)
        
        # ===== 第一行：暂停按钮 =====
        btn_color = COLORS['ORANGE'] if self.paused else COLORS['GREEN']
        pygame.draw.rect(self.screen, btn_color, (600, 130, 80, 38), border_radius=5)
        font = get_font(14)
        text = font.render(get_text('pause') if not self.paused else get_text('resume'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(640, 149))
        self.screen.blit(text, text_rect)
        
        # ===== 难度选择区域 =====
        # 难度选择标题
        font = get_font(16)
        text = font.render(get_text('difficulty') + ":", True, COLORS['TEXT_LIGHT'])
        self.screen.blit(text, (600, 175))
        
        # 难度按钮 - 3行布局
        # 第一行：简单、中等 (y=200)
        # 第二行：困难、极难 (y=245)
        # 第三行：不可能（居中）(y=290)
        # 避免与下方按钮重叠
        btn_w, btn_h = 80, 35
        gap = 10
        
        diff_layout = [
            [('easy', 600, 200), ('medium', 600 + btn_w + gap, 200)],
            [('hard', 600, 240), ('very_hard', 600 + btn_w + gap, 240)],
            [('impossible', 600 + btn_w // 2 + gap // 2, 280)],  # 居中
        ]
        
        font = get_font(14)
        for row in diff_layout:
            for item in row:
                diff, x, y = item
                if diff == self.difficulty:
                    btn_color = COLORS['GREEN']
                else:
                    btn_color = COLORS['BLUE']
                pygame.draw.rect(self.screen, btn_color, (x, y, btn_w, btn_h), border_radius=5)
                label = get_text(diff)
                text = font.render(label, True, COLORS['TEXT_LIGHT'])
                text_rect = text.get_rect(center=(x + btn_w // 2, y + btn_h // 2))
                self.screen.blit(text, text_rect)
        
        # ===== 操作按钮行：新游戏 | 解决 ===== (y=325)
        # 新游戏按钮
        pygame.draw.rect(self.screen, COLORS['PURPLE'], (600, 325, 80, 35), border_radius=5)
        font = get_font(14)
        text = font.render(get_text('new_game'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(640, 342))
        self.screen.blit(text, text_rect)
        
        # 解决按钮
        pygame.draw.rect(self.screen, COLORS['ORANGE'], (690, 325, 80, 35), border_radius=5)
        font = get_font(14)
        text = font.render(get_text('solve'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(730, 342))
        self.screen.blit(text, text_rect)
        
        # ===== 自定义按钮 =====
        custom_color = COLORS['CYAN'] if self.custom_mode else COLORS['TEXT_GRAY']
        pygame.draw.rect(self.screen, custom_color, (600, 368, 165, 32), border_radius=5)
        font = get_font(14)
        text = font.render(get_text('custom'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(682, 384))
        self.screen.blit(text, text_rect)
        
        # ===== 操作说明区域 =====
        font = get_font(12)
        y = 410
        texts = [
            (get_text('controls') + ":", COLORS['TEXT_LIGHT']),
            ("1-9: " + get_text('input_number'), COLORS['TEXT_GRAY']),
            ("0/Del: " + get_text('clear_cell'), COLORS['TEXT_GRAY']),
            (get_text('arrows') + ": " + get_text('move'), COLORS['TEXT_GRAY']),
        ]
        for txt, color in texts:
            text = font.render(txt, True, color)
            self.screen.blit(text, (600, y))
            y += 18
        
        # ===== 最快通关按钮 =====
        pygame.draw.rect(self.screen, COLORS['CYAN'], (600, y + 10, 165, 35), border_radius=5)
        font = get_font(14)
        text = font.render(get_text('top_scores'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(682, y + 27))
        self.screen.blit(text, text_rect)
            
    def draw_grid(self):
        """绘制网格 - 表格样式"""
        cell_size = self.cell_size
        
        # 绘制外边框（3x3宫边界）
        outer_rect = pygame.Rect(
            self.grid_offset_x, 
            self.grid_offset_y, 
            9 * cell_size, 
            9 * cell_size
        )
        pygame.draw.rect(self.screen, GRID_COLORS['special'], outer_rect, 3)
        
        # 绘制每个格子
        for row in range(9):
            for col in range(9):
                x = self.grid_offset_x + col * cell_size
                y = self.grid_offset_y + row * cell_size
                rect = pygame.Rect(x, y, cell_size, cell_size)
                
                # 背景色
                if self.selected == (row, col):
                    bg = GRID_COLORS['selected']
                elif getattr(self, 'game_won', False):
                    bg = GRID_COLORS['win']  # 完成时背景 - 绿色
                elif self.errors[row][col]:
                    bg = GRID_COLORS['duplicate']  # 重复数字格子 - 黄色
                else:
                    bg = GRID_COLORS['bg']
                    
                pygame.draw.rect(self.screen, bg, rect)
                
                # 内部格子线（细线）
                line_width = 1
                pygame.draw.rect(self.screen, GRID_COLORS['normal'], rect, line_width)
                
                # 3x3宫竖线（加粗）
                if col == 3 or col == 6:
                    pygame.draw.line(self.screen, GRID_COLORS['special'], 
                                   (x, y), (x, y + cell_size), 2)
                
                # 3x3宫横线（加粗）
                if row == 3 or row == 6:
                    pygame.draw.line(self.screen, GRID_COLORS['special'], 
                                   (x, y), (x + cell_size, y), 2)
                
                # 数字
                if self.custom_mode:
                    num = self.user_grid[row][col]
                else:
                    num = self.board[row][col]
                if num != 0:
                    # 判断是固定数字还是用户输入
                    is_fixed = False if self.custom_mode else self.fixed[row][col]
                    
                    # 如果有重复（行或列），显示红色
                    if self.errors[row][col]:
                        color = GRID_COLORS['error_text']
                    elif is_fixed:
                        color = GRID_COLORS['fixed']
                    elif self.custom_mode:
                        # 自定义模式：已求解的用紫色，用户输入的用黑色
                        if self.custom_solved and self.custom_user_input:
                            # 如果是用户输入的数字用黑色，否则用紫色
                            if self.custom_user_input[row][col] != 0:
                                color = GRID_COLORS['custom_user']  # 黑色
                            else:
                                color = GRID_COLORS['user']  # 紫色
                        else:
                            color = GRID_COLORS['custom_user']  # 黑色
                    else:
                        color = GRID_COLORS['user']
                        
                    font = get_font(cell_size - 10)
                    text = font.render(str(num), True, color)
                    text_rect = text.get_rect(center=rect.center)
                    self.screen.blit(text, text_rect)
                    
        # 完成时显示"完成"文字
        if getattr(self, 'showing_complete', False):
            # 在网格区域正中间显示"完成"
            center_x = self.grid_offset_x + 9 * cell_size // 2
            center_y = self.grid_offset_y + 9 * cell_size // 2
            
            # 半透明背景
            overlay = pygame.Surface((250, 60))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            rect = overlay.get_rect(center=(center_x, center_y))
            self.screen.blit(overlay, rect)
            
            # "完成"文字
            font = get_font(36)
            text = font.render(get_text('complete'), True, COLORS['TEXT_LIGHT'])
            text_rect = text.get_rect(center=(center_x, center_y))
            self.screen.blit(text, text_rect)
                    
    def draw_game_over(self):
        """绘制胜利信息"""
        overlay = pygame.Surface((250, 80))
        overlay.set_alpha(200)
        overlay.fill((30, 30, 30))
        rect = overlay.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(overlay, rect)
        
        font = get_font(32)
        text = font.render(get_text('complete'), True, GRID_COLORS['special'])
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(text, text_rect)

def create_game(screen):
    return Sudoku(screen)