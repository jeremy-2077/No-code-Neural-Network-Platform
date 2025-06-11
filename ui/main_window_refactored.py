"""
重构后的主窗口
采用更清晰的架构和责任分离
"""
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                             QMenuBar, QAction, QLabel, QStackedWidget,
                             QHBoxLayout, QPushButton, QMessageBox)
from PyQt5.QtCore import pyqtSlot, Qt

from services.user_service import UserService
from ui.components.model_dialog import GeneratedModelsDialog
from ui.login_page import LoginPage
from ui.data_analysis_page import DataAnalysisPage
from ui.model_builder_page import ModelBuilderPage
from ui.training_page import TrainingPage
from ui.inference_page import InferencePage
from ui.ai_assistance import AIAssistantWidget
from ui.styles import ThemeManager
from config import ConfigManager, get_config_manager
from utils.logger import logger, ErrorHandler
from utils.performance_monitor import get_performance_monitor, performance_timer


class UserToolbar(QWidget):
    """用户工具栏组件"""
    
    def __init__(self, user_service: UserService):
        super().__init__()
        self.user_service = user_service
        self.setup_ui()
    
    def setup_ui(self):
        """设置工具栏界面"""
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 用户信息标签
        self.user_label = QLabel()
        layout.addWidget(self.user_label)
        
        layout.addStretch()  # 添加弹性空间
        
        # 登出按钮
        self.logout_btn = QPushButton("登出")
        self.logout_btn.setProperty("class", "danger")
        self.logout_btn.clicked.connect(self.handle_logout)
        layout.addWidget(self.logout_btn)
        
        self.setLayout(layout)
    
    def update_user_info(self):
        """更新用户信息显示"""
        try:
            if self.user_service.is_logged_in():
                username = self.user_service.get_current_username()
                self.user_label.setText(f"当前用户：{username}")
            else:
                self.user_label.setText("")
        except Exception as e:
            logger.error(f"更新用户信息失败: {str(e)}")
    
    def handle_logout(self):
        """处理用户登出"""
        try:
            self.user_service.logout()
            logger.info("用户已登出")
            # 发出登出信号给父窗口
            if hasattr(self.parent(), 'handle_logout'):
                self.parent().handle_logout()
        except Exception as e:
            logger.error(f"登出处理失败: {str(e)}")


class MainContent(QWidget):
    """主内容区域组件"""
    
    def __init__(self, user_service: UserService):
        super().__init__()
        self.user_service = user_service
        self.setup_ui()
        
        # 页面实例
        self.pages = {}
    
    def setup_ui(self):
        """设置主内容界面"""
        layout = QVBoxLayout()
        
        # 用户工具栏
        self.toolbar = UserToolbar(self.user_service)
        layout.addWidget(self.toolbar)
        
        # 标签页容器
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        self.setLayout(layout)
    
    def initialize_pages(self, user_id: int):
        """初始化应用页面"""
        try:
            logger.info(f"为用户 {user_id} 初始化页面")
            
            # 创建页面实例
            if not self.pages:
                self.pages = {
                    'data_analysis': DataAnalysisPage(),
                    'model_builder': ModelBuilderPage(),
                    'training': TrainingPage(),
                    'inference': InferencePage(),
                    'ai_assistant': AIAssistantWidget(user_id)
                }
                
                # 设置用户ID
                for page in self.pages.values():
                    if hasattr(page, 'user_id'):
                        page.user_id = user_id
                
                # 添加到标签页
                self.tab_widget.addTab(self.pages['data_analysis'], "数据分析")
                self.tab_widget.addTab(self.pages['model_builder'], "模型搭建")
                self.tab_widget.addTab(self.pages['training'], "模型训练")
                self.tab_widget.addTab(self.pages['inference'], "模型应用")
                self.tab_widget.addTab(self.pages['ai_assistant'], "AI助手")
            else:
                # 更新现有页面的用户ID
                for page in self.pages.values():
                    if hasattr(page, 'user_id'):
                        page.user_id = user_id
            
            # 更新工具栏
            self.toolbar.update_user_info()
            
        except Exception as e:
            error_msg = ErrorHandler.handle_ui_error(e, "初始化页面")
            QMessageBox.critical(self, "错误", error_msg)
    
    def handle_logout(self):
        """处理登出"""
        # 清理页面数据
        for page in self.pages.values():
            if hasattr(page, 'clear_data'):
                page.clear_data()
        
        # 重置到第一个标签页
        self.tab_widget.setCurrentIndex(0)


class MainWindow(QMainWindow):
    """重构后的主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("神经网络可视化编程平台")
        
        # 初始化配置管理器
        self.config_manager = get_config_manager()
        config = self.config_manager.get_config()
        
        # 设置窗口的响应式大小
        self.setup_responsive_window(config)
        
        # 初始化服务
        self.user_service = UserService()
        
        # 启动性能监控
        self.performance_monitor = get_performance_monitor()
        self.performance_monitor.start_monitoring()
        
        # 设置界面
        self.setup_ui()
        self.create_menu_bar()
        
        logger.info("主窗口初始化完成")
    
    def setup_responsive_window(self, config):
        """设置响应式窗口大小"""
        from PyQt5.QtWidgets import QApplication
        
        # 获取屏幕信息
        desktop = QApplication.desktop()
        screen_geometry = desktop.screenGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        
        # 计算合适的窗口大小（屏幕的80%，但不小于最小尺寸）
        min_width = 1000
        min_height = 700
        max_width = int(screen_width * 0.9)
        max_height = int(screen_height * 0.9)
        
        # 优先使用配置中的大小，但要确保在合理范围内
        window_width = max(min_width, min(config.ui.window_width, max_width))
        window_height = max(min_height, min(config.ui.window_height, max_height))
        
        # 设置最小和最大窗口尺寸
        self.setMinimumSize(min_width, min_height)
        self.setMaximumSize(max_width, max_height)
        
        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 设置窗口位置和大小
        self.setGeometry(x, y, window_width, window_height)
        
        logger.info(f"窗口大小设置为: {window_width}x{window_height}, 位置: ({x}, {y})")
        logger.info(f"屏幕尺寸: {screen_width}x{screen_height}")
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建堆叠窗口部件
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # 创建登录页面
        self.login_page = LoginPage()
        self.login_page.login_success.connect(self.handle_login_success)
        
        # 创建主内容页面
        self.main_content = MainContent(self.user_service)
        self.main_content.toolbar.parent = lambda: self  # 设置父窗口引用
        
        # 添加到堆叠窗口
        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.main_content)
        
        # 默认显示登录页面
        self.stacked_widget.setCurrentWidget(self.login_page)
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # AI助手菜单
        ai_menu = menubar.addMenu("AI助手")
        
        view_models_action = QAction("查看已生成模型", self)
        view_models_action.triggered.connect(self.show_generated_models)
        ai_menu.addAction(view_models_action)
        
        # 设置菜单
        settings_menu = menubar.addMenu("设置")
        
        # 主题子菜单
        theme_menu = settings_menu.addMenu("主题")
        
        dark_theme_action = QAction("深色主题", self)
        dark_theme_action.setCheckable(True)
        dark_theme_action.setChecked(True)  # 默认深色主题
        dark_theme_action.triggered.connect(lambda: self.switch_theme(ThemeManager.DARK))
        theme_menu.addAction(dark_theme_action)
        
        light_theme_action = QAction("浅色主题", self)
        light_theme_action.setCheckable(True)
        light_theme_action.triggered.connect(lambda: self.switch_theme(ThemeManager.LIGHT))
        theme_menu.addAction(light_theme_action)
        
        # 创建主题动作组（确保只能选择一个）
        from PyQt5.QtWidgets import QActionGroup
        self.theme_group = QActionGroup(self)
        self.theme_group.addAction(dark_theme_action)
        self.theme_group.addAction(light_theme_action)
        
        self.dark_theme_action = dark_theme_action
        self.light_theme_action = light_theme_action
    
    @performance_timer("ui_operation")
    def switch_theme(self, theme_name: str):
        """切换主题"""
        try:
            logger.info(f"切换到{theme_name}主题")
            
            # 获取应用程序实例
            from PyQt5.QtWidgets import QApplication
            app = QApplication.instance()
            
            # 应用新主题
            ThemeManager.apply_theme(app, theme_name)
            
            # 保存主题配置
            self.config_manager.update_ui_config(theme=theme_name)
            
            # 更新菜单选中状态
            if theme_name == ThemeManager.DARK:
                self.dark_theme_action.setChecked(True)
            elif theme_name == ThemeManager.LIGHT:
                self.light_theme_action.setChecked(True)
            
            logger.info(f"主题切换完成: {theme_name}")
            
        except Exception as e:
            error_msg = ErrorHandler.handle_ui_error(e, "切换主题")
            QMessageBox.warning(self, "主题切换失败", error_msg)
    
    @pyqtSlot(int)
    def handle_login_success(self, user_id: int):
        """处理登录成功"""
        try:
            logger.info(f"用户 {user_id} 登录成功")
            
            # 初始化主内容页面
            self.main_content.initialize_pages(user_id)
            
            # 切换到主内容页面
            self.stacked_widget.setCurrentWidget(self.main_content)
            
        except Exception as e:
            error_msg = ErrorHandler.handle_ui_error(e, "处理登录成功")
            QMessageBox.critical(self, "错误", error_msg)
    
    def handle_logout(self):
        """处理登出"""
        try:
            logger.info("处理用户登出")
            
            # 清理登录表单
            self.login_page.username_input.clear()
            self.login_page.password_input.clear()
            
            # 处理主内容的登出
            self.main_content.handle_logout()
            
            # 切换到登录页面
            self.stacked_widget.setCurrentWidget(self.login_page)
            
        except Exception as e:
            error_msg = ErrorHandler.handle_ui_error(e, "处理登出")
            QMessageBox.critical(self, "错误", error_msg)
    
    def show_generated_models(self):
        """显示已生成的模型对话框"""
        try:
            if not self.user_service.is_logged_in():
                QMessageBox.warning(self, "警告", "请先登录")
                return
            
            dialog = GeneratedModelsDialog(self)
            dialog.exec_()
            
        except Exception as e:
            error_msg = ErrorHandler.handle_ui_error(e, "显示模型对话框")
            QMessageBox.critical(self, "错误", error_msg)
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        try:
            logger.info("应用程序正在关闭")
            
            # 保存窗口位置和大小
            geometry = self.geometry()
            self.config_manager.save_window_geometry(
                geometry.x(), geometry.y(),
                geometry.width(), geometry.height()
            )
            
            # 停止性能监控
            self.performance_monitor.stop_monitoring()
            
            # 导出性能报告
            try:
                import os
                os.makedirs("logs", exist_ok=True)
                self.performance_monitor.export_metrics("logs/performance_report.json")
            except Exception as e:
                logger.warning(f"导出性能报告失败: {str(e)}")
            
            # 关闭数据库连接池
            from database.connection_pool import close_connection_pool
            close_connection_pool()
            
            event.accept()
            
        except Exception as e:
            logger.error(f"关闭应用程序时出错: {str(e)}")
            event.accept() 