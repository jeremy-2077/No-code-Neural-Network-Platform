from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QGroupBox, QFormLayout, QLineEdit, QMessageBox,
                            QFileDialog, QTableWidget, QTableWidgetItem, QComboBox)
from PyQt5.QtCore import Qt
import torch
import pandas as pd
import numpy as np
from models.neural_network import NNModel
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class InferencePage(QWidget):
    def __init__(self):
        super().__init__()
        self.model = None
        self.input_data = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout()
        
        # 左侧面板：模型加载和数据输入
        left_panel = QVBoxLayout()
        
        # 模型加载组
        model_group = QGroupBox("模型加载")
        model_layout = QVBoxLayout()
        
        self.load_model_btn = QPushButton("加载模型")
        self.load_model_btn.clicked.connect(self.load_model)
        
        self.model_info_label = QLabel("未加载模型")
        
        model_layout.addWidget(self.load_model_btn)
        model_layout.addWidget(self.model_info_label)
        model_group.setLayout(model_layout)
        
        # 数据输入组
        input_group = QGroupBox("数据输入")
        input_layout = QVBoxLayout()
        
        # 任务类型选择
        task_layout = QFormLayout()
        self.task_combo = QComboBox()
        self.task_combo.addItems(["分类", "回归"])
        self.task_combo.currentTextChanged.connect(self.on_task_changed)
        task_layout.addRow("任务类型:", self.task_combo)
        
        # 数据输入方式
        self.input_file_btn = QPushButton("导入数据文件")
        self.input_file_btn.clicked.connect(self.load_input_data)
        
        # 手动输入区域
        self.manual_input = QLineEdit()
        self.manual_input.setPlaceholderText("输入数据（用逗号分隔）")
        
        input_layout.addLayout(task_layout)
        input_layout.addWidget(self.input_file_btn)
        input_layout.addWidget(QLabel("或手动输入:"))
        input_layout.addWidget(self.manual_input)
        input_group.setLayout(input_layout)

        # 数据选择组
        column_select_group = QGroupBox("数据列选择")
        column_select_layout = QVBoxLayout()

        self.column_list_widget = QTableWidget()
        self.column_list_widget.setColumnCount(1)
        self.column_list_widget.setHorizontalHeaderLabels(["列名"])
        self.column_list_widget.setSelectionMode(QTableWidget.MultiSelection)

        apply_columns_btn = QPushButton("应用选择")
        apply_columns_btn.clicked.connect(self.apply_selected_columns)

        column_select_layout.addWidget(self.column_list_widget)
        column_select_layout.addWidget(apply_columns_btn)
        column_select_group.setLayout(column_select_layout)

        # 预测控制组
        predict_group = QGroupBox("预测控制")
        predict_layout = QVBoxLayout()
        
        self.predict_btn = QPushButton("开始预测")
        self.predict_btn.clicked.connect(self.predict)
        self.predict_btn.setEnabled(False)
        
        predict_layout.addWidget(self.predict_btn)
        predict_group.setLayout(predict_layout)
        
        left_panel.addWidget(model_group)
        left_panel.addWidget(input_group)
        left_panel.addWidget(column_select_group)
        left_panel.addWidget(predict_group)
        left_panel.addStretch()
        
        # 右侧面板：预测结果显示
        right_panel = QVBoxLayout()
        
        # 结果表格
        result_group = QGroupBox("预测结果")
        result_layout = QVBoxLayout()
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(2)
        self.result_table.setHorizontalHeaderLabels(["输入", "预测结果"])
        
        result_layout.addWidget(self.result_table)
        result_group.setLayout(result_layout)
        
        # 可视化区域
        viz_group = QGroupBox("结果可视化")
        viz_layout = QVBoxLayout()
        
        self.figure = plt.figure(figsize=(6, 4))
        self.canvas = FigureCanvas(self.figure)
        
        viz_layout.addWidget(self.canvas)
        viz_group.setLayout(viz_layout)
        
        right_panel.addWidget(result_group)
        right_panel.addWidget(viz_group)
        
        # 添加到主布局
        layout.addLayout(left_panel, 1)
        layout.addLayout(right_panel, 2)
        
        self.setLayout(layout)
    
    def load_model(self):
        """加载模型"""
        try:
            model_name, ok = QFileDialog.getOpenFileName(
                self, "选择模型文件", "", "Model Files (*.pth *.pt)"
            )
            if ok:
                self.model = torch.load(model_name)
                self.model.eval()  # 设置为评估模式
                self.model_info_label.setText(f"已加载模型: {model_name}")
                self.predict_btn.setEnabled(True)
                QMessageBox.information(self, "成功", "模型加载成功！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载模型失败: {str(e)}")

    def load_input_data(self):
        """加载输入数据文件"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择数据文件", "", "CSV Files (*.csv);;Excel Files (*.xlsx *.xls)"
            )
            if file_path:
                if file_path.endswith('.csv'):
                    self.input_data = pd.read_csv(file_path)
                else:
                    self.input_data = pd.read_excel(file_path)

                self.update_input_preview()
                self.update_column_list()
                QMessageBox.information(self, "成功", "数据加载成功！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载数据失败: {str(e)}")

    def update_column_list(self):
        """更新数据列选择列表"""
        if self.input_data is not None:
            self.column_list_widget.setRowCount(len(self.input_data.columns))
            for i, column_name in enumerate(self.input_data.columns):
                item = QTableWidgetItem(column_name)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.column_list_widget.setItem(i, 0, item)

    def apply_selected_columns(self):
        """应用选择的列"""
        if self.input_data is None:
            QMessageBox.warning(self, "警告", "请先导入数据！")
            return

        selected_columns = []
        for row in range(self.column_list_widget.rowCount()):
            item = self.column_list_widget.item(row, 0)
            if item.checkState() == Qt.Checked:
                selected_columns.append(item.text())

        if not selected_columns:
            QMessageBox.warning(self, "警告", "请选择至少一个列！")
            return

        try:
            # 将选中的列保存到 selected_data，不修改 input_data
            self.selected_data = self.input_data[selected_columns]

            # 更新 input_data 的内容为 selected_data
            self.input_data = self.selected_data

            QMessageBox.information(self, "成功", "列选择已应用！")
        except KeyError as e:
            QMessageBox.critical(self, "错误", f"列选择失败: {str(e)}")

    def update_input_preview(self):
        """更新输入数据预览"""
        if self.input_data is not None:
            # 清空表格
            self.result_table.setRowCount(0)
            self.result_table.setColumnCount(len(self.input_data.columns))

            # 设置列名
            for i, column_name in enumerate(self.input_data.columns):
                self.result_table.setHorizontalHeaderItem(i, QTableWidgetItem(column_name))

            # 设置行数据
            self.result_table.setRowCount(len(self.input_data))
            for i in range(len(self.input_data)):
                for j in range(len(self.input_data.columns)):
                    item = QTableWidgetItem(str(self.input_data.iloc[i, j]))
                    self.result_table.setItem(i, j, item)

    def on_task_changed(self, task_type: str):
        """任务类型改变时的处理"""
        if task_type == "分类":
            self.manual_input.setPlaceholderText("输入特征（用逗号分隔）")
        else:
            self.manual_input.setPlaceholderText("输入数值（用逗号分隔）")
    
    def predict(self):
        """执行预测"""
        if self.model is None:
            QMessageBox.warning(self, "警告", "请先加载模型！")
            return
        
        try:
            # 准备输入数据
            if self.input_data is not None:
                input_tensor = torch.FloatTensor(self.input_data.values)
            else:
                # 解析手动输入的数据
                try:
                    input_data = [float(x.strip()) for x in self.manual_input.text().split(",")]
                    input_tensor = torch.FloatTensor([input_data])
                except ValueError:
                    QMessageBox.warning(self, "警告", "请输入有效的数值，并用逗号分隔！")
                    return
            
            # 执行预测
            with torch.no_grad():
                outputs = self.model(input_tensor)
            
            # 处理预测结果
            task_type = self.task_combo.currentText()
            if task_type == "分类":
                predictions = outputs.argmax(dim=1)
            else:
                predictions = outputs.squeeze()
            
            # 显示结果
            self.show_predictions(predictions)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"预测失败: {str(e)}")
    
    def show_predictions(self, predictions):
        """显示预测结果"""
        # 更新结果表格
        if isinstance(predictions, torch.Tensor):
            predictions = predictions.numpy()
        
        rows = len(predictions) if isinstance(predictions, np.ndarray) else 1
        self.result_table.setRowCount(rows)
        
        for i in range(rows):
            pred = predictions[i] if isinstance(predictions, np.ndarray) else predictions
            item = QTableWidgetItem(str(pred))
            self.result_table.setItem(i, 1, item)
        
        # 更新可视化
        self.update_visualization(predictions)
    
    def update_visualization(self, predictions):
        """更新预测结果可视化"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        task_type = self.task_combo.currentText()
        if task_type == "分类":
            # 绘制分类结果的条形图
            if isinstance(predictions, np.ndarray):
                unique_classes, counts = np.unique(predictions, return_counts=True)
                ax.bar(unique_classes, counts)
                ax.set_title("分类结果分布")
                ax.set_xlabel("类别")
                ax.set_ylabel("数量")
        else:
            # 绘制回归结果的散点图
            if isinstance(predictions, np.ndarray):
                ax.scatter(range(len(predictions)), predictions)
                ax.set_title("回归预测结果")
                ax.set_xlabel("样本索引")
                ax.set_ylabel("预测值")
        
        self.figure.tight_layout()
        self.canvas.draw() 