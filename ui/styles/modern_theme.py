"""
现代化UI主题样式
提供深色和浅色两种主题
"""

DARK_THEME = """
/* 全局样式 */
QMainWindow {
    background-color: #2b2b2b;
    color: #ffffff;
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
    font-size: 9pt;
}

QWidget {
    background-color: #2b2b2b;
    color: #ffffff;
}

/* 按钮样式 */
QPushButton {
    background-color: #3d4142;
    border: 2px solid #5a5a5a;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: bold;
    min-width: 80px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #4a4a4a;
    border-color: #007acc;
}

QPushButton:pressed {
    background-color: #2a2a2a;
    border-color: #005a9e;
}

QPushButton:disabled {
    background-color: #1e1e1e;
    border-color: #3a3a3a;
    color: #808080;
}

/* 主要按钮（登录、注册等） */
QPushButton[class="primary"] {
    background-color: #007acc;
    border-color: #007acc;
    color: #ffffff;
}

QPushButton[class="primary"]:hover {
    background-color: #1e8ce6;
    border-color: #1e8ce6;
}

QPushButton[class="primary"]:pressed {
    background-color: #005a9e;
    border-color: #005a9e;
}

/* 危险按钮（删除等） */
QPushButton[class="danger"] {
    background-color: #d73a49;
    border-color: #d73a49;
    color: #ffffff;
}

QPushButton[class="danger"]:hover {
    background-color: #e85663;
    border-color: #e85663;
}

/* 输入框样式 */
QLineEdit {
    background-color: #404040;
    border: 2px solid #5a5a5a;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 9pt;
    selection-background-color: #007acc;
}

QLineEdit:focus {
    border-color: #007acc;
    background-color: #4a4a4a;
}

QLineEdit:disabled {
    background-color: #2a2a2a;
    border-color: #3a3a3a;
    color: #808080;
}

/* 文本框样式 */
QTextEdit {
    background-color: #404040;
    border: 2px solid #5a5a5a;
    border-radius: 6px;
    padding: 8px;
    font-family: "Consolas", "Monaco", monospace;
    selection-background-color: #007acc;
}

QTextEdit:focus {
    border-color: #007acc;
}

/* 标签样式 */
QLabel {
    color: #ffffff;
    font-size: 9pt;
}

QLabel[class="title"] {
    font-size: 18pt;
    font-weight: bold;
    color: #007acc;
    margin: 10px 0;
}

QLabel[class="subtitle"] {
    font-size: 12pt;
    font-weight: bold;
    color: #cccccc;
    margin: 5px 0;
}

QLabel[class="info"] {
    color: #cccccc;
    font-size: 8pt;
}

/* 标签页样式 */
QTabWidget::pane {
    border: 1px solid #5a5a5a;
    background-color: #2b2b2b;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #3d4142;
    border: 1px solid #5a5a5a;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    min-width: 80px;
}

QTabBar::tab:selected {
    background-color: #007acc;
    color: #ffffff;
    border-bottom-color: #007acc;
}

QTabBar::tab:hover:!selected {
    background-color: #4a4a4a;
}

/* 表格样式 */
QTableWidget {
    background-color: #404040;
    border: 1px solid #5a5a5a;
    border-radius: 4px;
    gridline-color: #5a5a5a;
    selection-background-color: #007acc;
}

QHeaderView::section {
    background-color: #3d4142;
    border: 1px solid #5a5a5a;
    padding: 8px;
    font-weight: bold;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #5a5a5a;
}

QTableWidget::item:selected {
    background-color: #007acc;
}

/* 菜单样式 */
QMenuBar {
    background-color: #3d4142;
    border-bottom: 1px solid #5a5a5a;
    padding: 4px;
}

QMenuBar::item {
    background: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #007acc;
}

QMenu {
    background-color: #404040;
    border: 1px solid #5a5a5a;
    border-radius: 4px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 16px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #007acc;
}

/* 滚动条样式 */
QScrollBar:vertical {
    background-color: #3d4142;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #5a5a5a;
    border-radius: 6px;
    min-height: 20px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #007acc;
}

QScrollBar:horizontal {
    background-color: #3d4142;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #5a5a5a;
    border-radius: 6px;
    min-width: 20px;
    margin: 2px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #007acc;
}

/* 分组框样式 */
QGroupBox {
    border: 2px solid #5a5a5a;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 8px 0 8px;
    color: #007acc;
}

/* 对话框样式 */
QDialog {
    background-color: #2b2b2b;
    border-radius: 8px;
}

/* 状态栏样式 */
QStatusBar {
    background-color: #3d4142;
    border-top: 1px solid #5a5a5a;
    padding: 4px;
}

/* 工具栏样式 */
QToolBar {
    background-color: #3d4142;
    border: none;
    padding: 4px;
    spacing: 4px;
}

QToolBar::separator {
    background-color: #5a5a5a;
    width: 1px;
    margin: 4px;
}

/* 进度条样式 */
QProgressBar {
    background-color: #404040;
    border: 2px solid #5a5a5a;
    border-radius: 6px;
    text-align: center;
    font-weight: bold;
}

QProgressBar::chunk {
    background-color: #007acc;
    border-radius: 4px;
}

/* 复选框样式 */
QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #5a5a5a;
    border-radius: 3px;
    background-color: #404040;
}

QCheckBox::indicator:checked {
    background-color: #007acc;
    border-color: #007acc;
}

QCheckBox::indicator:checked:hover {
    background-color: #1e8ce6;
}
"""

LIGHT_THEME = """
/* 浅色主题样式 */
QMainWindow {
    background-color: #ffffff;
    color: #333333;
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
    font-size: 9pt;
}

QWidget {
    background-color: #ffffff;
    color: #333333;
}

QPushButton {
    background-color: #f8f9fa;
    border: 2px solid #dee2e6;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: bold;
    min-width: 80px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #e9ecef;
    border-color: #007acc;
}

QPushButton:pressed {
    background-color: #dee2e6;
    border-color: #005a9e;
}

QPushButton[class="primary"] {
    background-color: #007acc;
    border-color: #007acc;
    color: #ffffff;
}

QPushButton[class="primary"]:hover {
    background-color: #1e8ce6;
    border-color: #1e8ce6;
}

QPushButton[class="danger"] {
    background-color: #dc3545;
    border-color: #dc3545;
    color: #ffffff;
}

QLineEdit {
    background-color: #ffffff;
    border: 2px solid #dee2e6;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 9pt;
    selection-background-color: #007acc;
}

QLineEdit:focus {
    border-color: #007acc;
    background-color: #f8f9fa;
}

QLabel[class="title"] {
    font-size: 18pt;
    font-weight: bold;
    color: #007acc;
    margin: 10px 0;
}

QTabWidget::pane {
    border: 1px solid #dee2e6;
    background-color: #ffffff;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    min-width: 80px;
}

QTabBar::tab:selected {
    background-color: #007acc;
    color: #ffffff;
}

QTableWidget {
    background-color: #ffffff;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    gridline-color: #dee2e6;
    selection-background-color: #007acc;
}

QHeaderView::section {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    padding: 8px;
    font-weight: bold;
}
"""


class ThemeManager:
    """主题管理器"""
    
    DARK = "dark"
    LIGHT = "light"
    
    @staticmethod
    def get_theme(theme_name: str) -> str:
        """获取主题样式"""
        if theme_name == ThemeManager.DARK:
            return DARK_THEME
        elif theme_name == ThemeManager.LIGHT:
            return LIGHT_THEME
        else:
            return DARK_THEME  # 默认深色主题
    
    @staticmethod
    def apply_theme(app, theme_name: str = DARK):
        """应用主题到应用程序"""
        style = ThemeManager.get_theme(theme_name)
        app.setStyleSheet(style)
    
    @staticmethod
    def get_available_themes() -> list:
        """获取可用主题列表"""
        return [ThemeManager.DARK, ThemeManager.LIGHT] 