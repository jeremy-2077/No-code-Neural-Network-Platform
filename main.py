import sys
import os

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from PyQt5.QtWidgets import QApplication
from ui.main_window_refactored import MainWindow
from ui.styles import ThemeManager
from config import get_config_manager
from utils.logger import logger

def main():
    """应用程序主入口函数"""
    try:
        logger.info("启动神经网络可视化编程平台")
         
        app = QApplication(sys.argv)
        app.setApplicationName("神经网络可视化编程平台")
        app.setApplicationVersion("1.0.0")
        
        # 加载配置
        config_manager = get_config_manager()
        config = config_manager.get_config()
        
        # 根据配置应用主题
        ThemeManager.apply_theme(app, config.ui.theme)
        
        window = MainWindow()
        window.show()
        
        logger.info("应用程序界面已显示")
        
        # 运行应用程序
        exit_code = app.exec_()
        
        logger.info(f"应用程序退出，退出码: {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        logger.critical(f"应用程序启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 