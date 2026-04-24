"""
数据库层 - 使用SQLite存储游戏数据
"""
import sqlite3
import os
from config import DB_PATH


class Database:
    """数据库操作类（单例模式）"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.conn = None
        self._statements = {}  # 预编译SQL语句缓存
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        db_dir = os.path.dirname(DB_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        self._connect()
        self._create_tables()

    def _connect(self):
        """连接数据库"""
        if self.conn is None:
            self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA journal_mode=WAL")
            self.conn.execute("PRAGMA synchronous=NORMAL")
            self.conn.execute("PRAGMA cache_size=-64000")  # 64MB缓存

    def _get_statement(self, sql):
        """获取预编译SQL语句（带缓存）"""
        if sql not in self._statements:
            self._statements[sql] = self.conn.prepare(sql)
        return self._statements[sql]

    def _create_tables(self):
        """创建表"""
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS high_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_name TEXT NOT NULL,
                player_name TEXT NOT NULL,
                score INTEGER NOT NULL,
                time_used INTEGER DEFAULT 0,
                difficulty TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_name TEXT NOT NULL UNIQUE,
                level INTEGER DEFAULT 1,
                data TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        # 创建索引（如果不存在）
        try:
            self.conn.execute('CREATE INDEX IF NOT EXISTS idx_scores_game_diff ON high_scores(game_name, difficulty)')
            self.conn.execute('CREATE INDEX IF NOT EXISTS idx_scores_time ON high_scores(time_used ASC)')
        except sqlite3.OperationalError:
            pass  # 索引已存在
        self.conn.commit()

    def save_score(self, game_name, player_name, score=0, time_used=None, difficulty=None):
        """保存分数"""
        if time_used is not None:
            score = max(0, 10000 - time_used * 10)
        self.conn.execute(
            'INSERT INTO high_scores (game_name, player_name, score, time_used, difficulty) VALUES (?, ?, ?, ?, ?)',
            (game_name, player_name, score, time_used, difficulty)
        )
        self.conn.commit()

    def get_top_scores(self, game_name, limit=10, difficulty=None):
        """获取最高分"""
        if difficulty:
            cursor = self.conn.execute(
                'SELECT * FROM high_scores WHERE game_name = ? AND difficulty = ? ORDER BY time_used ASC LIMIT ?',
                (game_name, difficulty, limit)
            )
        else:
            cursor = self.conn.execute(
                'SELECT * FROM high_scores WHERE game_name = ? ORDER BY time_used ASC LIMIT ?',
                (game_name, limit)
            )
        return [dict(row) for row in cursor.fetchall()]

    def get_setting(self, key, default=None):
        """获取设置"""
        cursor = self.conn.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        return row['value'] if row else default

    def save_setting(self, key, value):
        """保存设置"""
        self.conn.execute(
            'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
            (key, str(value))
        )
        self.conn.commit()

    def save_progress(self, game_name, level, data):
        """保存进度（upsert模式）"""
        self.conn.execute(
            'INSERT INTO progress (game_name, level, data, updated_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP) '
            'ON CONFLICT(game_name) DO UPDATE SET level=excluded.level, data=excluded.data, updated_at=CURRENT_TIMESTAMP',
            (game_name, level, data)
        )
        self.conn.commit()

    def get_progress(self, game_name):
        """获取进度"""
        cursor = self.conn.execute('SELECT * FROM progress WHERE game_name = ?', (game_name,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def delete_zero_scores(self, game_name):
        """删除时间为0的记录"""
        self.conn.execute('DELETE FROM high_scores WHERE game_name = ? AND time_used = 0', (game_name,))
        self.conn.commit()

    def clear_game_scores(self, game_name):
        """清空游戏排行榜"""
        self.conn.execute('DELETE FROM high_scores WHERE game_name = ?', (game_name,))
        self.conn.commit()

    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self._statements.clear()


# 全局数据库实例
db = Database()