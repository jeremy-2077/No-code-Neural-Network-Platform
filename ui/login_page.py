from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit,
                            QPushButton, QLabel, QMessageBox)
from PyQt5.QtCore import pyqtSignal
from database.db_manager import DatabaseManager

class LoginPage(QWidget):
    login_success = pyqtSignal(int)  # 登录成功信号，传递用户ID
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("无代码神经网络编程平台")
        title.setStyleSheet("font-size: 24px; margin: 20px;")
        layout.addWidget(title)
        
        # 登录表单
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        form_layout.addRow("用户名:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("密码:", self.password_input)
        
        layout.addLayout(form_layout)
        
        # 登录按钮
        self.login_btn = QPushButton("登录")
        self.login_btn.clicked.connect(self.login)
        layout.addWidget(self.login_btn)
        
        # 注册按钮
        self.register_btn = QPushButton("注册新用户")
        self.register_btn.clicked.connect(self.register)
        layout.addWidget(self.register_btn)
        
        self.setLayout(layout)
    
    def login(self):
        """登录处理"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "警告", "用户名和密码不能为空！")
            return
        
        success, user_id = self.db.verify_user(username, password)
        if success:
            self.login_success.emit(user_id)
        else:
            QMessageBox.warning(self, "错误", "用户名或密码错误！")
    
    def register(self):
        """注册处理"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "警告", "用户名和密码��能为空！")
            return
        
        if self.db.add_user(username, password):
            QMessageBox.information(self, "成功", "注册成功！请登录。")
        else:
            QMessageBox.warning(self, "错误", "用户名已存在！") 