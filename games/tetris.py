"""
俄罗斯方块游戏模块
"""
import pygame
import random
from config import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, TETRIS_BLOCK_SIZE, TETRIS_WIDTH, TETRIS_HEIGHT, get_font
from ui import draw_gradient_background, draw_decorative_circle
from lang import get_text
from db import db

class Tetris:
    """俄罗斯方块游戏类"""
    
    SHAPES = [
        [[1, 1, 1, 1]],
        [[1, 1], [1, 1]],
        [[0, 1, 0], [1, 1, 1]],
        [[0, 1, 1], [1, 1, 0]],
        [[1, 1, 0], [0, 1, 1]],
        [[1, 0, 0], [1, 1, 1]],
        [[0, 0, 1], [1, 1, 1]],
    ]
    
    COLORS = [
        (26, 188, 156),
        (241, 196, 15),
        (155, 89, 182),
        (39, 174, 96),
        (231, 76, 60),
        (52, 152, 219),
        (230, 126, 34),
    ]
    
    def __init__(self, screen):
        self.screen = screen
        self.width = TETRIS_WIDTH
        self.height = TETRIS_HEIGHT
        self.block_size = TETRIS_BLOCK_SIZE
        # 游戏区域右侧与侧边栏保持10px间距
        # 侧边栏x=580, 间距10, 游戏区域右侧=570
        game_width = self.width * self.block_size
        self.offset_x = 570 - game_width
        self.offset_y = 60
        self.reset()
        
    def reset(self):
        self.board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.current_piece = None
        self.current_color = None
        self.current_x = 0
        self.current_y = 0
        self.next_piece = None
        self.next_color = None
        self.score = 0
        self.level = 1
        self.lines = 0
        self.game_over = False
        self.paused = False
        self.paused_time = 0
        self.drop_speed = 500
        self.show_rankings = False
        self.last_drop = pygame.time.get_ticks()
        self.first_spawn = True
        self.spawn_piece()
        
    def spawn_piece(self):
        if self.next_piece is None:
            idx = random.randint(0, len(self.SHAPES) - 1)
            self.current_piece = [row[:] for row in self.SHAPES[idx]]
            self.current_color = self.COLORS[idx]
            idx = random.randint(0, len(self.SHAPES) - 1)
            self.next_piece = [row[:] for row in self.SHAPES[idx]]
            self.next_color = self.COLORS[idx]
        else:
            self.current_piece = self.next_piece
            self.current_color = self.next_color
            idx = random.randint(0, len(self.SHAPES) - 1)
            self.next_piece = [row[:] for row in self.SHAPES[idx]]
            self.next_color = self.COLORS[idx]
            
        self.current_x = self.width // 2 - len(self.current_piece[0]) // 2
        self.current_y = 0
        
        if self.first_spawn:
            self.first_spawn = False
            return
            
        if self.check_collision():
            self.game_over = True
            
    def rotate_piece(self):
        if self.current_piece is None:
            return
        rotated = list(zip(*self.current_piece[::-1]))
        old_piece = self.current_piece
        self.current_piece = [list(row) for row in rotated]
        if self.check_collision():
            self.current_piece = old_piece
            
    def move_piece(self, dx, dy):
        old_x, old_y = self.current_x, self.current_y
        self.current_x += dx
        self.current_y += dy
        if self.check_collision():
            self.current_x, self.current_y = old_x, old_y
            return False
        return True
            
    def check_collision(self):
        if self.current_piece is None:
            return True
        for y, row in enumerate(self.current_piece):
            for x, cell in enumerate(row):
                if cell:
                    nx = self.current_x + x
                    ny = self.current_y + y
                    if nx < 0 or nx >= self.width or ny >= self.height:
                        return True
                    if ny >= 0 and self.board[ny][nx]:
                        return True
        return False
        
    def lock_piece(self):
        if self.current_piece is None:
            return
        for y, row in enumerate(self.current_piece):
            for x, cell in enumerate(row):
                if cell:
                    nx = self.current_x + x
                    ny = self.current_y + y
                    if 0 <= ny < self.height and 0 <= nx < self.width:
                        self.board[ny][nx] = self.current_color
        self.clear_lines()
        self.spawn_piece()
        
    def clear_lines(self):
        lines_cleared = 0
        for y in range(self.height):
            if all(self.board[y]):
                for y2 in range(y, 0, -1):
                    self.board[y2] = self.board[y2 - 1][:]
                self.board[0] = [0] * self.width
                lines_cleared += 1
                y += 1
        if lines_cleared > 0:
            points = [0, 100, 300, 500, 800]
            self.score += points[lines_cleared] * self.level
            self.lines += lines_cleared
            if self.lines >= self.level * 10:
                self.level += 1
                self.drop_speed = max(100, 500 - (self.level - 1) * 50)
                
    def drop_piece(self):
        if not self.move_piece(0, 1):
            self.lock_piece()
            
    def update(self):
        if self.game_over or self.paused:
            return
        current_time = pygame.time.get_ticks()
        if current_time - self.last_drop > self.drop_speed:
            self.drop_piece()
            self.last_drop = current_time
            
    def handle_click(self, pos, button=1):
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
        
        # 暂停按钮 (600, 70, 80, 38)
        if 600 <= pos[0] <= 680 and 70 <= pos[1] <= 108:
            self.paused = not self.paused
            return
        # 新游戏按钮 (600, 115, 80, 38)
        if 600 <= pos[0] <= 680 and 115 <= pos[1] <= 153:
            self.reset()
            return
        
        # 最快通关按钮 (600, 450, 165, 35)
        if 600 <= pos[0] <= 765 and 450 <= pos[1] <= 485:
            self.show_rankings = True
            return
        
    def handle_key(self, key):
        # 游戏结束时不处理按键
        if self.game_over:
            return
        
        # P键暂停功能
        if key == pygame.K_p:
            self.paused = not self.paused
            if self.paused:
                self.paused_time = pygame.time.get_ticks()
            else:
                # 恢复时调整last_drop
                if self.paused_time:
                    paused_duration = pygame.time.get_ticks() - self.paused_time
                    self.last_drop += paused_duration
                    self.paused_time = 0
            return
        
        # 暂停时不处理其他按键
        if self.paused:
            return
        
        # 检查当前方块是否存在
        if self.current_piece is None:
            return
        
        if key == pygame.K_LEFT:
            self.move_piece(-1, 0)
        elif key == pygame.K_RIGHT:
            self.move_piece(1, 0)
        elif key == pygame.K_DOWN:
            self.drop_piece()
        elif key == pygame.K_UP:
            self.rotate_piece()
        elif key == pygame.K_SPACE:
            while self.move_piece(0, 1):
                pass
            self.lock_piece()
    
    def draw(self):
        draw_gradient_background(self.screen)
        draw_decorative_circle(self.screen, 50, 550, 50, COLORS['PURPLE_NEON'], 20)
        draw_decorative_circle(self.screen, SCREEN_WIDTH - 50, 50, 40, COLORS['ORANGE_NEON'], 20)
        self.draw_game_area()
        self.draw_sidebar()
        
        # 最快通关窗口
        if getattr(self, 'show_rankings', False):
            self.draw_rankings_window()
    
    def draw_rankings_window(self):
        """绘制最快通关窗口"""
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
        scores = db.get_top_scores('tetris', 50)
        font = get_font(14)
        
        if scores:
            for i, score in enumerate(scores):
                if i >= 15:
                    break
                score_val = score.get('score', 0) or 0
                rank_text = f"{i+1}. {score_val}"
                color = COLORS['GREEN'] if i < 3 else COLORS['TEXT_LIGHT']
                text = font.render(rank_text, True, color)
                self.screen.blit(text, (win_x + 40, list_y + i * 22))
        else:
            text = font.render(get_text('no_records'), True, COLORS['TEXT_GRAY'])
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, list_y + 50))
            self.screen.blit(text, text_rect)
        
    def draw_game_area(self):
        # 标题
        font = get_font(40)
        text = font.render(get_text('tetris'), True, COLORS['TEXT_LIGHT'])
        self.screen.blit(text, (self.offset_x, 20))
        
        # 游戏区域
        game_rect = pygame.Rect(
            self.offset_x, self.offset_y,
            self.width * self.block_size,
            self.height * self.block_size
        )
        pygame.draw.rect(self.screen, COLORS['PANEL'], game_rect)
        pygame.draw.rect(self.screen, COLORS['CYAN'], game_rect, 2)
        
        # 已落下的方块
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x]:
                    rect = pygame.Rect(
                        self.offset_x + x * self.block_size,
                        self.offset_y + y * self.block_size,
                        self.block_size,
                        self.block_size
                    )
                    pygame.draw.rect(self.screen, self.board[y][x], rect)
                    pygame.draw.rect(self.screen, (44, 62, 80), rect, 1)
                    
        # 当前方块
        if self.current_piece and not self.game_over:
            for y, row in enumerate(self.current_piece):
                for x, cell in enumerate(row):
                    if cell:
                        rect = pygame.Rect(
                            self.offset_x + (self.current_x + x) * self.block_size,
                            self.offset_y + (self.current_y + y) * self.block_size,
                            self.block_size,
                            self.block_size
                        )
                        pygame.draw.rect(self.screen, self.current_color, rect)
                        pygame.draw.rect(self.screen, (44, 62, 80), rect, 1)
                        
        # 暂停遮罩 (黑色不透明)
        if self.paused:
            overlay = pygame.Surface((self.width * self.block_size, self.height * self.block_size))
            overlay.set_alpha(255)  # 不透明
            overlay.fill((0, 0, 0))  # 黑色
            self.screen.blit(overlay, (self.offset_x, self.offset_y))
            font = get_font(36)
            text = font.render(get_text('pause'), True, COLORS['TEXT_LIGHT'])
            text_rect = text.get_rect(center=(self.offset_x + self.width * self.block_size // 2, 
                                            self.offset_y + self.height * self.block_size // 2))
            self.screen.blit(text, text_rect)
            
        # 游戏结束
        if self.game_over:
            self.draw_game_over()
            
    def draw_game_over(self):
        overlay = pygame.Surface((250, 100))
        overlay.set_alpha(200)
        overlay.fill((30, 30, 30))
        rect = overlay.get_rect(center=(self.offset_x + self.width * self.block_size // 2, 
                                        self.offset_y + self.height * self.block_size // 2))
        self.screen.blit(overlay, rect)
        font = get_font(32)
        text = font.render(get_text('game_over_text'), True, COLORS['RED'])
        text_rect = text.get_rect(center=(self.offset_x + self.width * self.block_size // 2, 
                                        self.offset_y + self.height * self.block_size // 2 - 20))
        self.screen.blit(text, text_rect)
        
    def draw_sidebar(self):
        # 与游戏区域顶部保持相同垂直位置 (offset_y=60)
        pygame.draw.rect(self.screen, COLORS['PANEL'], (580, 60, 205, 445), border_radius=10)
        
        # 暂停按钮 (宽80, 高38)
        btn_color = COLORS['ORANGE'] if self.paused else COLORS['GREEN']
        pygame.draw.rect(self.screen, btn_color, (600, 70, 80, 38), border_radius=5)
        font = get_font(14)
        text = font.render(get_text('pause') if not self.paused else get_text('resume'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(640, 89))
        self.screen.blit(text, text_rect)
        
        # 新游戏按钮 (宽80, 高38)
        pygame.draw.rect(self.screen, COLORS['PURPLE'], (600, 115, 80, 38), border_radius=5)
        text = font.render(get_text('new_game'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(640, 134))
        self.screen.blit(text, text_rect)
        
        # 分数
        font = get_font(20)
        text = font.render(f"{get_text('score')}: {self.score}", True, COLORS['GREEN_NEON'])
        self.screen.blit(text, (600, 165))
        
        # 等级
        text = font.render(f"{get_text('level')}: {self.level}", True, COLORS['TEXT_LIGHT'])
        self.screen.blit(text, (600, 195))
        
        # 行数
        text = font.render(f"{get_text('lines')}: {self.lines}", True, COLORS['TEXT_LIGHT'])
        self.screen.blit(text, (600, 225))
        
        # 下一个方块标题
        font = get_font(14)
        text = font.render(f"{get_text('next')}:", True, COLORS['TEXT_LIGHT'])
        self.screen.blit(text, (600, 260))
        
        # 下一个方块预览
        if self.next_piece:
            next_size = 20
            for y, row in enumerate(self.next_piece):
                for x, cell in enumerate(row):
                    if cell:
                        rect = pygame.Rect(610 + x * next_size, 280 + y * next_size, next_size - 1, next_size - 1)
                        pygame.draw.rect(self.screen, self.next_color, rect)
        
        # 操作说明
        font = get_font(12)
        y = 330
        help_texts = [
            ("Controls", ""),
            ("<- -> : Move", ""),
            ("UP : Rotate", ""),
            ("DOWN : Drop", ""),
            ("SPACE : Fast", ""),
            ("P : Pause", ""),
        ]
        for txt, _ in help_texts:
            text = font.render(txt, True, COLORS['TEXT_GRAY'])
            self.screen.blit(text, (600, y))
            y += 16
        
        # 最快通关按钮
        pygame.draw.rect(self.screen, COLORS['CYAN'], (600, 450, 165, 35), border_radius=5)
        font = get_font(14)
        text = font.render(get_text('top_scores'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(682, 467))
        self.screen.blit(text, text_rect)

def create_game(screen):
    return Tetris(screen)