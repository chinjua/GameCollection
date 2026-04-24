"""
游戏合集主程序
包含主菜单和各游戏入口
"""
import pygame
import sys
import os
from config import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, get_font
from ui import Button, Dropdown, draw_gradient_background, draw_decorative_circle, ScrollableTextBox
from lang import get_text, set_lang, get_available_langs, LANG_NAMES, get_lang

# 初始化pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(get_text('app_title'))
clock = pygame.time.Clock()

# 游戏状态
STATE_MENU = 'menu'
STATE_GAME = 'game'

# 主菜单按钮配置
MENU_BUTTONS_CONFIG = [
    ('minesweeper', COLORS['RED'], 'minesweeper'),
    ('sudoku', COLORS['BLUE'], 'sudoku'),
    ('tetris', COLORS['PURPLE'], 'tetris'),
    ('maze', COLORS['GREEN'], 'maze'),
    ('snake', COLORS['ORANGE'], 'snake'),
    ('gomoku', COLORS['CYAN'], 'gomoku'),
    ('intl_chess', COLORS['BRASS'], 'chess'),
    ('help', COLORS['TEXT_GRAY'], 'show_help'),
    ('about', COLORS['TEXT_DARK'], 'show_about'),
    ('quit', COLORS['TEXT_DARK'], 'quit_game'),
]
MENU_BUTTON_START_Y = 130
MENU_BUTTON_GAP = 60
MENU_BUTTON_WIDTH = 200
MENU_BUTTON_HEIGHT = 50

# 关于窗口配置
ABOUT_WIN_WIDTH = 550
ABOUT_WIN_HEIGHT = 350
ABOUT_BTN_WIDTH = 150
ABOUT_BTN_HEIGHT = 35
ABOUT_CONTENT_Y_OFFSET = 65
ABOUT_VISIBLE_HEIGHT = 180
ABOUT_LINE_HEIGHT = 22

# 游戏类映射（延迟导入）
GAME_CLASSES = {}


class GameCollection:
    """游戏合集主程序"""
    
    def __init__(self):
        self.state = STATE_MENU
        self.current_game = None
        self.current_game_name = None
        self.showing_help = False
        self.showing_about = False
        self.about_current_page = 'author'
        self.protocol_scroll_y = 0
        self.update_scroll_y = 0
        self.help_scroll = 0
        self._help_lang = None
        self._menu_buttons = None
        
        # 语言下拉列表
        lang_options = [(LANG_NAMES[l], l) for l in get_available_langs()]
        self.lang_dropdown = Dropdown(
            SCREEN_WIDTH - 120, 15, 110, 35,
            lang_options,
            callback=self.on_lang_changed
        )
        for i, (name, code) in enumerate(lang_options):
            if code == get_lang():
                self.lang_dropdown.selected_index = i
                break
        
        self._create_menu_buttons()
    
    def _get_game_class(self, game_name):
        """延迟加载游戏类"""
        if game_name not in GAME_CLASSES:
            from games import Minesweeper, Sudoku, Tetris, Maze, Snake, Gomoku, InternationalChess
            GAME_CLASSES.update({
                'minesweeper': Minesweeper,
                'sudoku': Sudoku,
                'tetris': Tetris,
                'maze': Maze,
                'snake': Snake,
                'gomoku': Gomoku,
                'chess': InternationalChess,
            })
        return GAME_CLASSES[game_name]
    
    def _create_menu_buttons(self):
        """创建主菜单按钮"""
        self._menu_buttons = []
        for i, (text_key, color, callback_name) in enumerate(MENU_BUTTONS_CONFIG):
            y = MENU_BUTTON_START_Y + i * MENU_BUTTON_GAP
            if callback_name in ('show_help', 'show_about', 'quit_game'):
                callback = getattr(self, callback_name)
            else:
                callback = lambda name=callback_name: self._start_game(name)
            btn = Button(
                SCREEN_WIDTH // 2 - MENU_BUTTON_WIDTH // 2, y,
                MENU_BUTTON_WIDTH, MENU_BUTTON_HEIGHT,
                get_text(text_key), color,
                callback=callback
            )
            self._menu_buttons.append(btn)
    
    @property
    def menu_buttons(self):
        """按钮属性，动态更新"""
        return self._menu_buttons
    
    def _get_base_dir(self):
        """获取基础目录，兼容 PyInstaller"""
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))
    
    def load_update_log(self):
        """从文件加载更新日志"""
        update_file = os.path.join(self._get_base_dir(), 'update_log.txt')
        if os.path.exists(update_file):
            with open(update_file, 'r', encoding='utf-8') as f:
                return [line.rstrip('\n\r') for line in f.readlines()]
        return []
    
    def _start_game(self, game_name):
        """启动游戏（通用方法）"""
        game_class = self._get_game_class(game_name)
        self.current_game = game_class(screen)
        self.current_game_name = game_name
        self.state = STATE_GAME

    def show_help(self):
        """显示帮助"""
        self.showing_help = True
        self.help_scroll = 0
        
    def show_about(self):
        """显示关于"""
        self.showing_about = True
        
    def quit_game(self):
        """退出游戏"""
        pygame.quit()
        sys.exit()
        
    def change_lang(self, lang):
        """切换语言"""
        set_lang(lang)
        self._create_menu_buttons()
        
    def on_lang_changed(self, option):
        """语言下拉列表选择回调"""
        self.change_lang(option[1])
        
    def handle_menu_events(self, events):
        """处理菜单事件"""
        for event in events:
            if not (self.showing_about or self.showing_help):
                for button in self.menu_buttons:
                    button.handle_event(event)
            self.lang_dropdown.handle_event(event)
                
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.quit_game()
                    
    def draw_menu(self):
        """绘制主菜单"""
        draw_gradient_background(screen)
        
        # 装饰性圆形
        draw_decorative_circle(screen, 100, 100, 80, COLORS['BLUE_NEON'], 25)
        draw_decorative_circle(screen, SCREEN_WIDTH - 100, 500, 60, COLORS['PURPLE_NEON'], 20)
        draw_decorative_circle(screen, 150, 450, 40, COLORS['GREEN_NEON'], 15)
        
        # 主标题 - 带发光效果
        font = get_font(56)
        for i in range(3):
            alpha = 60 - i * 18
            title_surf = font.render(get_text('title'), True, (*COLORS['BLUE_NEON'], alpha))
            rect = title_surf.get_rect(center=(SCREEN_WIDTH//2, 80 - i * 2))
            screen.blit(title_surf, rect)
        
        # 主体标题
        title = font.render(get_text('title'), True, COLORS['TEXT_LIGHT'])
        rect = title.get_rect(center=(SCREEN_WIDTH//2, 80))
        screen.blit(title, rect)
        
        # 副标题
        font = get_font(22)
        subtitle = font.render(get_text('subtitle'), True, COLORS['TEXT_GRAY'])
        rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, 125))
        screen.blit(subtitle, rect)
        
        # 绘制按钮
        for button in self.menu_buttons:
            button.draw(screen)
            
        # 绘制语言下拉列表
        self.lang_dropdown.draw(screen)
            
    def handle_game_events(self, events):
        """处理游戏事件"""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and self.current_game:
                if self.current_game_name == 'minesweeper':
                    self.current_game.handle_click(event.pos, event.button)
                else:
                    self.current_game.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.return_to_menu()
                elif self.current_game:
                    if self.current_game_name == 'maze':
                        if hasattr(self.current_game, 'handle_key_down'):
                            self.current_game.handle_key_down(event.key)
                    elif event.key == pygame.K_p and self.current_game_name in ('tetris', 'maze', 'minesweeper', 'sudoku', 'snake', 'gomoku', 'puzzle', 'chess'):
                        self.current_game.handle_key(pygame.K_p)
                    elif hasattr(self.current_game, 'handle_key'):
                        self.current_game.handle_key(event.key)
            elif event.type == pygame.KEYUP:
                if self.current_game and self.current_game_name == 'maze':
                    if hasattr(self.current_game, 'handle_key_up'):
                        self.current_game.handle_key_up(event.key)
                        
    def draw_game(self):
        """绘制游戏"""
        if self.current_game:
            self.current_game.draw()
            self._draw_back_button()
            
    def _draw_back_button(self):
        """绘制返回按钮"""
        pygame.draw.rect(screen, COLORS['RED'], (10, 10, 100, 35), border_radius=5)
        font = get_font(24)
        text = font.render("< " + get_text('back'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(55, 27))
        screen.blit(text, text_rect)
        
    def return_to_menu(self):
        """返回菜单"""
        self.state = STATE_MENU
        self.current_game = None
        
    def update(self):
        """更新游戏"""
        if self.current_game and hasattr(self.current_game, 'update'):
            self.current_game.update()
    
    def run(self):
        """主循环"""
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and self.state == STATE_GAME:
                    x, y = event.pos
                    if 10 <= x <= 90 and 10 <= y <= 45:
                        self.return_to_menu()
            
            if self.state == STATE_MENU:
                if self.showing_about:
                    self._draw_about()
                    self._handle_about_events(events)
                else:
                    self.handle_menu_events(events)
                    self.draw_menu()
                if self.showing_help:
                    self._draw_help()
            elif self.state == STATE_GAME:
                self.handle_game_events(events)
                self.update()
                self.draw_game()
            
            pygame.display.flip()
            clock.tick(60)
    
    def _handle_about_events(self, events):
        """处理关于窗口事件"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.showing_about = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                btn_y = self.about_win_y + 15
                if btn_y <= y <= btn_y + ABOUT_BTN_HEIGHT:
                    total_btn_width = 3 * ABOUT_BTN_WIDTH + 20
                    start_x = self.about_win_x + (ABOUT_WIN_WIDTH - total_btn_width) // 2
                    buttons = [
                        (start_x, 'author'),
                        (start_x + ABOUT_BTN_WIDTH + 10, 'protocol'),
                        (start_x + 2 * (ABOUT_BTN_WIDTH + 10), 'update'),
                    ]
                    for bx, page in buttons:
                        if bx <= x <= bx + ABOUT_BTN_WIDTH:
                            self.about_current_page = page
                            break
                close_y = self.about_win_y + ABOUT_WIN_HEIGHT - 60
                if self.about_win_x + ABOUT_WIN_WIDTH // 2 - 60 <= x <= self.about_win_x + ABOUT_WIN_WIDTH // 2 + 60 and close_y <= y <= close_y + 40:
                    self.showing_about = False
            elif event.type == pygame.MOUSEWHEEL:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                content_y = self.about_win_y + ABOUT_CONTENT_Y_OFFSET
                if self.about_win_x + 20 <= mouse_x <= self.about_win_x + ABOUT_WIN_WIDTH - 30 and content_y <= mouse_y <= content_y + ABOUT_VISIBLE_HEIGHT:
                    scroll_lines = 19 if self.about_current_page == 'update' else 21
                    max_scroll = max(0, scroll_lines * ABOUT_LINE_HEIGHT - ABOUT_VISIBLE_HEIGHT)
                    if self.about_current_page == 'protocol':
                        self.protocol_scroll_y = max(0, min(max_scroll, self.protocol_scroll_y - event.y * 30))
                    elif self.about_current_page == 'update':
                        self.update_scroll_y = max(0, min(max_scroll, self.update_scroll_y - event.y * 30))
    
    def _draw_about_page_content(self, content_y):
        """绘制关于窗口页面内容"""
        font = get_font(16)
        
        if self.about_current_page == 'author':
            lines = [
                f"{get_text('author')}: 天涯客", "",
                "Email: 774667285@qq.com", "",
                f"{get_text('blog')}: https://www.chinjua.com.cn/", "",
                f"{get_text('project_url')}: https://github.com/chinjua/GameCollection",
            ]
            for i, line in enumerate(lines):
                text = font.render(line, True, COLORS['TEXT_LIGHT'])
                screen.blit(text, (self.about_win_x + 30, content_y + i * 30))
        else:
            lines = self._get_scrollable_content()
            total_height = len(lines) * ABOUT_LINE_HEIGHT
            max_scroll = max(0, total_height - ABOUT_VISIBLE_HEIGHT)
            
            clip_rect = pygame.Rect(self.about_win_x + 20, content_y, ABOUT_WIN_WIDTH - 50, ABOUT_VISIBLE_HEIGHT)
            screen.set_clip(clip_rect)
            
            font = get_font(14)
            scroll_y = self.protocol_scroll_y if self.about_current_page == 'protocol' else self.update_scroll_y
            y = content_y - scroll_y
            for line in lines:
                if content_y <= y <= content_y + ABOUT_VISIBLE_HEIGHT + ABOUT_LINE_HEIGHT:
                    text = font.render(line, True, COLORS['TEXT_LIGHT'])
                    screen.blit(text, (self.about_win_x + 30, y))
                y += ABOUT_LINE_HEIGHT
            
            screen.set_clip(None)
            
            if max_scroll > 0:
                self._draw_scrollbar(content_y, total_height, max_scroll, scroll_y)
    
    def _get_scrollable_content(self):
        """获取可滚动内容"""
        if self.about_current_page == 'protocol':
            return [
                "MIT License", "",
                "Permission is hereby granted, free of charge,", "to any person obtaining a copy of this software",
                "and associated documentation files (the 'Software'),", "to deal in the Software without restriction,",
                "including without limitation the rights to use, copy,", "modify, merge, publish, distribute, sublicense,",
                "and/or sell copies of the Software, and to permit", "persons to whom the Software is furnished to do so,",
                "subject to the following conditions:", "",
                "The above copyright notice and this permission", "notice shall be included in all copies or",
                "substantial portions of the Software.", "",
                "THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT", "WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,",
                "INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF", "MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE",
                "AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS", "OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,",
                "DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION", "OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,",
                "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE", "USE OR OTHER DEALINGS IN THE SOFTWARE.",
            ]
        else:
            try:
                return self.load_update_log()
            except Exception as e:
                return [f"Error: {str(e)}"]
    
    def _draw_scrollbar(self, content_y, total_height, max_scroll, current_scroll):
        """绘制滚动条"""
        scrollbar_x = self.about_win_x + ABOUT_WIN_WIDTH - 30
        pygame.draw.rect(screen, COLORS['TEXT_DARK'], (scrollbar_x, content_y, 12, ABOUT_VISIBLE_HEIGHT), border_radius=6)
        thumb_height = max(30, int(ABOUT_VISIBLE_HEIGHT * ABOUT_VISIBLE_HEIGHT / total_height))
        scroll_ratio = current_scroll / max_scroll
        thumb_y = content_y + int((ABOUT_VISIBLE_HEIGHT - thumb_height) * scroll_ratio)
        pygame.draw.rect(screen, COLORS['TEXT_LIGHT'], (scrollbar_x + 2, thumb_y, 8, thumb_height), border_radius=4)
            
    def _draw_help(self):
        """绘制帮助界面"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(240)
        overlay.fill((30, 41, 55))
        screen.blit(overlay, (0, 0))
        
        font = get_font(48)
        title = font.render(get_text('help_title'), True, COLORS['TEXT_LIGHT'])
        rect = title.get_rect(center=(SCREEN_WIDTH//2, 60))
        screen.blit(title, rect)
        
        help_content_lines = [
            (get_text('title'), COLORS['GREEN'], 28, True),
            (get_text('game_intro'), COLORS['TEXT_GRAY'], 18, False),
            ("", COLORS['TEXT_GRAY'], 18, False),
            (get_text('minesweeper'), COLORS['GREEN'], 28, True),
            (get_text('minesweeper_desc'), COLORS['TEXT_GRAY'], 18, False),
            (get_text('minesweeper_goal'), COLORS['TEXT_GRAY'], 18, False),
            ("", COLORS['TEXT_GRAY'], 18, False),
            (get_text('sudoku'), COLORS['GREEN'], 28, True),
            (get_text('sudoku_desc'), COLORS['TEXT_GRAY'], 18, False),
            (get_text('sudoku_goal'), COLORS['TEXT_GRAY'], 18, False),
            ("", COLORS['TEXT_GRAY'], 18, False),
            (get_text('tetris'), COLORS['GREEN'], 28, True),
            (get_text('tetris_desc'), COLORS['TEXT_GRAY'], 18, False),
            (get_text('tetris_goal'), COLORS['TEXT_GRAY'], 18, False),
            ("", COLORS['TEXT_GRAY'], 18, False),
            (get_text('maze'), COLORS['GREEN'], 28, True),
            (get_text('maze_desc'), COLORS['TEXT_GRAY'], 18, False),
            (get_text('maze_goal'), COLORS['TEXT_GRAY'], 18, False),
            ("", COLORS['TEXT_GRAY'], 18, False),
            (get_text('snake'), COLORS['GREEN'], 28, True),
            (get_text('snake_desc'), COLORS['TEXT_GRAY'], 18, False),
            (get_text('snake_goal'), COLORS['TEXT_GRAY'], 18, False),
            ("", COLORS['TEXT_GRAY'], 18, False),
            (get_text('gomoku'), COLORS['GREEN'], 28, True),
            (get_text('gomoku_desc'), COLORS['TEXT_GRAY'], 18, False),
            (get_text('gomoku_goal'), COLORS['TEXT_GRAY'], 18, False),
            ("", COLORS['TEXT_GRAY'], 18, False),
            (get_text('intl_chess'), COLORS['GREEN'], 28, True),
            (get_text('intl_chess_desc'), COLORS['TEXT_GRAY'], 18, False),
            (get_text('intl_chess_goal'), COLORS['TEXT_GRAY'], 18, False),
            ("", COLORS['TEXT_GRAY'], 18, False),
            (get_text('general'), COLORS['GREEN'], 28, True),
            (get_text('esc_return'), COLORS['TEXT_GRAY'], 18, False),
        ]
        
        if not hasattr(self, 'help_textbox') or self._help_lang != get_lang():
            self._help_lang = get_lang()
            self.help_textbox = ScrollableTextBox(50, 100, SCREEN_WIDTH - 120, SCREEN_HEIGHT - 180, font_size=18)
            self.help_textbox.set_text_lines(help_content_lines)
        
        self.help_textbox.draw(screen)
        
        font = get_font(24)
        text = font.render(get_text('press_esc'), True, COLORS['TEXT_LIGHT'])
        rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 40))
        screen.blit(text, rect)
        
        for event in pygame.event.get([pygame.MOUSEWHEEL, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION]):
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.showing_help = False
            try:
                self.help_textbox.handle_event(event)
            except:
                pass
    
    def _draw_about(self):
        """绘制关于界面"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(240)
        overlay.fill((30, 41, 55))
        screen.blit(overlay, (0, 0))
        
        self.about_win_x = (SCREEN_WIDTH - ABOUT_WIN_WIDTH) // 2
        self.about_win_y = (SCREEN_HEIGHT - ABOUT_WIN_HEIGHT) // 2
        
        pygame.draw.rect(screen, COLORS['PANEL'], (self.about_win_x, self.about_win_y, ABOUT_WIN_WIDTH, ABOUT_WIN_HEIGHT), border_radius=15)
        pygame.draw.rect(screen, COLORS['BLUE'], (self.about_win_x, self.about_win_y, ABOUT_WIN_WIDTH, ABOUT_WIN_HEIGHT), 2, border_radius=15)
        
        btn_y = self.about_win_y + 15
        total_btn_width = 3 * ABOUT_BTN_WIDTH + 20
        start_x = self.about_win_x + (ABOUT_WIN_WIDTH - total_btn_width) // 2
        
        font = get_font(14)
        buttons_info = [
            (start_x, 'author', get_text('author')),
            (start_x + ABOUT_BTN_WIDTH + 10, 'protocol', get_text('protocol')),
            (start_x + 2 * (ABOUT_BTN_WIDTH + 10), 'update', get_text('update')),
        ]
        
        for bx, page, label in buttons_info:
            color = COLORS['BLUE'] if self.about_current_page == page else COLORS['TEXT_DARK']
            pygame.draw.rect(screen, color, (bx, btn_y, ABOUT_BTN_WIDTH, ABOUT_BTN_HEIGHT), border_radius=8)
            text = font.render(label, True, COLORS['TEXT_LIGHT'])
            text_rect = text.get_rect(center=(bx + ABOUT_BTN_WIDTH // 2, btn_y + ABOUT_BTN_HEIGHT // 2))
            screen.blit(text, text_rect)
        
        content_y = btn_y + ABOUT_BTN_HEIGHT + 30
        self._draw_about_page_content(content_y)
        
        close_y = self.about_win_y + ABOUT_WIN_HEIGHT - 60
        pygame.draw.rect(screen, COLORS['RED'], (self.about_win_x + ABOUT_WIN_WIDTH // 2 - 60, close_y, 120, 40), border_radius=8)
        font = get_font(20)
        text = font.render(get_text('back'), True, COLORS['TEXT_LIGHT'])
        text_rect = text.get_rect(center=(self.about_win_x + ABOUT_WIN_WIDTH // 2, close_y + 20))
        screen.blit(text, text_rect)


if __name__ == '__main__':
    game = GameCollection()
    game.run()