"""
数据库连接池管理器
优化数据库连接的创建和管理
"""
import sqlite3
import threading
from contextlib import contextmanager
from queue import Queue, Empty
from typing import Optional
from utils.logger import logger, ErrorHandler


class DatabaseConnectionPool:
    """数据库连接池"""
    
    def __init__(self, db_path: str, pool_size: int = 5):
        self.db_path = db_path
        self.pool_size = pool_size
        self._pool = Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        self._initialized = False
        
        # 预创建连接
        self._initialize_pool()
    
    def _initialize_pool(self):
        """初始化连接池"""
        with self._lock:
            if self._initialized:
                return
            
            try:
                for _ in range(self.pool_size):
                    conn = sqlite3.connect(
                        self.db_path,
                        check_same_thread=False,
                        timeout=30.0
                    )
                    # 启用外键约束
                    conn.execute("PRAGMA foreign_keys = ON")
                    # 设置WAL模式以提高并发性能
                    conn.execute("PRAGMA journal_mode = WAL")
                    # 设置同步模式
                    conn.execute("PRAGMA synchronous = NORMAL")
                    
                    self._pool.put(conn)
                
                self._initialized = True
                logger.info(f"数据库连接池初始化完成，创建了 {self.pool_size} 个连接")
                
            except Exception as e:
                error_msg = ErrorHandler.handle_database_error(e, "初始化数据库连接池")
                raise Exception(error_msg)
    
    def get_connection(self) -> sqlite3.Connection:
        """从连接池获取连接"""
        try:
            # 尝试从池中获取连接，超时10秒
            conn = self._pool.get(timeout=10.0)
            
            # 检查连接是否有效
            try:
                conn.execute("SELECT 1").fetchone()
                return conn
            except sqlite3.Error:
                # 连接无效，创建新连接
                logger.warning("检测到无效连接，正在创建新连接")
                conn.close()
                return self._create_new_connection()
                
        except Empty:
            # 连接池为空，创建新连接
            logger.warning("连接池为空，正在创建新连接")
            return self._create_new_connection()
    
    def return_connection(self, conn: sqlite3.Connection):
        """将连接返回到连接池"""
        try:
            if conn and not self._pool.full():
                # 回滚任何未提交的事务
                conn.rollback()
                self._pool.put_nowait(conn)
            else:
                # 连接池已满或连接无效，关闭连接
                if conn:
                    conn.close()
        except Exception as e:
            logger.error(f"返回连接到连接池时出错: {str(e)}")
            if conn:
                conn.close()
    
    def _create_new_connection(self) -> sqlite3.Connection:
        """创建新的数据库连接"""
        try:
            conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            return conn
        except Exception as e:
            error_msg = ErrorHandler.handle_database_error(e, "创建新数据库连接")
            raise Exception(error_msg)
    
    @contextmanager
    def get_connection_context(self):
        """获取连接的上下文管理器"""
        conn = None
        try:
            conn = self.get_connection()
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                self.return_connection(conn)
    
    def close_all(self):
        """关闭所有连接"""
        logger.info("正在关闭数据库连接池")
        with self._lock:
            while not self._pool.empty():
                try:
                    conn = self._pool.get_nowait()
                    conn.close()
                except Empty:
                    break
                except Exception as e:
                    logger.error(f"关闭连接时出错: {str(e)}")
            
            self._initialized = False
            logger.info("数据库连接池已关闭")


# 全局连接池实例
_connection_pool: Optional[DatabaseConnectionPool] = None
_pool_lock = threading.Lock()


def get_connection_pool(db_path: str = "neural_network.db") -> DatabaseConnectionPool:
    """获取全局连接池实例"""
    global _connection_pool
    
    with _pool_lock:
        if _connection_pool is None:
            _connection_pool = DatabaseConnectionPool(db_path)
        return _connection_pool


def close_connection_pool():
    """关闭全局连接池"""
    global _connection_pool
    
    with _pool_lock:
        if _connection_pool:
            _connection_pool.close_all()
            _connection_pool = None 