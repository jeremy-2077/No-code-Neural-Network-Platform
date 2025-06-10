from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QComboBox, QFileDialog, QTableWidget, QTableWidgetItem,
                            QLabel, QGroupBox, QFormLayout, QMessageBox, QScrollArea)
from PyQt5.QtCore import Qt
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from utils.visualizer import DataVisualizer
from models.data_processor import DataProcessor

class DataAnalysisPage(QWidget):
    def __init__(self):
        super().__init__()
        self.data_processor = DataProcessor()
        self.visualizer = DataVisualizer()
        self.df = None
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout()
        
        # 创建左侧滚动区域
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setMinimumWidth(300)
        left_scroll.setMaximumWidth(400)
        
        # 左侧面板容器：数据导入和预处理
        left_container = QWidget()
        left_panel = QVBoxLayout(left_container)
        
        # 数据导入部分
        import_group = QGroupBox("数据导入")
        import_layout = QVBoxLayout()
        self.import_btn = QPushButton("导入数据")
        self.import_btn.clicked.connect(self.import_data)
        import_layout.addWidget(self.import_btn)
        import_group.setLayout(import_layout)
        
        # 预处理选项部分
        preprocess_group = QGroupBox("数据预处理")
        preprocess_layout = QFormLayout()
        
        self.normalize_combo = QComboBox()
        self.normalize_combo.addItems(["无", "标准化", "归一化", "最大最小缩放"])
        
        self.missing_combo = QComboBox()
        self.missing_combo.addItems(["无", "删除", "均值填充", "中位数填充"])
        
        self.feature_combo = QComboBox()
        self.feature_combo.addItems(["无", "主成分分析(PCA)", "特征选择"])
        
        preprocess_layout.addRow("标准化方法:", self.normalize_combo)
        preprocess_layout.addRow("缺失值处理:", self.missing_combo)
        preprocess_layout.addRow("特征工程:", self.feature_combo)
        
        self.apply_btn = QPushButton("应用预处理")
        self.apply_btn.clicked.connect(self.apply_preprocessing)
        preprocess_layout.addRow(self.apply_btn)
        
        preprocess_group.setLayout(preprocess_layout)
        
        # 可视化选项部分
        viz_group = QGroupBox("数据可视化")
        viz_layout = QFormLayout()
        
        self.plot_type_combo = QComboBox()
        self.plot_type_combo.addItems(["折线图", "柱状图", "散点图", "箱线图", "相关性热图"])
        
        self.x_axis_combo = QComboBox()
        self.y_axis_combo = QComboBox()
        
        self.plot_btn = QPushButton("生成图表")
        self.plot_btn.clicked.connect(self.plot_data)
        
        viz_layout.addRow("Graph:", self.plot_type_combo)
        viz_layout.addRow("X:", self.x_axis_combo)
        viz_layout.addRow("Y:", self.y_axis_combo)
        viz_layout.addRow(self.plot_btn)
        
        viz_group.setLayout(viz_layout)
        
        left_panel.addWidget(import_group)
        left_panel.addWidget(preprocess_group)
        left_panel.addWidget(viz_group)
        left_panel.addStretch()
        
        # 设置左侧容器到滚动区域
        left_scroll.setWidget(left_container)
        
        # 右侧面板：数据预览和可视化结果
        right_panel = QVBoxLayout()
        
        # 数据预览表格
        self.data_table = QTableWidget()
        self.data_table.setMaximumHeight(250)  # 限制表格高度
        
        # 可视化结果显示区域
        self.figure = plt.figure(figsize=(5, 3))  # 减小图表尺寸
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumSize(300, 200)  # 设置最小尺寸
        
        right_panel.addWidget(QLabel("数据预览"))
        right_panel.addWidget(self.data_table)
        right_panel.addWidget(QLabel("可视化结果"))
        right_panel.addWidget(self.canvas)
        
        # 添加左右面板到布局
        layout.addWidget(left_scroll)  # 添加滚动区域
        layout.addLayout(right_panel, 2)  # 右侧占更多空间
        
        self.setLayout(layout)
    
    def import_data(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择数据文件", "", "CSV Files (*.csv);;Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.df = pd.read_csv(file_path)
                else:
                    self.df = pd.read_excel(file_path)
                self.update_data_preview()
                self.update_column_combos()
                QMessageBox.information(self, "成功", "数据导入成功！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导入数据错误: {str(e)}")
    
    def update_data_preview(self):
        if self.df is not None:
            self.data_table.setRowCount(min(100, len(self.df)))
            self.data_table.setColumnCount(len(self.df.columns))
            self.data_table.setHorizontalHeaderLabels(self.df.columns)
            
            for i in range(min(100, len(self.df))):
                for j in range(len(self.df.columns)):
                    item = QTableWidgetItem(str(self.df.iloc[i, j]))
                    self.data_table.setItem(i, j, item)
    
    def update_column_combos(self):
        if self.df is not None:
            self.x_axis_combo.clear()
            self.y_axis_combo.clear()
            self.x_axis_combo.addItems(self.df.columns)
            self.y_axis_combo.addItems(self.df.columns)
    
    def apply_preprocessing(self):
        if self.df is not None:
            try:
                # 获取预处理选项
                normalize_method = self.normalize_combo.currentText()
                missing_method = self.missing_combo.currentText()
                feature_method = self.feature_combo.currentText()
                
                # 应用预处理
                self.df = self.data_processor.process_data(
                    self.df,
                    normalize_method,
                    missing_method,
                    feature_method
                )
                
                # 更新预览
                self.update_data_preview()
                self.update_column_combos()
                QMessageBox.information(self, "成功", "数据预处理完成！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"预处理错误: {str(e)}")
        else:
            QMessageBox.warning(self, "警告", "请先导入数据！")
    
    def plot_data(self):
        if self.df is not None:
            plot_type = self.plot_type_combo.currentText()
            x_col = self.x_axis_combo.currentText()
            y_col = self.y_axis_combo.currentText()
            
            # 清除之前的图形
            self.figure.clear()
            
            # 绘制新图形
            self.visualizer.plot_data(
                self.figure,
                self.df,
                plot_type,
                x_col,
                y_col
            )
            
            # 更新画布
            self.canvas.draw() 