"""
贪吃蛇游戏模块
"""
import pygame
import random
from config import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, get_font
from ui import draw_gradient_background, draw_decorative_circle
from lang import get_text
from db import db

# 贪吃蛇配置
GRID_SIZE = 20  # 格子大小
GRID_WIDTH = 20  # 横向格子数
GRID_HEIGHT = 18  # 纵向格子数

# 初始游戏区域位置
INIT_OFFSET_X = 50
INIT_OFFSET_Y = 80


class Snake:
    """贪吃蛇游戏类"""
    
    def __init__(self, screen):
        self.screen = screen
        # 计算游戏区域位置（右侧留出200px给侧边栏，间距10px）
        self.game_width = GRID_WIDTH * GRID_SIZE
        self.game_height = GRID_HEIGHT * GRID_SIZE
        # 侧边栏x=580, 间距10, 游戏区域右侧=570, 左侧=170
        self.offset_x = 170
        self.offset_y = 80
        self.reset()
        
    def reset(self):
        """初始化游戏"""
        # 蛇的初始位置（中间）
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)  # 向右
        self.next_direction = (1, 0)
        self.score = 0
        self.game_over = False
        self.paused = False
        self.food = None
        self.spawn_food()
        self.start_time = None
        self.elapsed_time = 0
        self.show_rankings = False
        self.last_move_time = pygame.time.get_ticks()
        self.speed = 200  # 移动间隔（毫秒），越小越快
        
    def spawn_food(self):
        """生成食物"""
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake:
                self.food = (x, y)
                break
        
    def update(self):
        """更新游戏"""
        if self.game_over or self.paused:
            return
            
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time < self.speed:
            return
            
        self.last_move_time = current_time
        
        # 首次移动开始计时
        if self.start_time is None:
            self.start_time = current_time
            
        # 更新方向
        self.direction = self.next_direction
        
        # 计算新头部位置
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        
        # 检查是否撞墙
        if new_head[0] < 0 or new_head[0] >= GRID_WIDTH or \
           new_head[1] < 0 or new_head[1] >= GRID_HEIGHT:
            self.game_over = True
            # 保存成绩 - 分数和用时
            if self.score > 0:
                db.save_score('snake', 'Player', self.score, self.elapsed_time, 'normal')
            return
        
        # 检查是否撞到自己
        if new_head in self.snake:
            self.game_over = True
            # 保存成绩 - 分数和用时
            if self.score > 0:
                db.save_score('snake', 'Player', self.score, self.elapsed_time, 'normal')
            return
        
        # 移动蛇
        self.snake.insert(0, new_head)
        
        # 检查是否吃到食物
        if new_head == self.food:
            self.score += 10
            # 速度稍微加快
            if self.score % 50 == 0 and self.speed > 50:
                self.speed -= 5
            self.spawn_food()
        else:
            self.snake.pop()
        
        # 更新时间
        if self.start_time:
            self.elapsed_time = (current_time - self.start_time) // 1000
            
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
            
        if self.game_over or self.paused:
            return
        
        # 方向键
        if key == pygame.K_UP and self.direction != (0, 1):
            self.next_direction = (0, -1)
        elif key == pygame.K_DOWN and self.direction != (0, -1):
            self.next_direction = (0, 1)
        elif key == pygame.K_LEFT and self.direction != (1, 0):
            self.next_direction = (-1, 0)
        elif key == pygame.K_RIGHT and self.direction != (-1, 0):
            self.next_direction = (1, 0)
    
    def handle_click(self, pos, button=1):
        """处理点击"""
        # 侧边栏区域
        sidebar_x = 580
        
        # 暂停/继续按钮 (600, 80, 80, 38)
        if 600 <= pos[0] <= 680 and 80 <= pos[1] <= 118:
            self.paused = not self.paused
            return
        
        # 新游戏按钮 (600, 125, 80, 38)
        if 600 <= pos[0] <= 680 and 125 <= pos[1] <= 163:
            self.reset()
            return
        
        # 最快通关按钮 (600, 520, 165, 35)
        if 600 <= pos[0] <= 765 and 520 <= pos[1] <= 555:
            self.show_rankings = True
            return
        
        # 排行榜窗口关闭
        if getattr(self, 'show_rankings', False):
            win_width = 500
            win_height = 450
            win_x = (SCREEN_WIDTH - win_width) // 2
            win_y = (SCREEN_HEIGHT - win_height) // 2
            
            # 关闭按钮
            close_y = win_y + win_height - 50
            if win_x + win_width // 2 - 50 <= pos[0] <= win_x + win_width // 2 + 50 and \
               close_y <= pos[1] <= close_y + 35:
                self.show_rankings = False
            return
        
    def draw(self):
        """绘制游戏"""
        draw_gradient_background(self.screen)
        draw_decorative_circle(self.screen, 50, 550, 50, COLORS['GREEN_NEON'], 20)
        draw_decorative_circle(self.screen, SCREEN_WIDTH - 50, 50, 40, COLORS['ORANGE_NEON'], 20)
        
        self.draw_game_area()
        self.draw_sidebar()
        
        # 排行榜窗口
        if getattr(self, 'show_rankings', False):
            self.draw_rankings_window()
    
    def draw_game_area(self):
        """绘制游戏区域"""
        # 标题
        font = get_font(36)
        text = font.render(get_text('snake'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(self.offset_x + self.game_width // 2, 40))
        self.screen.blit(text, text_rect)
        
        # 游戏区域背景
        game_rect = pygame.Rect(self.offset_x, self.offset_y, self.game_width, self.game_height)
        pygame.draw.rect(self.screen, COLORS['PANEL'], game_rect, border_radius=5)
        
        # 绘制蛇
        for i, segment in enumerate(self.snake):
            x, y = segment
            rect_x = self.offset_x + x * GRID_SIZE
            rect_y = self.offset_y + y * GRID_SIZE
            rect = pygame.Rect(rect_x, rect_y, GRID_SIZE, GRID_SIZE)
            
            # 头部颜色不同
            if i == 0:
                pygame.draw.rect(self.screen, COLORS['GREEN'], rect)
            else:
                # 身体渐变色
                alpha = max(100, 200 - i * 5)
                color = (0, min(255, 100 + alpha), 0)
                pygame.draw.rect(self.screen, color, rect)
            
            pygame.draw.rect(self.screen, COLORS['FRAME'], rect, 1)
        
        # 绘制食物
        if self.food:
            food_x, food_y = self.food
            rect_x = self.offset_x + food_x * GRID_SIZE + 2
            rect_y = self.offset_y + food_y * GRID_SIZE + 2
            rect = pygame.Rect(rect_x, rect_y, GRID_SIZE - 4, GRID_SIZE - 4)
            pygame.draw.rect(self.screen, COLORS['RED'], rect, border_radius=3)
        
        # 暂停遮罩 - 黑色不透明
        if self.paused:
            overlay = pygame.Surface((self.game_width, self.game_height))
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (self.offset_x, self.offset_y))
            font = get_font(36)
            text = font.render(get_text('pause'), True, COLORS['TEXT_LIGHT'])
            text_rect = text.get_rect(center=(self.offset_x + self.game_width // 2,
                                            self.offset_y + self.game_height // 2))
            self.screen.blit(text, text_rect)
        
        # 游戏结束
        if self.game_over:
            overlay = pygame.Surface((self.game_width, self.game_height))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (self.offset_x, self.offset_y))
            font = get_font(32)
            text = font.render(get_text('game_over_text'), True, COLORS['RED'])
            text_rect = text.get_rect(center=(self.offset_x + self.game_width // 2,
                                            self.offset_y + self.game_height // 2 - 20))
            self.screen.blit(text, text_rect)
            
            font = get_font(20)
            text = font.render(f"{get_text('score')}: {self.score}", True, COLORS['TEXT_LIGHT'])
            text_rect = text.get_rect(center=(self.offset_x + self.game_width // 2,
                                            self.offset_y + self.game_height // 2 + 20))
            self.screen.blit(text, text_rect)
    
    def draw_sidebar(self):
        """绘制侧边栏"""
        # 侧边栏背景
        pygame.draw.rect(self.screen, COLORS['PANEL'], (580, 80, 200, 500), border_radius=10)
        
        # 暂停按钮
        btn_color = COLORS['ORANGE'] if self.paused else COLORS['GREEN']
        pygame.draw.rect(self.screen, btn_color, (600, 80, 80, 38), border_radius=5)
        font = get_font(14)
        text = font.render(get_text('pause') if not self.paused else get_text('resume'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(640, 99))
        self.screen.blit(text, text_rect)
        
        # 新游戏按钮
        pygame.draw.rect(self.screen, COLORS['PURPLE'], (600, 125, 80, 38), border_radius=5)
        text = font.render(get_text('new_game'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(640, 144))
        self.screen.blit(text, text_rect)
        
        # 分数
        font = get_font(20)
        text = font.render(f"{get_text('score')}: {self.score}", True, COLORS['GREEN_NEON'])
        self.screen.blit(text, (600, 175))
        
        # 时间
        text = font.render(f"{get_text('time')}: {self.elapsed_time}s", True, COLORS['TEXT_LIGHT'])
        self.screen.blit(text, (600, 205))
        
        # 操作说明
        font = get_font(12)
        y = 250
        help_texts = [
            (get_text('controls') + ":", COLORS['TEXT_LIGHT']),
            ("1-9: " + get_text('input_number'), COLORS['TEXT_GRAY']),
            ("0/Del: " + get_text('clear_cell'), COLORS['TEXT_GRAY']),
            (get_text('arrows') + ": " + get_text('move'), COLORS['TEXT_GRAY']),
            ("P: " + get_text('pause'), COLORS['TEXT_GRAY']),
        ]
        for txt, color in help_texts:
            text = font.render(txt, True, color)
            self.screen.blit(text, (600, y))
            y += 18
        
        # 最快通关按钮 - 底部保持20px间距
        # 面板底部 y=580, 按钮 y=520, 间距20
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
        scores = db.get_top_scores('snake', 50)
        font = get_font(14)
        
        if scores:
            for i, score in enumerate(scores):
                if i >= 15:
                    break
                score_val = score.get('score', 0) or 0
                time_val = score.get('time_used', 0) or 0
                rank_text = f"{i+1}. {score_val}分 / {time_val}秒"
                color = COLORS['GREEN'] if i < 3 else COLORS['TEXT_LIGHT']
                text = font.render(rank_text, True, color)
                self.screen.blit(text, (win_x + 40, list_y + i * 22))
        else:
            text = font.render(get_text('no_records'), True, COLORS['TEXT_GRAY'])
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, list_y + 50))
            self.screen.blit(text, text_rect)


def create_game(screen):
    return Snake(screen)