"""
生成模型对话框组件
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QTextEdit, 
                             QFileDialog, QMessageBox)
import sqlite3
import json
import os
import shutil


class GeneratedModelsDialog(QDialog):
    """已生成模型的管理对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("已生成的模型")
        self.resize(800, 600)
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
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
        """加载模型列表"""
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
            QMessageBox.warning(self, "错误", f"加载模型失败: {str(e)}")
            
    def show_model_details(self, row, col):
        """显示模型详情"""
        try:
            model_id = int(self.table.item(row, 0).text())
            
            conn = sqlite3.connect('neural_networks.db')
            cursor = conn.cursor()
            cursor.execute('SELECT model_spec FROM models WHERE id = ?', (model_id,))
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                QMessageBox.warning(self, "错误", "模型数据不存在")
                return
                
            model_spec = result[0]
            
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
            QMessageBox.warning(self, "错误", f"显示模型详情失败: {str(e)}")
            
    def export_selected_model(self):
        """导出选中的模型"""
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
        """应用模型到项目"""
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
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                QMessageBox.warning(self, "错误", "模型数据不存在")
                return
                
            model_spec = json.loads(result[0])
            
            # 将模型应用到项目
            if hasattr(self.parent(), 'model_builder_page'):
                self.parent().model_builder_page.apply_model(model_spec)
                QMessageBox.information(self, "成功", "模型已应用到项目")
                self.close()
            else:
                QMessageBox.warning(self, "错误", "无法找到模型构建页面")
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"应用失败: {str(e)}") 