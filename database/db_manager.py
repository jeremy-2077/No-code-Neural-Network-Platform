import sqlite3
from typing import Dict, Any
import bcrypt
from .connection_pool import get_connection_pool
from utils.logger import logger, ErrorHandler


class DatabaseManager:
    def __init__(self, db_path: str = "neural_network.db"):
        self.db_path = db_path
        self.connection_pool = get_connection_pool(db_path)
        self.init_database()

    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 检查users表是否存在
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='users'
            """)
            if not cursor.fetchone():
                # 创建用户表
                cursor.execute('''
                    CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        created_at INTEGER DEFAULT (strftime('%s', 'now'))
                    )
                ''')

            # 检查models表是否存在
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='models'
            """)
            models_exists = cursor.fetchone()
            
            if models_exists:
                # 检查models表是否需要更新
                cursor.execute("PRAGMA table_info(models)")
                columns = [column[1] for column in cursor.fetchall()]

                if 'user_id' not in columns:
                    # 备份旧数据
                    cursor.execute("ALTER TABLE models RENAME TO models_old")

                    # 创建新的models表
                    cursor.execute('''
                        CREATE TABLE models (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            name TEXT NOT NULL,
                            architecture TEXT NOT NULL,
                            parameters TEXT NOT NULL,
                            created_at INTEGER DEFAULT (strftime('%s', 'now')),
                            FOREIGN KEY (user_id) REFERENCES users (id)
                        )
                    ''')

                    # 迁移旧数据（将user_id设为1）
                    cursor.execute("""
                        INSERT INTO models (user_id, name, architecture, parameters, created_at)
                        SELECT 1, name, architecture, parameters, created_at
                        FROM models_old
                    """)

                    # 删除旧表
                    cursor.execute("DROP TABLE models_old")
            else:
                # 创建新的models表
                cursor.execute('''
                    CREATE TABLE models (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        architecture TEXT NOT NULL,
                        parameters TEXT NOT NULL,
                        created_at INTEGER DEFAULT (strftime('%s', 'now')),
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')

            # 检查datasets表是否存在
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='datasets'
            """)
            datasets_exists = cursor.fetchone()
            
            if datasets_exists:
                # 检查datasets表是否需要更新
                cursor.execute("PRAGMA table_info(datasets)")
                columns = [column[1] for column in cursor.fetchall()]

                if 'user_id' not in columns:
                    # 备份旧数据
                    cursor.execute("ALTER TABLE datasets RENAME TO datasets_old")

                    # 创建新的datasets表
                    cursor.execute('''
                        CREATE TABLE datasets (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            name TEXT NOT NULL,
                            file_path TEXT NOT NULL,
                            preprocessing_params TEXT,
                            created_at INTEGER DEFAULT (strftime('%s', 'now')),
                            FOREIGN KEY (user_id) REFERENCES users (id)
                        )
                    ''')

                    # 迁移旧数据（将user_id设为1）
                    cursor.execute("""
                        INSERT INTO datasets (user_id, name, file_path, preprocessing_params, created_at)
                        SELECT 1, name, file_path, preprocessing_params, created_at
                        FROM datasets_old
                    """)

                    # 删除旧表
                    cursor.execute("DROP TABLE datasets_old")
            else:
                # 创建新的datasets表
                cursor.execute('''
                    CREATE TABLE datasets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        preprocessing_params TEXT,
                        created_at INTEGER DEFAULT (strftime('%s', 'now')),
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')

            conn.commit()

    def get_connection(self):
        """获取数据库连接（使用连接池）"""
        return self.connection_pool.get_connection_context()

    def get_all_models(self, user_id: int = None) -> list:
        """获取用户的所有已保存模型"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if user_id is not None:
                cursor.execute(
                    """
                    SELECT id, name, datetime(created_at, 'unixepoch', 'localtime') as created_time
                    FROM models 
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    """,
                    (user_id,)
                )
            else:
                cursor.execute(
                    """
                    SELECT id, name, datetime(created_at, 'unixepoch', 'localtime') as created_time
                    FROM models 
                    ORDER BY created_at DESC
                    """
                )
            return cursor.fetchall()

    def get_model_by_id(self, model_id: int, user_id: int = None) -> dict:
        """根据ID获取模型，可选择验证用户所有权"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if user_id is not None:
                cursor.execute(
                    """
                    SELECT name, architecture, parameters 
                    FROM models 
                    WHERE id = ? AND user_id = ?
                    """,
                    (model_id, user_id)
                )
            else:
                cursor.execute(
                    """
                    SELECT name, architecture, parameters 
                    FROM models 
                    WHERE id = ?
                    """,
                    (model_id,)
                )
            result = cursor.fetchone()
            if result:
                return {
                    "name": result[0],
                    "architecture": result[1],
                    "parameters": result[2]
                }
            return None

    def add_user(self, username: str, password: str) -> bool:
        """添加新用户，密码将被安全哈希存储"""
        try:
            # 生成密码哈希
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, password_hash.decode('utf-8'))
                )
                return True
        except sqlite3.IntegrityError:
            return False

    def verify_user(self, username: str, password: str) -> tuple:
        """验证用户登录，使用安全的密码哈希验证"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, password FROM users WHERE username = ?",
                (username,)
            )
            result = cursor.fetchone()
            
            if result:
                user_id, stored_hash = result
                # 验证密码
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                    return (True, user_id)
            
            return (False, None)