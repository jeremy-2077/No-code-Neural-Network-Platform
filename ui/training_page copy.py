from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QGroupBox, QFormLayout, QSpinBox, QComboBox,
                            QProgressBar, QCheckBox, QDoubleSpinBox, QMessageBox,
                            QFileDialog, QDialog, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader  # 添加这行
from models.neural_network import NNModel
from utils.visualizer import DataVisualizer
import pandas as pd
from datetime import datetime

class TrainingThread(QThread):
    """训练线程"""
    progress_updated = pyqtSignal(int, dict)  # 进度信号
    training_finished = pyqtSignal(dict)  # 完成信号
    error_occurred = pyqtSignal(str)  # 错误信号
    
    def __init__(self, model, train_params, data):
        super().__init__()
        self.model = model
        self.train_params = train_params
        self.data = data
        self.is_running = True
    
    def run(self):
        try:
            # 设置设备
            device = torch.device("cuda" if self.train_params["use_gpu"] and 
                                torch.cuda.is_available() else "cpu")
            self.model = self.model.to(device)
            
            # 获取优化器
            optimizer = self.get_optimizer(self.train_params["optimizer"])
            
            # 获取损失函数
            criterion = self.get_criterion(self.train_params["loss_function"])
            
            # 训练循环
            epochs = self.train_params["epochs"]
            history = {"loss": [], "val_loss": [], "accuracy": [], "val_accuracy": []}
            
            for epoch in range(epochs):
                if not self.is_running:
                    break
                
                # 训练模式
                self.model.train()
                running_loss = 0.0
                correct = 0
                total = 0
                
                # 训练一个epoch
                for i, (inputs, targets) in enumerate(self.data["train_loader"]):
                    inputs, targets = inputs.to(device), targets.to(device)
                    
                    optimizer.zero_grad()
                    outputs = self.model(inputs)
                    loss = criterion(outputs, targets)
                    loss.backward()
                    optimizer.step()
                    
                    running_loss += loss.item()
                    _, predicted = outputs.max(1)
                    total += targets.size(0)
                    correct += predicted.eq(targets).sum().item()
                
                # 验证模式
                self.model.eval()
                val_loss = 0.0
                val_correct = 0
                val_total = 0
                
                with torch.no_grad():
                    for inputs, targets in self.data["val_loader"]:
                        inputs, targets = inputs.to(device), targets.to(device)
                        outputs = self.model(inputs)
                        loss = criterion(outputs, targets)
                        
                        val_loss += loss.item()
                        _, predicted = outputs.max(1)
                        val_total += targets.size(0)
                        val_correct += predicted.eq(targets).sum().item()
                
                # 更新历史记录
                history["loss"].append(running_loss / len(self.data["train_loader"]))
                history["val_loss"].append(val_loss / len(self.data["val_loader"]))
                history["accuracy"].append(100. * correct / total)
                history["val_accuracy"].append(100. * val_correct / val_total)
                
                # 发送进度信号
                progress = int((epoch + 1) / epochs * 100)
                self.progress_updated.emit(progress, history)
            
            self.training_finished.emit(history)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def get_optimizer(self, optimizer_name: str):
        """获取优化器"""
        optimizers = {
            "SGD": optim.SGD,
            "Adam": optim.Adam,
            "RMSprop": optim.RMSprop
        }
        return optimizers[optimizer_name](self.model.parameters(), 
                                        lr=self.train_params["learning_rate"])
    
    def get_criterion(self, loss_name: str):
        """获取损失函数"""
        criteria = {
            "CrossEntropyLoss": nn.CrossEntropyLoss,
            "MSELoss": nn.MSELoss,
            "BCELoss": nn.BCELoss
        }
        return criteria[loss_name]()
    
    def stop(self):
        """停止训练"""
        self.is_running = False

class ModelSelectDialog(QDialog):
    """模型选择对话框"""
    def __init__(self, models, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择模型")
        self.setModal(True)
        self.selected_model_id = None
        
        layout = QVBoxLayout()
        
        # 模型列表
        self.list_widget = QListWidget()
        for model_id, name, created_at in models:
            try:
                # 将日期时间字符串转换为 datetime 对象
                if created_at:
                    created_time = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    # 将 datetime 对象格式化为字符串，以便显示
                    created_time_str = created_time.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    created_time_str = "未知时间"
            except (ValueError, TypeError):
                created_time_str = "未知时间"

            # 创建 QListWidgetItem 并设置其文本和数据
            item = QListWidgetItem(f"{name} (创建时间: {created_time_str})")
            item.setData(Qt.UserRole, model_id)  # 将模型ID设置为用户数据，以便后续使用
            self.list_widget.addItem(item)  # 将项添加到列表中
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addWidget(self.list_widget)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def get_selected_model_id(self):
        """获取选中的模型ID"""
        current_item = self.list_widget.currentItem()
        if current_item:
            return current_item.data(Qt.UserRole)
        return None

class TrainingPage(QWidget):
    def __init__(self):
        super().__init__()
        self.model = None
        self.training_thread = None
        self.visualizer = DataVisualizer()
        self.data = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout()
        
        # 左侧训练参数面板
        left_panel = QVBoxLayout()
        
        # 模型加载组
        model_group = QGroupBox("模型加载")
        model_layout = QVBoxLayout()
        
        self.load_model_btn = QPushButton("加载已保存的模型")
        self.load_model_btn.clicked.connect(self.load_model)
        
        self.model_info_label = QLabel("未加载模型")
        
        model_layout.addWidget(self.load_model_btn)
        model_layout.addWidget(self.model_info_label)
        model_group.setLayout(model_layout)
        
        # 数据加载组
        data_group = QGroupBox("数据加载")
        data_layout = QVBoxLayout()
        
        self.load_data_btn = QPushButton("加载训练数据")
        self.load_data_btn.clicked.connect(self.load_training_data)
        
        self.data_info_label = QLabel("未加载数据")
        
        data_layout.addWidget(self.load_data_btn)
        data_layout.addWidget(self.data_info_label)
        data_group.setLayout(data_layout)
        
        # 超参数设置组
        hyperparams_group = QGroupBox("超参数设置")
        hyperparams_layout = QFormLayout()
        
        # 学习率
        self.lr_spin = QDoubleSpinBox()
        self.lr_spin.setRange(0.00001, 1.0)
        self.lr_spin.setSingleStep(0.0001)
        self.lr_spin.setValue(0.001)
        hyperparams_layout.addRow("学习率:", self.lr_spin)
        
        # 批次大小
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(1, 1024)
        self.batch_size_spin.setValue(32)
        hyperparams_layout.addRow("批次大小:", self.batch_size_spin)
        
        # 训练轮数
        self.epochs_spin = QSpinBox()
        self.epochs_spin.setRange(1, 1000)
        self.epochs_spin.setValue(10)
        hyperparams_layout.addRow("训练轮数:", self.epochs_spin)
        
        hyperparams_group.setLayout(hyperparams_layout)
        
        # 训练设置组
        training_group = QGroupBox("训练设置")
        training_layout = QFormLayout()
        
        # 优化器选择
        self.optimizer_combo = QComboBox()
        self.optimizer_combo.addItems(["SGD", "Adam", "RMSprop"])
        training_layout.addRow("优化器:", self.optimizer_combo)
        
        # 损失函数选择
        self.loss_combo = QComboBox()
        self.loss_combo.addItems(["CrossEntropyLoss", "MSELoss", "BCELoss"])
        training_layout.addRow("损失函数:", self.loss_combo)
        
        # GPU加速选项
        self.gpu_check = QCheckBox("使用GPU加速")
        self.gpu_check.setChecked(torch.cuda.is_available())
        training_layout.addRow(self.gpu_check)
        
        training_group.setLayout(training_layout)
        
        # 训练控制组
        control_group = QGroupBox("训练控制")
        control_layout = QVBoxLayout()
        
        self.start_btn = QPushButton("开始训练")
        self.start_btn.clicked.connect(self.start_training)
        
        self.stop_btn = QPushButton("停止训练")
        self.stop_btn.clicked.connect(self.stop_training)
        self.stop_btn.setEnabled(False)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.progress_bar)
        
        control_group.setLayout(control_layout)
        
        # 添加保存模型按钮
        self.save_model_btn = QPushButton("保存模型")
        self.save_model_btn.clicked.connect(self.save_model)
        model_layout.addWidget(self.save_model_btn)  # 将按钮添加到模型加载组
        
        left_panel.addWidget(model_group)  # 添加到左侧面板最上方
        left_panel.addWidget(data_group)
        left_panel.addWidget(hyperparams_group)
        left_panel.addWidget(training_group)
        left_panel.addWidget(control_group)
        left_panel.addStretch()
        
        # 右侧训练可视化面板
        right_panel = QVBoxLayout()
        
        # 训练曲线图
        self.figure = plt.figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        
        right_panel.addWidget(QLabel("训练过程可视化"))
        right_panel.addWidget(self.canvas)
        
        # 添加到主布局
        layout.addLayout(left_panel, 1)
        layout.addLayout(right_panel, 2)
        
        self.setLayout(layout)
    
    def load_model(self):
        """加载已保存的模型"""
        try:
            # 获取所有模型
            models = self.model.db.get_all_models() if self.model else NNModel().db.get_all_models()
            
            if not models:
                QMessageBox.warning(self, "警告", "没有找到已保存的模型！")
                return
            
            # 显示模型选择对话框
            dialog = ModelSelectDialog(models, self)
            if dialog.exec_() == QDialog.Accepted:
                model_id = dialog.get_selected_model_id()
                if model_id:
                    model = NNModel.load(model_id)
                    self.set_model(model)
                    QMessageBox.information(self, "成功", "模型加载成功！")
                else:
                    QMessageBox.warning(self, "警告", "请选择一个模型！")
                    
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载模型失败: {str(e)}")
    
    def set_model(self, model):
        """设置要训练的模型"""
        self.model = model
        # 更新UI状态
        self.start_btn.setEnabled(True)
        # 更新模型信息显示
        self.show_model_info()
        # 更新模型信息标签
        if self.model:
            self.model_info_label.setText(f"已加载模型\n层数: {len(self.model.layers)}")
    
    def show_model_info(self):
        """显示模型信息"""
        if self.model:
            info = "当前模型结构:\n"
            for i, layer in enumerate(self.model.layers):
                info += f"Layer {i+1}: {layer.type} - {layer.params}\n"
            QMessageBox.information(self, "模型信息", info)
    
    def load_training_data(self):
        """加载训练数据"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择训练数据", "", "CSV Files (*.csv);;Excel Files (*.xlsx *.xls)"
            )
            if file_path:
                # 加载数据
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)
                
                # 假设最后一列是标签
                X = df.iloc[:, :-1].values
                y = df.iloc[:, -1].values
                
                # 划分训练集和验证集
                from sklearn.model_selection import train_test_split
                X_train, X_val, y_train, y_val = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )
                
                # 创建数据加载器
                from torch.utils.data import TensorDataset, DataLoader
                train_dataset = TensorDataset(
                    torch.FloatTensor(X_train),
                    torch.LongTensor(y_train)
                )
                val_dataset = TensorDataset(
                    torch.FloatTensor(X_val),
                    torch.LongTensor(y_val)
                )
                
                self.data = {
                    "train_loader": DataLoader(
                        train_dataset,
                        batch_size=self.batch_size_spin.value(),
                        shuffle=True
                    ),
                    "val_loader": DataLoader(
                        val_dataset,
                        batch_size=self.batch_size_spin.value(),
                        shuffle=False
                    )
                }
                
                # 更新数据信息
                self.data_info_label.setText(
                    f"已加载数据:\n"
                    f"训练集: {len(X_train)} 样本\n"
                    f"验证集: {len(X_val)} 样本\n"
                    f"特征数: {X.shape[1]}"
                )
                
                QMessageBox.information(self, "成功", "数据加载成功！")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载数据失败: {str(e)}")
    
    def start_training(self):
        """开始训练"""
        if self.model is None:
            QMessageBox.warning(self, "警告", "请先在模型搭建页面创建模型！")
            return
        
        if self.data is None:
            QMessageBox.warning(self, "警告", "请先加载训练数据！")
            return
        
        # 获取训练参数
        train_params = {
            "learning_rate": self.lr_spin.value(),
            "batch_size": self.batch_size_spin.value(),
            "epochs": self.epochs_spin.value(),
            "optimizer": self.optimizer_combo.currentText(),
            "loss_function": self.loss_combo.currentText(),
            "use_gpu": self.gpu_check.isChecked()
        }
        
        # 创建训练线程
        self.training_thread = TrainingThread(self.model, train_params, self.data)
        self.training_thread.progress_updated.connect(self.update_progress)
        self.training_thread.training_finished.connect(self.training_finished)
        self.training_thread.error_occurred.connect(self.handle_error)
        
        # 更新UI状态
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # 开始训练
        self.training_thread.start()
    
    def stop_training(self):
        """停止训练"""
        if self.training_thread and self.training_thread.isRunning():
            self.training_thread.stop()
            self.training_thread.wait()
            self.update_ui_state(False)
    
    def update_progress(self, progress: int, history: dict):
        """更新训练进度和可视化"""
        self.progress_bar.setValue(progress)
        self.update_plots(history)
    
    def training_finished(self, history: dict):
        """训练完成处理"""
        self.update_ui_state(False)
        QMessageBox.information(self, "完成", "训练已完成！")
    
    def handle_error(self, error_msg: str):
        """处理训练错误"""
        self.update_ui_state(False)
        QMessageBox.critical(self, "错误", f"训练出错: {error_msg}")
    
    def update_ui_state(self, is_training: bool):
        """更新UI状态"""
        self.start_btn.setEnabled(not is_training)
        self.stop_btn.setEnabled(is_training)
    
    def update_plots(self, history: dict):
        """更新训练曲线图"""
        self.figure.clear()
        
        # 损失曲线
        ax1 = self.figure.add_subplot(211)
        ax1.plot(history["loss"], label="训练损失")
        ax1.plot(history["val_loss"], label="验证损失")
        ax1.set_title("损失曲线")
        ax1.set_xlabel("Epoch")
        ax1.set_ylabel("Loss")
        ax1.legend()
        
        # 准确率曲线
        ax2 = self.figure.add_subplot(212)
        ax2.plot(history["accuracy"], label="训练准确率")
        ax2.plot(history["val_accuracy"], label="验证准确率")
        ax2.set_title("准确率曲线")
        ax2.set_xlabel("Epoch")
        ax2.set_ylabel("Accuracy (%)")
        ax2.legend()
        
        self.figure.tight_layout()
        self.canvas.draw() 
    
    def save_model(self):
        """保存当前加载的模型"""
        if self.model is None:
            QMessageBox.warning(self, "警告", "没有加载模型，无法保存！")
            return
        
        try:
            # 选择保存路径
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存模型", "", "模型文件 (*.pt);;所有文件 (*)"
            )
            if file_path:
                # 保存模型
                torch.save(self.model.state_dict(), file_path)
                QMessageBox.information(self, "成功", "模型保存成功！")
        
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存模型失败: {str(e)}") 
    
    def train_model(self):
        try:
            # 获取选中的特征列和标签列
            feature_columns = [col for col in self.feature_columns if self.feature_checkboxes[col].isChecked()]
            label_column = self.label_combo.currentText()
            
            # 准备数据
            X = self.data[feature_columns].values
            y = self.data[label_column].values
            
            # 转换为PyTorch张量
            X_tensor = torch.tensor(X, dtype=torch.float32)
            
            # 根据任务类型处理标签数据
            if self.model.task_type == "classification":
                y = y.astype(int)
                y_tensor = torch.tensor(y, dtype=torch.long)
            else:  # regression
                y = y.astype(float)
                y_tensor = torch.tensor(y, dtype=torch.float32).reshape(-1, 1)
            
            # 创建数据加载器
            dataset = TensorDataset(X_tensor, y_tensor)
            train_loader = DataLoader(dataset, batch_size=32, shuffle=True)
            
            # 设置损失函数
            if self.model.task_type == "classification":
                criterion = nn.CrossEntropyLoss()
            else:  # regression
                criterion = nn.MSELoss()
            
            # 设置优化器
            optimizer = optim.Adam(self.model.parameters(), lr=0.001)
            
            # 训练循环
            num_epochs = 10  # 可以通过UI设置
            for epoch in range(num_epochs):
                self.model.train()
                total_loss = 0
                for batch_X, batch_y in train_loader:
                    # 前向传播
                    outputs = self.model(batch_X)
                    loss = criterion(outputs, batch_y)
                    
                    # 反向传播和优化
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()
                    
                    total_loss += loss.item()
                
                # 更新进度条和显示损失
                avg_loss = total_loss / len(train_loader)
                self.update_progress(epoch, num_epochs, avg_loss)
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"训练过程中出错: {str(e)}")
    
    def update_progress(self, epoch, total_epochs, loss):
        progress = int((epoch + 1) / total_epochs * 100)
        self.progress_bar.setValue(progress)
        self.status_label.setText(f"Epoch {epoch+1}/{total_epochs}, Loss: {loss:.4f}") 