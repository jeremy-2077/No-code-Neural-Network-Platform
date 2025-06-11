from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                            QPushButton, QLabel, QMessageBox)
from PyQt5.QtCore import pyqtSignal, Qt
from services.user_service import UserService
from utils.logger import logger, ErrorHandler

class LoginPage(QWidget):
    login_success = pyqtSignal(int)  # 登录成功信号，传递用户ID
    
    def __init__(self):
        super().__init__()
        self.user_service = UserService()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # 添加顶部空间
        layout.addStretch(1)
        
        # 标题
        title = QLabel("无代码神经网络编程平台")
        title.setProperty("class", "title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 副标题
        subtitle = QLabel("智能化模型构建，让AI开发变得简单")
        subtitle.setProperty("class", "info")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        # 登录表单容器
        form_container = QWidget()
        form_container.setMaximumWidth(400)
        form_container.setMinimumWidth(300)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(15)
        
        # 用户名输入
        username_label = QLabel("用户名")
        form_layout.addWidget(username_label)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setMinimumHeight(40)
        form_layout.addWidget(self.username_input)
        
        # 密码输入
        password_label = QLabel("密码")
        form_layout.addWidget(password_label)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        form_layout.addWidget(self.password_input)
        
        form_layout.addSpacing(20)
        
        # 按钮容器
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)
        
        # 登录按钮
        self.login_btn = QPushButton("登录")
        self.login_btn.setProperty("class", "primary")
        self.login_btn.setMinimumHeight(45)
        self.login_btn.clicked.connect(self.login)
        button_layout.addWidget(self.login_btn)
        
        # 注册按钮
        self.register_btn = QPushButton("注册新用户")
        self.register_btn.setMinimumHeight(45)
        self.register_btn.clicked.connect(self.register)
        button_layout.addWidget(self.register_btn)
        
        form_layout.addLayout(button_layout)
        
        # 居中显示表单
        form_wrapper = QHBoxLayout()
        form_wrapper.addStretch(1)
        form_wrapper.addWidget(form_container)
        form_wrapper.addStretch(1)
        
        layout.addLayout(form_wrapper)
        layout.addStretch(2)
        
        # 底部信息
        info_label = QLabel("提示：用户名至少3个字符，密码至少6个字符")
        info_label.setProperty("class", "info")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        self.setLayout(layout)
        
        # 回车键快捷键
        self.password_input.returnPressed.connect(self.login)
        self.username_input.returnPressed.connect(self.password_input.setFocus)
    
    def login(self):
        """登录处理"""
        try:
            username = self.username_input.text().strip()
            password = self.password_input.text().strip()
            
            success, user_id, message = self.user_service.login(username, password)
            
            if success:
                logger.info(f"用户 {username} 登录成功")
                self.login_success.emit(user_id)
            else:
                QMessageBox.warning(self, "登录失败", message)
                
        except Exception as e:
            error_msg = ErrorHandler.handle_ui_error(e, "用户登录")
            QMessageBox.critical(self, "错误", error_msg)
    
    def register(self):
        """注册处理"""
        try:
            username = self.username_input.text().strip()
            password = self.password_input.text().strip()
            
            success, message = self.user_service.register(username, password)
            
            if success:
                logger.info(f"用户 {username} 注册成功")
                QMessageBox.information(self, "注册成功", message)
            else:
                QMessageBox.warning(self, "注册失败", message)
                
        except Exception as e:
            error_msg = ErrorHandler.handle_ui_error(e, "用户注册")
            QMessageBox.critical(self, "错误", error_msg) 