"""
UI组件模块
包含按钮、面板等通用UI组件
"""
import pygame
import math
import random
from config import COLORS, BUTTON_WIDTH, BUTTON_HEIGHT, get_font

# 字体大小默认值
FONT_SMALL = 20
FONT_MIDDLE = 28
FONT_LARGE = 36
FONT_TITLE = 48


def draw_gradient_background(screen, color1=None, color2=None):
    """绘制渐变背景"""
    color1 = color1 or COLORS['BG_GRADIENT_START']
    color2 = color2 or COLORS['BG_GRADIENT_END']
    
    height = screen.get_height()
    width = screen.get_width()
    
    for y in range(height):
        # 计算插值颜色
        ratio = y / height
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2] - color1[2]) * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (width, y))


def draw_decorative_circle(screen, x, y, radius, color, alpha=30):
    """绘制装饰性圆形"""
    temp_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(temp_surface, (*color, alpha), (radius, radius), radius)
    screen.blit(temp_surface, (x - radius, y - radius))


def draw_glow_effect(screen, x, y, radius, color):
    """绘制发光效果"""
    for i in range(3):
        alpha = 40 - i * 12
        r = radius + i * 8
        temp_surface = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp_surface, (*color, alpha), (r, r), r)
        screen.blit(temp_surface, (x - r, y - r))


def draw_card_background(screen, rect, color=None, radius=10):
    """绘制卡片背景"""
    color = color or COLORS['PANEL']
    
    # 绘制阴影
    shadow_rect = pygame.Rect(rect.x + 4, rect.y + 4, rect.width, rect.height)
    pygame.draw.rect(screen, COLORS['SHADOW'], shadow_rect, border_radius=radius)
    
    # 绘制主背景
    pygame.draw.rect(screen, color, rect, border_radius=radius)
    
    # 绘制高光边框
    pygame.draw.rect(screen, COLORS['HIGHLIGHT'], rect, 2, border_radius=radius)


def draw_neon_border(screen, rect, color, radius=10):
    """绘制霓虹边框"""
    # 外发光
    for i in range(3):
        alpha = 60 - i * 18
        temp_surface = pygame.Surface((rect.width + i * 8, rect.height + i * 8), pygame.SRCALPHA)
        pygame.draw.rect(temp_surface, (*color, alpha), temp_surface.get_rect(), border_radius=radius + i * 2)
        screen.blit(temp_surface, (rect.x - i * 4 - 4, rect.y - i * 4 - 4))
    
    # 主边框
    pygame.draw.rect(screen, color, rect, 2, border_radius=radius)


def draw_particle(screen, x, y, color, size=3):
    """绘制粒子"""
    temp_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    pygame.draw.circle(temp_surface, color, (size, size), size)
    screen.blit(temp_surface, (x - size, y - size))

pygame.font.init()

class Button:
    """按钮组件"""
    def __init__(self, x, y, width, height, text, color=None, text_color=None, 
                 font_size=FONT_MIDDLE, callback=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color or COLORS['BUTTON']
        self.base_color = self.color
        self.text_color = text_color or COLORS['TEXT_LIGHT']
        self.font_size = font_size
        self.callback = callback
        self.is_hovered = False
        self.is_pressed = False
        
    def draw(self, screen):
        """绘制按钮"""
        # 根据状态选择颜色
        if self.is_pressed:
            color = tuple(max(0, c - 30) for c in self.base_color)
        elif self.is_hovered:
            color = COLORS['BUTTON_HOVER']
        else:
            color = self.base_color
            
        # 绘制圆角矩形（使用多边形模拟）
        self.draw_rounded_rect(screen, color, self.rect, radius=8)
        
        # 绘制文字
        font = get_font(self.font_size)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def draw_rounded_rect(self, screen, color, rect, radius=8):
        """绘制圆角矩形"""
        # 绘制填充
        pygame.draw.rect(screen, color, rect, border_radius=radius)
        # 绘制边框
        pygame.draw.rect(screen, tuple(max(0, c - 20) for c in color), 
                     rect, 2, border_radius=radius)
        
    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
            self.is_pressed = False
            
    def update(self, x, y):
        """更新位置"""
        self.rect.x = x
        self.rect.y = y
        
class Label:
    """标签组件"""
    def __init__(self, x, y, text, font_size=FONT_MIDDLE, color=None, center=False):
        self.x = x
        self.y = y
        self.text = text
        self.font_size = font_size
        self.color = color or COLORS['TEXT_DARK']
        self.center = center
        self.surface = None
        self.rect = None
        self.update()
        
    def update(self, text=None):
        """更新文本"""
        if text is not None:
            self.text = text
        font = get_font(self.font_size)
        self.surface = font.render(self.text, True, self.color)
        self.rect = self.surface.get_rect()
        if self.center:
            self.rect.center = (self.x, self.y)
        else:
            self.rect.topleft = (self.x, self.y)
            
    def draw(self, screen):
        """绘制标签"""
        if self.surface:
            screen.blit(self.surface, self.rect)

class Panel:
    """面板组件"""
    def __init__(self, x, y, width, height, color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color or COLORS['PANEL']
        
    def draw(self, screen):
        """绘制面板"""
        pygame.draw.rect(screen, self.color, self.rect, border_radius=10)
        pygame.draw.rect(screen, tuple(max(0, c - 15) for c in self.color),
                    self.rect, 2, border_radius=10)
        
    def set_position(self, x, y):
        """设置位置"""
        self.rect.x = x
        self.rect.y = y

class InputBox:
    """输入框组件"""
    def __init__(self, x, y, width, height, placeholder="", font_size=FONT_MIDDLE):
        self.rect = pygame.Rect(x, y, width, height)
        self.placeholder = placeholder
        self.text = ""
        self.font_size = font_size
        self.active = False
        
    def draw(self, screen):
        """绘制输入框"""
        # 边框颜色
        border_color = COLORS['BUTTON'] if self.active else COLORS['GRID_LINE']
        pygame.draw.rect(screen, COLORS['BG'], self.rect)
        pygame.draw.rect(screen, border_color, self.rect, 2)
        
        # 文字
        font = get_font(self.font_size)
        display_text = self.text if self.text else self.placeholder
        color = COLORS['TEXT_DARK'] if self.text else COLORS['TEXT_GRAY']
        text_surface = font.render(display_text, True, color)
        text_rect = text_surface.get_rect(midleft=self.rect.left + 10, centery=self.rect.centery)
        screen.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isalnum() and len(self.text) < 20:
                self.text += event.unicode

def draw_text(screen, text, x, y, font_size, color, center=False):
    """便捷的文字绘制函数"""
    font = get_font(font_size)
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surface, rect)

def draw_centered_text(screen, text, x, y, font_size, color):
    """绘制居中文字"""
    draw_text(screen, text, x, y, font_size, color, center=True)


class Dropdown:
    """下拉列表组件"""
    def __init__(self, x, y, width, height, options, callback=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options  # [(label, value), ...]
        self.callback = callback
        self.is_open = False
        self.option_height = height
        self.selected_index = 0
        self.is_hovered = False
        self.hover_index = 0
        
    def get_selected(self):
        """获取选中的值"""
        return self.options[self.selected_index]
        
    def draw(self, screen):
        """绘制下拉列表"""
        # 主按钮
        bg_color = COLORS['BUTTON'] if not self.is_hovered else COLORS['BUTTON_HOVER']
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=5)
        pygame.draw.rect(screen, tuple(max(0, c - 20) for c in bg_color), self.rect, 2, border_radius=5)
        
# 显示选中项 - 减小字体
        font = get_font(18)
        text = font.render(self.options[self.selected_index][0], True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(midleft=(self.rect.left + 10, self.rect.centery))
        screen.blit(text, text_rect)

        # 箭头
        arrow_x = self.rect.right - 20
        arrow_y = self.rect.centery
        points = [(arrow_x, arrow_y - 4), (arrow_x - 4, arrow_y + 4), (arrow_x + 4, arrow_y + 4)]
        pygame.draw.polygon(screen, COLORS['TEXT_LIGHT'], points)

        # 下拉选项
        if self.is_open:
            overlay_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, len(self.options) * self.option_height)
            pygame.draw.rect(screen, COLORS['PANEL'], overlay_rect, border_radius=5)
            pygame.draw.rect(screen, COLORS['TEXT_LIGHT'], overlay_rect, 2, border_radius=5)
            
            for i, (label, value) in enumerate(self.options):
                opt_rect = pygame.Rect(self.rect.x, self.rect.bottom + i * self.option_height, self.rect.width, self.option_height)
                bg = COLORS['BUTTON'] if i == self.selected_index else COLORS['GRID_LINE']
                pygame.draw.rect(screen, bg, opt_rect)
                
                font = get_font(18)
                text = font.render(label, True, COLORS['TEXT_LIGHT'])
                text_rect = text.get_rect(midleft=(opt_rect.left + 10, opt_rect.centery))
                screen.blit(text, text_rect)
                
    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            if self.is_open:
                opt_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, len(self.options) * self.option_height)
                if opt_rect.collidepoint(event.pos):
                    y = (event.pos[1] - self.rect.bottom) // self.option_height
                    if 0 <= y < len(self.options):
                        self.hover_index = y
                        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_open = not self.is_open
            elif self.is_open:
                clicked = False
                for i in range(len(self.options)):
                    opt_rect = pygame.Rect(self.rect.x, self.rect.bottom + i * self.option_height, self.rect.width, self.option_height)
                    if opt_rect.collidepoint(event.pos):
                        self.selected_index = i
                        self.is_open = False
                        if self.callback:
                            self.callback(self.options[i])
                        clicked = True
                        break
                if not clicked:
                    self.is_open = False
                        
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_open and not self.rect.collidepoint(event.pos):
                opt_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, len(self.options) * self.option_height)
                if not opt_rect.collidepoint(event.pos):
                    self.is_open = False


class ScrollableTextBox:
    """带滚动条的只读文本框组件"""
    def __init__(self, x, y, width, height, font_size=FONT_SMALL, text_color=None, bg_color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.font_size = font_size
        self.text_color = text_color or COLORS['TEXT_LIGHT']
        self.bg_color = bg_color or COLORS['BG']
        self.text_lines = []  # [(text, color, font_size, is_header), ...]
        self.scroll_y = 0
        self.scrollbar_width = 12
        self.is_dragging = False
        self.drag_start_y = 0
        self.drag_start_scroll = 0
        
    def set_text_lines(self, lines_data):
        """设置文本内容 [(text, color, font_size, is_header), ...]"""
        self.text_lines = lines_data
        
        # 计算总高度 - 使用和draw方法一致的计算方式
        total_height = 0
        for text, color, font_size, is_header in self.text_lines:
            h = font_size + 15  # 与draw中的line_height一致
            total_height += h
        self.max_scroll = max(0, total_height - self.rect.height + 30)
        
    def set_text(self, text):
        """设置纯文本内容（简单模式）"""
        lines = text.split('\n')
        self.text_lines = []
        for line in lines:
            if line.startswith('==') and line.endswith('=='):
                # 标题行
                clean_text = line[2:-2]
                self.text_lines.append((clean_text, COLORS['GREEN'], self.font_size + 12, True))
            else:
                self.text_lines.append((line, COLORS['TEXT_LIGHT'], self.font_size, False))
        
        # 计算最大滚动值
        total_height = 0
        for text, color, font_size, is_header in self.text_lines:
            h = font_size + 15
            total_height += h
        self.max_scroll = max(0, total_height - self.rect.height + 30)
        
    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y = max(0, min(self.max_scroll, self.scroll_y - event.y * 30))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = getattr(event, 'pos', (0, 0))
            # 检查是否点击了滚动条
            scrollbar_rect = pygame.Rect(
                self.rect.right - self.scrollbar_width,
                self.rect.top,
                self.scrollbar_width,
                self.rect.height
            )
            if scrollbar_rect.collidepoint(pos):
                self.is_dragging = True
                self.drag_start_y = pos[1]
                self.drag_start_scroll = self.scroll_y
            elif self.rect.collidepoint(pos):
                # 点击文本区域也允许滚动
                self.is_dragging = True
                self.drag_start_y = pos[1]
                self.drag_start_scroll = self.scroll_y
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                delta = self.drag_start_y - event.pos[1]
                new_scroll = self.drag_start_scroll + delta * 2
                self.scroll_y = max(0, min(self.max_scroll, new_scroll))
    
    def draw(self, screen):
        """绘制文本框"""
        # 背景
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, COLORS['TEXT_DARK'], self.rect, 2, border_radius=8)
        
        # 裁剪区域
        clip_rect = pygame.Rect(
            self.rect.left + 4,
            self.rect.top + 4,
            self.rect.width - self.scrollbar_width - 8,
            self.rect.height - 8
        )
        screen.set_clip(clip_rect)
        
        # 绘制文本 - 整齐布局，使用累积高度
        y = self.rect.top + 15 - self.scroll_y
        
        for text, color, font_size, is_header in self.text_lines:
            line_height = font_size + 15
            
            # 检查是否在可视区域内
            if y + font_size < self.rect.top or y > self.rect.bottom:
                y += line_height  # 仍然累积高度
                continue
                
            font = get_font(font_size)
            
            # 标题行靠左空2格，普通行靠左空3格
            if is_header:
                x_offset = 25
            else:
                x_offset = 45
                # 如果是空行，保持空白
                if text.strip() == "":
                    y += line_height
                    continue
                # 普通行前面加"◇"符号
                text = "◇ " + text
            
            text_surface = font.render(text, True, color)
            screen.blit(text_surface, (self.rect.left + x_offset, y))
            y += line_height
        
        # 取消裁剪
        screen.set_clip(None)
        
        # 绘制滚动条
        if self.max_scroll > 0:
            scrollbar_x = self.rect.right - self.scrollbar_width
            scrollbar_height = self.rect.height - 8
            
            # 滚动条背景
            pygame.draw.rect(screen, COLORS['TEXT_DARK'], 
                (scrollbar_x, self.rect.top + 4, self.scrollbar_width, scrollbar_height),
                border_radius=6)
            
            # 计算滚动滑块位置
            thumb_height = max(30, int(scrollbar_height * self.rect.height / (self.max_scroll + self.rect.height)))
            scroll_ratio = self.scroll_y / self.max_scroll
            thumb_y = self.rect.top + 4 + int((scrollbar_height - thumb_height) * scroll_ratio)
            
            # 滚动滑块
            pygame.draw.rect(screen, COLORS['TEXT_LIGHT'], 
                (scrollbar_x + 2, thumb_y, self.scrollbar_width - 4, thumb_height),
                border_radius=4)
            
            # 上箭头
            arrow_y = self.rect.top + 8
            pygame.draw.polygon(screen, COLORS['TEXT_LIGHT'], [
                (scrollbar_x + self.scrollbar_width // 2, arrow_y + 5),
                (scrollbar_x + 2, arrow_y + 12),
                (scrollbar_x + self.scrollbar_width - 2, arrow_y + 12),
            ])
            # 下箭头
            arrow_y = self.rect.bottom - 8
            pygame.draw.polygon(screen, COLORS['TEXT_LIGHT'], [
                (scrollbar_x + self.scrollbar_width // 2, arrow_y - 5),
                (scrollbar_x + 2, arrow_y - 12),
                (scrollbar_x + self.scrollbar_width - 2, arrow_y - 12),
            ])