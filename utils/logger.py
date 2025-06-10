"""
统一日志管理系统
提供应用程序的日志记录功能
"""
import logging
import os
from datetime import datetime
from typing import Optional


class Logger:
    """应用程序日志管理器"""
    
    _instance: Optional['Logger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self):
        """设置日志配置"""
        # 创建日志目录
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # 创建日志文件名
        log_filename = f"{log_dir}/app_{datetime.now().strftime('%Y%m%d')}.log"
        
        # 配置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        
        # 创建logger
        self._logger = logging.getLogger('NeuralNetworkPlatform')
        self._logger.setLevel(logging.DEBUG)
        
        # 避免重复添加handler
        if not self._logger.handlers:
            # 文件处理器
            file_handler = logging.FileHandler(log_filename, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            
            # 添加处理器
            self._logger.addHandler(file_handler)
            self._logger.addHandler(console_handler)
    
    def debug(self, message: str, *args, **kwargs):
        """记录调试信息"""
        self._logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """记录一般信息"""
        self._logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """记录警告信息"""
        self._logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """记录错误信息"""
        self._logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """记录严重错误信息"""
        self._logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """记录异常信息（包含traceback）"""
        self._logger.exception(message, *args, **kwargs)


# 创建全局logger实例
logger = Logger()


def log_exception(func):
    """装饰器：自动记录函数异常"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"函数 {func.__name__} 发生异常: {str(e)}")
            raise
    return wrapper


class ErrorHandler:
    """统一错误处理器"""
    
    @staticmethod
    def handle_database_error(e: Exception, operation: str = "数据库操作") -> str:
        """处理数据库错误"""
        error_msg = f"{operation}失败: {str(e)}"
        logger.error(error_msg)
        return error_msg
    
    @staticmethod
    def handle_file_error(e: Exception, operation: str = "文件操作") -> str:
        """处理文件操作错误"""
        error_msg = f"{operation}失败: {str(e)}"
        logger.error(error_msg)
        return error_msg
    
    @staticmethod
    def handle_model_error(e: Exception, operation: str = "模型操作") -> str:
        """处理模型相关错误"""
        error_msg = f"{operation}失败: {str(e)}"
        logger.error(error_msg)
        return error_msg
    
    @staticmethod
    def handle_ui_error(e: Exception, operation: str = "界面操作") -> str:
        """处理UI相关错误"""
        error_msg = f"{operation}失败: {str(e)}"
        logger.error(error_msg)
        return error_msg
    
    @staticmethod
    def handle_network_error(e: Exception, operation: str = "网络操作") -> str:
        """处理网络相关错误"""
        error_msg = f"{operation}失败: {str(e)}"
        logger.error(error_msg)
        return error_msg 