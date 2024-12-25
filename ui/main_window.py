from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                           QMenuBar, QAction, QTableWidget, QTableWidgetItem,
                           QDialog, QTextEdit, QHBoxLayout, QPushButton, QFileDialog,
                           QMessageBox)
from .data_analysis_page import DataAnalysisPage
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
        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建标签页组件
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # 添加四个主要页面
        self.data_analysis_page = DataAnalysisPage()
        self.model_builder_page = ModelBuilderPage()
        self.training_page = TrainingPage()
        self.inference_page = InferencePage()
        
        self.tab_widget.addTab(self.data_analysis_page, "数据分析")
        self.tab_widget.addTab(self.model_builder_page, "模型搭建")
        self.tab_widget.addTab(self.training_page, "模型训练")
        self.tab_widget.addTab(self.inference_page, "模型应用")

        # 添加AI助手标签页作为辅助功能
        self.ai_assistant = AIAssistantWidget()
        self.tab_widget.addTab(self.ai_assistant, "AI助手")

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