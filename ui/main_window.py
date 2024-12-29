from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                             QMenuBar, QAction, QTableWidget, QTableWidgetItem,
                             QDialog, QTextEdit, QHBoxLayout, QPushButton, QFileDialog,
                             QMessageBox, QLabel, QStackedWidget)

from database.db_manager import DatabaseManager
from .data_analysis_page import DataAnalysisPage
from .login_page import LoginPage
from .model_builder_page import ModelBuilderPage
from .training_page import TrainingPage
from .inference_page import InferencePage
from ui.ai_assistance import AIAssistantWidget
import sqlite3
import json
import os
import shutil

class GeneratedModelsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("已生成的模型")
        self.resize(800, 600)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "任务类型", "数据规模", "复杂度",
            "时间预算", "特殊需求", "创建时间"
        ])
        layout.addWidget(self.table)
        
        # 添加按钮
        button_layout = QHBoxLayout()
        
        export_btn = QPushButton("导出选中模型")
        export_btn.clicked.connect(self.export_selected_model)
        button_layout.addWidget(export_btn)
        
        apply_btn = QPushButton("应用到项目")
        apply_btn.clicked.connect(self.apply_to_project)
        button_layout.addWidget(apply_btn)
        
        layout.addLayout(button_layout)
        
        # 加载数据
        self.load_models()
        
        # 双击查看详情
        self.table.cellDoubleClicked.connect(self.show_model_details)
        
        self.setLayout(layout)
        
    def load_models(self):
        try:
            conn = sqlite3.connect('neural_networks.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM models ORDER BY created_at DESC')
            models = cursor.fetchall()
            
            self.table.setRowCount(len(models))
            for i, model in enumerate(models):
                for j, value in enumerate(model):
                    if j != 6:  # 跳过model_spec列
                        self.table.setItem(i, j, QTableWidgetItem(str(value)))
            
            conn.close()
        except Exception as e:
            print(f"加载模型失败: {str(e)}")
            
    def show_model_details(self, row, col):
        try:
            model_id = int(self.table.item(row, 0).text())
            
            conn = sqlite3.connect('neural_networks.db')
            cursor = conn.cursor()
            cursor.execute('SELECT model_spec FROM models WHERE id = ?', (model_id,))
            model_spec = cursor.fetchone()[0]
            conn.close()
            
            details_dialog = QDialog(self)
            details_dialog.setWindowTitle(f"模型 {model_id} 详情")
            details_dialog.resize(600, 400)
            
            layout = QVBoxLayout()
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setText(json.dumps(json.loads(model_spec), 
                                       indent=2, ensure_ascii=False))
            layout.addWidget(text_edit)
            
            details_dialog.setLayout(layout)
            details_dialog.exec_()
            
        except Exception as e:
            print(f"显示模型详情失败: {str(e)}")
            
    def export_selected_model(self):
        try:
            current_row = self.table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "警告", "请先选择一个模型")
                return
                
            model_id = int(self.table.item(current_row, 0).text())
            model_dir = f"generated_models/model_{model_id}"
            
            if not os.path.exists(model_dir):
                QMessageBox.warning(self, "错误", "模型文件不存在")
                return
            
            export_dir = QFileDialog.getExistingDirectory(
                self, "选择导出目录", "", QFileDialog.ShowDirsOnly)
                
            if export_dir:
                shutil.copytree(model_dir, f"{export_dir}/model_{model_id}")
                QMessageBox.information(self, "成功", "模型已导出")
                
        except Exception as e:
            QMessageBox.warning(self, "错误", f"导出失败: {str(e)}")
            
    def apply_to_project(self):
        try:
            current_row = self.table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "警告", "请先选择一个模型")
                return
                
            model_id = int(self.table.item(current_row, 0).text())
            
            # 获取模型规范
            conn = sqlite3.connect('neural_networks.db')
            cursor = conn.cursor()
            cursor.execute('SELECT model_spec FROM models WHERE id = ?', (model_id,))
            model_spec = json.loads(cursor.fetchone()[0])
            conn.close()
            
            # 将模型应用到项目
            self.parent().model_builder_page.apply_model(model_spec)
            
            QMessageBox.information(self, "成功", "模型已应用到项目")
            self.close()
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"应用失败: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("神经网络可视化编程平台")
        self.setGeometry(100, 100, 1200, 800)
        self.init_ui()
        self.create_menu_bar()

    def init_ui(self):
        # 创建堆叠窗口部件
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # 创建登录页面
        self.login_page = LoginPage()
        self.login_page.login_success.connect(self.on_login_success)

        # 添加登录页面到堆叠窗口部件
        self.stacked_widget.addWidget(self.login_page)

        # 创建主内容页面
        self.main_content = QTabWidget()

        # 创建包含标签页和登出按钮的容器
        self.main_container = QWidget()
        main_layout = QVBoxLayout()

        # 创建顶部工具栏
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(0, 0, 0, 0)

        # 添加用户信息标签
        self.user_label = QLabel()
        toolbar_layout.addWidget(self.user_label)

        toolbar_layout.addStretch()  # 添加弹性空间

        # 创建登出按钮
        self.logout_btn = QPushButton("登出")
        self.logout_btn.clicked.connect(self.logout)

        toolbar_layout.addWidget(self.logout_btn)

        toolbar.setLayout(toolbar_layout)

        # 将工具栏和标签页添加到主容器
        main_layout.addWidget(toolbar)
        main_layout.addWidget(self.main_content)
        self.main_container.setLayout(main_layout)

        # 添加主容器到堆叠窗口部件
        self.stacked_widget.addWidget(self.main_container)

        # 初始化主要页面（但不立即创建实例）
        self.data_analysis_page = None
        self.model_builder_page = None
        self.training_page = None
        self.inference_page = None
        self.ai_assistant = None

        # 显示登录页面
        self.stacked_widget.setCurrentWidget(self.login_page)

    def on_login_success(self, user_id):
        """登录成功后的处理"""
        # 创建主要页面实例
        if not self.data_analysis_page:
            self.data_analysis_page = DataAnalysisPage()
            self.model_builder_page = ModelBuilderPage()
            self.training_page = TrainingPage()
            self.inference_page = InferencePage()
            # 添加AI助手标签页作为辅助功能
            self.ai_assistant = AIAssistantWidget(user_id)

            # 设置用户ID
            self.data_analysis_page.user_id = user_id
            self.model_builder_page.user_id = user_id
            self.training_page.user_id = user_id
            self.inference_page.user_id = user_id
            self.ai_assistant.user_id = user_id

            # 添加页面到标签栏
            self.main_content.addTab(self.data_analysis_page, "数据分析")
            self.main_content.addTab(self.model_builder_page, "模型搭建")
            self.main_content.addTab(self.training_page, "模型训练")
            self.main_content.addTab(self.inference_page, "模型应用")
            self.main_content.addTab(self.ai_assistant, "AI助手")
        else:
            # 更新各页面的用户ID
            self.data_analysis_page.user_id = user_id
            self.model_builder_page.user_id = user_id
            self.training_page.user_id = user_id
            self.inference_page.user_id = user_id
            self.ai_assistant.user_id = user_id

        # 更新用户信息显示
        self.update_user_info(user_id)

        # 切换到主内容页面
        self.stacked_widget.setCurrentWidget(self.main_container)
        
        # 设置默认显示数据分析标签页
        self.main_content.setCurrentIndex(0)

    def update_user_info(self, user_id):
        """更新用户信息显示"""
        # 从数据库获取用户名
        with DatabaseManager().get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            if result:
                self.user_label.setText(f"当前用户：{result[0]}")

    def logout(self):
        """登出处理"""
        # 清空登录表单
        self.login_page.username_input.clear()
        self.login_page.password_input.clear()

        # 切换回登录页面
        self.stacked_widget.setCurrentWidget(self.login_page)



    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # AI助手菜单
        ai_menu = menubar.addMenu("AI助手")
        
        view_models_action = QAction("查看已生成模型", self)
        view_models_action.triggered.connect(self.view_generated_models)
        ai_menu.addAction(view_models_action)
    
    def view_generated_models(self):
        dialog = GeneratedModelsDialog(self)
        dialog.exec_()