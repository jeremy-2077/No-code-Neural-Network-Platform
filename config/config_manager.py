"""
应用程序配置管理系统
提供配置的读取、保存和管理功能
"""
import json
import os
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from utils.logger import logger, ErrorHandler


@dataclass
class DatabaseConfig:
    """数据库配置"""
    path: str = "neural_network.db"
    pool_size: int = 5
    timeout: float = 30.0
    enable_wal: bool = True
    enable_foreign_keys: bool = True


@dataclass
class UIConfig:
    """用户界面配置"""
    theme: str = "dark"  # dark 或 light
    window_width: int = 1200
    window_height: int = 800
    window_x: int = 100
    window_y: int = 100
    remember_window_position: bool = True
    auto_save_interval: int = 30  # 秒


@dataclass
class LogConfig:
    """日志配置"""
    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    max_file_size: int = 10  # MB
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = True


@dataclass
class ModelConfig:
    """模型配置"""
    default_save_format: str = "pth"  # pth 或 onnx
    auto_backup: bool = True
    max_backup_count: int = 10
    compression_enabled: bool = False


@dataclass
class AppConfig:
    """应用程序总配置"""
    database: DatabaseConfig
    ui: UIConfig
    logging: LogConfig
    model: ModelConfig
    
    def __init__(self):
        self.database = DatabaseConfig()
        self.ui = UIConfig()
        self.logging = LogConfig()
        self.model = ModelConfig()


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config: AppConfig = AppConfig()
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 更新数据库配置
                if 'database' in data:
                    db_config = data['database']
                    self.config.database = DatabaseConfig(**db_config)
                
                # 更新UI配置
                if 'ui' in data:
                    ui_config = data['ui']
                    self.config.ui = UIConfig(**ui_config)
                
                # 更新日志配置
                if 'logging' in data:
                    log_config = data['logging']
                    self.config.logging = LogConfig(**log_config)
                
                # 更新模型配置
                if 'model' in data:
                    model_config = data['model']
                    self.config.model = ModelConfig(**model_config)
                
                logger.info(f"配置文件加载成功: {self.config_file}")
            else:
                logger.info("配置文件不存在，使用默认配置")
                self._save_config()  # 创建默认配置文件
                
        except Exception as e:
            error_msg = ErrorHandler.handle_file_error(e, "加载配置文件")
            logger.warning(f"加载配置失败，使用默认配置: {error_msg}")
    
    def _save_config(self):
        """保存配置到文件"""
        try:
            config_data = {
                'database': asdict(self.config.database),
                'ui': asdict(self.config.ui),
                'logging': asdict(self.config.logging),
                'model': asdict(self.config.model)
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置文件保存成功: {self.config_file}")
            
        except Exception as e:
            error_msg = ErrorHandler.handle_file_error(e, "保存配置文件")
            logger.error(error_msg)
    
    def get_config(self) -> AppConfig:
        """获取当前配置"""
        return self.config
    
    def update_database_config(self, **kwargs):
        """更新数据库配置"""
        for key, value in kwargs.items():
            if hasattr(self.config.database, key):
                setattr(self.config.database, key, value)
                logger.info(f"更新数据库配置: {key}={value}")
        self._save_config()
    
    def update_ui_config(self, **kwargs):
        """更新UI配置"""
        for key, value in kwargs.items():
            if hasattr(self.config.ui, key):
                setattr(self.config.ui, key, value)
                logger.info(f"更新UI配置: {key}={value}")
        self._save_config()
    
    def update_logging_config(self, **kwargs):
        """更新日志配置"""
        for key, value in kwargs.items():
            if hasattr(self.config.logging, key):
                setattr(self.config.logging, key, value)
                logger.info(f"更新日志配置: {key}={value}")
        self._save_config()
    
    def update_model_config(self, **kwargs):
        """更新模型配置"""
        for key, value in kwargs.items():
            if hasattr(self.config.model, key):
                setattr(self.config.model, key, value)
                logger.info(f"更新模型配置: {key}={value}")
        self._save_config()
    
    def reset_to_default(self):
        """重置为默认配置"""
        logger.info("重置配置为默认值")
        self.config = AppConfig()
        self._save_config()
    
    def export_config(self, export_path: str) -> bool:
        """导出配置到指定路径"""
        try:
            import shutil
            shutil.copy2(self.config_file, export_path)
            logger.info(f"配置文件导出成功: {export_path}")
            return True
        except Exception as e:
            error_msg = ErrorHandler.handle_file_error(e, "导出配置文件")
            logger.error(error_msg)
            return False
    
    def import_config(self, import_path: str) -> bool:
        """从指定路径导入配置"""
        try:
            import shutil
            shutil.copy2(import_path, self.config_file)
            self._load_config()
            logger.info(f"配置文件导入成功: {import_path}")
            return True
        except Exception as e:
            error_msg = ErrorHandler.handle_file_error(e, "导入配置文件")
            logger.error(error_msg)
            return False
    
    def get_window_geometry(self) -> tuple:
        """获取窗口几何信息"""
        ui = self.config.ui
        return (ui.window_x, ui.window_y, ui.window_width, ui.window_height)
    
    def save_window_geometry(self, x: int, y: int, width: int, height: int):
        """保存窗口几何信息"""
        if self.config.ui.remember_window_position:
            self.update_ui_config(
                window_x=x,
                window_y=y, 
                window_width=width,
                window_height=height
            )


# 全局配置管理器实例
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> AppConfig:
    """获取应用程序配置的快捷方法"""
    return get_config_manager().get_config() 