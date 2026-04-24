"""
多语言支持模块
支持：简体中文、繁体中文、English
"""

# 当前语言 (可设置为 'zh_CN', 'zh_TW', 'en')
CURRENT_LANG = 'zh_CN'  # 默认简体中文

# 语言名称显示
LANG_NAMES = {
    'zh_CN': '简体中文',
    'zh_TW': '繁体中文',
    'en': 'English'
}

# 所有语言文本
LANG_DATA = {
    'zh_CN': {
        # 应用标题
        'app_title': '单机游戏合集v0.1',
        
        # 主菜单
        'title': '游戏合集',
        'subtitle': '',
        'about': '关于',
        'minesweeper': '扫雷',
        'sudoku': '数独',
        'tetris': '俄罗斯方块',
        'maze': '迷宫',
        'snake': '贪吃蛇',
        'gomoku': '五子棋',
        'intl_chess': '国际象棋',
        'puzzle': '拼图',
        'help': '帮助',
        'quit': '退出',
        
        # 通用
        'back': '返回',
        'pause': '暂停',
        'resume': '继续',
        'game_over': '游戏结束',
        'you_win': '胜利!',
        
        # 扫雷
        'mines': '剩余地雷',
        'time': '时间',
        'seconds': '秒',
        'game_over_text': '游戏结束',
        
        # 数独
        'selected': '选择',
        'row': '行',
        'col': '列',
        'complete': '完成!',
        
        # 俄罗斯方块
        'score': '分数',
        'level': '等级',
        'lines': '行数',
        'next': '下一个',
        
        # 迷宫
        'maze': '迷宫',
        'moves': '步数',
        'top_scores': '最快通关',
        'no_records': '暂无记录',
        
        # 操作说明
        'rotate': '旋转',
        'drop': '下降',
        'fast_drop': '快速下落',
        'move_lr': '左右移动',
        
        # 帮助
        'help_title': '帮助',
        'game_intro': '多款经典小游戏合集',
        'minesweeper_desc': '左键点击揭开格子，右键标记地雷',
        'minesweeper_goal': '找出所有地雷即可获胜',
        'sudoku_desc': '鼠标选择格子，键盘输入1-9',
        'sudoku_goal': '使每行、每列、每宫都包含1-9',
        'tetris_desc': '方向键移动/旋转，空格快速下落',
        'tetris_goal': '消除满行得分，升级加快速度',
        'maze_desc': '方向键控制移动，找到出口',
        'maze_goal': '用最短路径到达出口',
        'snake_desc': '方向键控制移动，吃食物变长',
        'snake_goal': '吃到更多食物，避开障碍',
        'gomoku_desc': '鼠标点击落子，五子连珠获胜',
        'gomoku_goal': '黑白交替落子，先连五子获胜',
        'intl_chess_desc': '鼠标点击移动棋子，将死对方获胜',
        'intl_chess_goal': '吃掉对方王即获胜',
        'general': '通用',
        'esc_return': 'ESC 返回菜单',
        'press_esc': '按 ESC 关闭',
        
        # 按钮
        'new_game': '新游戏',
        'current_player': '当前玩家',
        'easy': '简单',
        'medium': '中等',
        'hard': '困难',
        'very_hard': '极难',
        'impossible': '不可能',
        'difficulty': '难度',
        'controls': '操作说明',
        'input_number': '输入数字',
        'clear_cell': '清空格子',
        'arrows': '方向键',
        'move': '移动',
        'solve': '解决',
        'clear': '清空',
        'clear_records': '清空记录',
        'custom': '自定义',
        
        # 五子棋右侧面板
        'ai_mode': 'AI模式',
        'your_turn': '你的回合',
        'computer_thinking': '电脑思考中',
        'result': '结果',
        'you_win_label': '你获胜',
        'computer_wins': '电脑获胜',
        'mouse_place': '鼠标: 落子',
        'pause_game': 'P: 暂停',
        'game_paused': '暂停中',
        'you': '你',
        'black': '执黑',
        'white': '执白',
        
        # 国际象棋右侧面板
        'chess_ai_mode': 'AI模式',
        'chess_your_turn': '你的回合',
        'chess_computer': '电脑',
        'click_piece': '点击: 选择棋子',
        'click_destination': '点击: 移动位置',
        'captured': '吃子',
        'none': '无',
        'first': '先',
        
        # 帮助页面滚动条
        'scroll_up': '上滚',
        'scroll_down': '下滚',
        
        # 关于页面
        'about_title': '关于',
        'author': '作者',
        'author_name': '单机游戏开发者',
        'protocol': '协议',
        'protocol_name': 'MIT License',
        'update': '更新',
        'update_info': 'v0.1 - 初始版本',
        'blog': '博客',
        'project_url': '项目地址',
    },
    
    'zh_TW': {
        # 應用標題
        'app_title': '單機遊戲合集v0.1',
        
        # 主菜單
        'title': '遊戲合集',
        'subtitle': '',
        'about': '關於',
        'minesweeper': '踩地雷',
        'sudoku': '數独',
        'tetris': '俄羅斯方塊',
        'maze': '迷宮',
        'snake': '貪吃蛇',
        'gomoku': '五子棋',
        'intl_chess': '國際象棋',
        'puzzle': '拼圖',
        'help': '説明',
        'quit': '退出',
        
        # 通用
        'back': '返回',
        'pause': '暫停',
        'resume': '繼續',
        'game_over': '遊戲結束',
        'you_win': '勝利!',
        
        # 掃雷
        'mines': '剩餘地雷',
        'time': '時間',
        'seconds': '秒',
        'game_over_text': '遊戲結束',
        
        # 數独
        'selected': '選擇',
        'row': '行',
        'col': '列',
        'complete': '完成!',
        
        # 俄羅斯方塊
        'score': '分數',
        'level': '等級',
        'lines': '行數',
        'next': '下一個',
        
        # 迷宫
        'maze': '迷宫',
        'moves': '步数',
        'top_scores': '最快通關',
        'no_records': '暫無記錄',
        
        # 操作説明
        'rotate': '旋轉',
        'drop': '下降',
        'fast_drop': '快速下落',
        'move_lr': '左右移動',
        
        # 帮助
        'help_title': '説明',
        'game_intro': '多款經典小遊戲合集',
        'minesweeper_desc': '左鍵點擊揭開格子，右鍵標記地雷',
        'minesweeper_goal': '找出所有地雷即可獲勝',
        'sudoku_desc': '滑鼠選擇格子，鍵盤輸入1-9',
        'sudoku_goal': '使每行、每列、每宮都包含1-9',
        'tetris_desc': '方向鍵移動/旋轉，空格快速下落',
        'tetris_goal': '消除滿行得分，升級加快速度',
        'maze_desc': '方向鍵控制移動，找到出口',
        'maze_goal': '用最短路徑到達出口',
        'snake_desc': '方向鍵控制移動，吃食物變長',
        'snake_goal': '吃到更多食物，避開障礙',
        'gomoku_desc': '滑鼠點擊落子，五子連珠獲勝',
        'gomoku_goal': '黑白交替落子，先連五子獲勝',
        'intl_chess_desc': '滑鼠點擊移動棋子，將死對方獲勝',
        'intl_chess_goal': '吃掉對方王即獲勝',
        'general': '通用',
        'esc_return': 'ESC 返回菜單',
        'press_esc': '按 ESC 關閉',
        
        # 按鈕
        'new_game': '新遊戲',
        'current_player': '當前玩家',
        'easy': '簡單',
        'medium': '中等',
        'hard': '困難',
        'very_hard': '極難',
        'impossible': '不可能',
        'difficulty': '難度',
        'controls': '操作説明',
        'input_number': '輸入數字',
        'clear_cell': '清空格子',
        'arrows': '方向鍵',
        'move': '移動',
        'solve': '解決',
        'clear': '清空',
        'clear_records': '清空記錄',
        'custom': '自訂',
        
        # 五子棋右側面板
        'ai_mode': 'AI模式',
        'your_turn': '你的回合',
        'computer_thinking': '電腦思考中',
        'result': '結果',
        'you_win_label': '你獲勝',
        'computer_wins': '電腦獲勝',
        'mouse_place': '滑鼠: 落子',
        'pause_game': 'P: 暫停',
        'game_paused': '暫停中',
        'you': '你',
        'black': '執黑',
        'white': '執白',
        
        # 國際象棋右側面板
        'chess_ai_mode': 'AI模式',
        'chess_your_turn': '你的回合',
        'chess_computer': '電腦',
        'click_piece': '點擊: 選擇棋子',
        'click_destination': '點擊: 移動位置',
        'captured': '吃子',
        'none': '無',
        'first': '先',
        
        # 幫助頁面滾動條
        'scroll_up': '上滾',
        'scroll_down': '下滾',
        
        # 關於頁面
        'about_title': '關於',
        'author': '作者',
        'author_name': '單機遊戲開發者',
        'protocol': '協議',
        'protocol_name': 'MIT License',
        'update': '更新',
        'update_info': 'v0.1 - 初始版本',
        'blog': '部落格',
        'project_url': '專案地址',
    },
    
    'en': {
        # App Title
        'app_title': 'Standalone Games v0.1',
        
        # Main Menu
        'title': 'Game Collection',
        'subtitle': '',
        'about': 'About',
        'minesweeper': 'Minesweeper',
        'sudoku': 'Sudoku',
        'tetris': 'Tetris',
        'maze': 'Maze',
        'snake': 'Snake',
        'gomoku': 'Gomoku',
        'intl_chess': 'International Chess',
        'puzzle': 'Puzzle',
        'help': 'Help',
        'quit': 'Quit',
        
        # General
        'back': 'Back',
        'pause': 'Pause',
        'resume': 'Resume',
        'game_over': 'Game Over',
        'you_win': 'YOU WIN!',
        
        # Minesweeper
        'mines': 'Mines',
        'time': 'Time',
        'seconds': 's',
        'game_over_text': 'GAME OVER',
        
        # Sudoku
        'selected': 'Selected',
        'row': 'Row',
        'col': 'Col',
        'complete': 'COMPLETE!',
        
        # Tetris
        'score': 'Score',
        'level': 'Level',
        'lines': 'Lines',
        'next': 'Next',
        
        # Maze
        'maze': 'Maze',
        'moves': 'Moves',
        'top_scores': 'Best Time',
        'no_records': 'No records',
        
        # Controls
        'rotate': 'Rotate',
        'drop': 'Drop',
        'fast_drop': 'Fast Drop',
        'move_lr': 'Left/Right',
        
        # Help
        'help_title': 'Help',
        'game_intro': 'Collection of Classic Games',
        'minesweeper_desc': 'Left-click to reveal, Right-click to flag',
        'minesweeper_goal': 'Find all mines to win',
        'sudoku_desc': 'Mouse to select, Keys 1-9 to input',
        'sudoku_goal': 'Fill 1-9 in each row/col/box',
        'tetris_desc': 'Arrows to move/rotate, Space to drop',
        'tetris_goal': 'Clear lines to score, level up',
        'maze_desc': 'Arrows to move, find the exit',
        'maze_goal': 'Reach the exit in shortest path',
        'snake_desc': 'Arrows to move, eat food to grow',
        'snake_goal': 'Eat more food, avoid obstacles',
        'gomoku_desc': 'Click to place stone, five in a row wins',
        'gomoku_goal': 'Alternate black/white, first to five wins',
        'intl_chess_desc': 'Click to move pieces, checkmate to win',
        'intl_chess_goal': 'Capture the enemy king to win',
        'general': 'General',
        'esc_return': 'ESC to return to menu',
        'press_esc': 'Press ESC to close',
        
        # Buttons
        'new_game': 'New Game',
        'current_player': 'Current Player',
        'easy': 'Easy',
        'medium': 'Medium',
        'hard': 'Hard',
        'very_hard': 'Very Hard',
        'impossible': 'Impossible',
        'difficulty': 'Difficulty',
        'controls': 'Controls',
        'input_number': 'Input number',
        'clear_cell': 'Clear cell',
        'arrows': 'Arrows',
        'move': 'Move',
        'solve': 'Solve',
        'clear': 'Clear',
        'clear_records': 'Clear Records',
        'custom': 'Custom',
        
        # Gomoku right panel
        'ai_mode': 'AI Mode',
        'your_turn': 'Your Turn',
        'computer_thinking': 'Computer Thinking',
        'result': 'Result',
        'you_win_label': 'You Win',
        'computer_wins': 'Computer Wins',
        'mouse_place': 'Mouse: Place',
        'pause_game': 'P: Pause',
        'game_paused': 'Paused',
        'you': 'You',
        'black': 'Black',
        'white': 'White',
        
        # Chess right panel
        'chess_ai_mode': 'AI Mode',
        'chess_your_turn': 'Your Turn',
        'chess_computer': 'Computer',
        'click_piece': 'Click: Select',
        'click_destination': 'Click: Move',
        'captured': 'Captured',
        'none': 'None',
        'first': 'First',
        
        # Help page scrollbar
        'scroll_up': 'Scroll Up',
        'scroll_down': 'Scroll Down',
        
        # About page
        'about_title': 'About',
        'author': 'Author',
        'author_name': 'Game Developer',
        'protocol': 'Protocol',
        'protocol_name': 'MIT License',
        'update': 'Update',
        'update_info': 'v0.1 - Initial Version',
        'blog': 'Blog',
        'project_url': 'Project URL',
    }
}


def get_text(key):
    """获取当前语言的文本"""
    return LANG_DATA.get(CURRENT_LANG, LANG_DATA['en']).get(key, key)


def set_lang(lang_code):
    """设置语言"""
    global CURRENT_LANG
    if lang_code in LANG_DATA:
        CURRENT_LANG = lang_code


def get_lang():
    """获取当前语言代码"""
    return CURRENT_LANG


def get_available_langs():
    """获取所有可用语言"""
    return list(LANG_DATA.keys())