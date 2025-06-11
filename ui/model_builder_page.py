import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QGraphicsScene, QGraphicsView, QMessageBox,
                            QGroupBox, QFormLayout, QSpinBox, QComboBox, QLineEdit,
                            QGraphicsItem, QInputDialog, QGraphicsRectItem, QScrollArea)
from PyQt5.QtCore import Qt, QPointF, QRectF, pyqtSignal
from PyQt5.QtGui import (QPainter, QPen, QBrush, QColor, QFont, QLinearGradient, 
                        QPolygonF)
from models.neural_network import NNLayer, NNModel


class LayerItem:
    def __init__(self, layer_type: str, params: dict):
        self.layer_type = layer_type
        self.params = params
        self.pos = QPointF(0, 0)
        self.next_layers = []
        self.prev_layers = []
        # 添加颜色属性
        self.color = self.get_layer_color(layer_type)
    
    @staticmethod
    def get_layer_color(layer_type: str) -> QColor:
        """根据层类型返回对应的颜色"""
        colors = {
            "卷积层": QColor(100, 149, 237),  # 矢车菊蓝
            "池化层": QColor(144, 238, 144),  # 淡绿色
            "全连接层": QColor(255, 182, 193),  # 浅粉色
            "激活函数": QColor(255, 218, 185)  # 蜜桃色
        }
        return colors.get(layer_type, QColor(200, 200, 200))

class ModelBuilderPage(QWidget):
    # 修改信号名称，表示加载了模型
    model_loaded = pyqtSignal(object)  # 发送加载的模型对象
    
    def __init__(self):
        super().__init__()
        self.layers = []
        self.selected_layer = None
        self.drawing_connection = False
        self.connection_start = None
        self.user_id = None  # 添加用户ID属性
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout()
        
        # 左侧工具栏
        tools_panel = QVBoxLayout()
        
        # 层类型选择组
        layer_group = QGroupBox("添加层")
        layer_layout = QVBoxLayout()
        
        # 卷积层按钮
        conv_btn = QPushButton("卷积层")
        conv_btn.clicked.connect(lambda: self.add_layer_dialog("卷积层"))
        
        # 池化层按钮
        pool_btn = QPushButton("池化层")
        pool_btn.clicked.connect(lambda: self.add_layer_dialog("池化层"))
        
        # 全连接层按钮
        dense_btn = QPushButton("全连接层")
        dense_btn.clicked.connect(lambda: self.add_layer_dialog("全连接层"))
        
        # 激活函数层按钮
        activation_btn = QPushButton("激活函数")
        activation_btn.clicked.connect(lambda: self.add_layer_dialog("激活函数"))
        
        layer_layout.addWidget(conv_btn)
        layer_layout.addWidget(pool_btn)
        layer_layout.addWidget(dense_btn)
        layer_layout.addWidget(activation_btn)
        layer_group.setLayout(layer_layout)
        
        # 模型操作按钮
        operation_group = QGroupBox("模型操作")
        operation_layout = QVBoxLayout()
        
        save_btn = QPushButton("保存模型")
        save_btn.clicked.connect(self.save_model)
        
        clear_btn = QPushButton("清空画布")
        clear_btn.clicked.connect(self.clear_canvas)
        
        operation_layout.addWidget(save_btn)
        operation_layout.addWidget(clear_btn)
        operation_group.setLayout(operation_layout)
        
        tools_panel.addWidget(layer_group)
        tools_panel.addWidget(operation_group)
        tools_panel.addStretch()
        
        # 中央画布
        self.scene = QGraphicsScene()
        self.view = ModelBuilderView(self.scene, self)
        self.view.setMinimumSize(400, 300)  # 减小最小尺寸
        
        # 右侧参数面板 - 添加滚动支持
        params_scroll = QScrollArea()
        params_scroll.setWidgetResizable(True)
        params_scroll.setMaximumWidth(300)
        params_scroll.setMinimumWidth(250)
        
        params_container = QWidget()
        params_panel = QVBoxLayout(params_container)
        params_group = QGroupBox("层参数")
        self.params_layout = QFormLayout()
        params_group.setLayout(self.params_layout)
        params_panel.addWidget(params_group)
        params_panel.addStretch()
        
        params_scroll.setWidget(params_container)
        
        # 添加到主布局
        layout.addLayout(tools_panel, 0)  # 固定宽度
        layout.addWidget(self.view, 3)    # 主要空间给画布
        layout.addWidget(params_scroll, 0)  # 固定宽度
        
        self.setLayout(layout)
    
    def add_layer_dialog(self, layer_type: str):
        """添加新层"""
        params = {}
        
        if layer_type == "卷积层":
            params = {
                "in_channels": 1,      # 输入通道数
                "out_channels": 32,    # 输出通道数
                "kernel_size": 3,      # 卷积核大小
                "stride": 1,           # 步长
                "padding": 1           # 填充
            }
        elif layer_type == "池化层":
            params = {
                "mode": "max",         # max 或 avg
                "kernel_size": 2,      # 池化窗口大小
                "stride": 2            # 步长
            }
        elif layer_type == "全连接层":
            params = {
                "in_features": 1024,   # 输入特征数
                "out_features": 128    # 输出特征数
            }
        elif layer_type == "激活函数":
            params = {
                "type": "ReLU"         # ReLU, Tanh, Sigmoid
            }
        
        # 创建新层并添加到模型中
        layer = LayerItem(layer_type, params)
        self.layers.append(layer)
        
        # 如果有前一个层，建立连接
        if self.layers and len(self.layers) > 1:
            prev_layer = self.layers[-2]
            prev_layer.next_layers.append(layer)
            layer.prev_layers.append(prev_layer)
        
        # 更新画布并显示参数
        self.update_canvas()
        self.show_layer_params(layer)
    
    def show_layer_params(self, layer: LayerItem):
        """显示层参数在右侧面板"""
        # 清除现有参数
        while self.params_layout.count():
            child = self.params_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if layer is None:
            return
        
        # 添加层类型标签
        type_label = QLabel(f"层类型: {layer.layer_type}")
        type_label.setStyleSheet("font-weight: bold;")
        self.params_layout.addRow(type_label)
        
        # 根据不同层类型显示对应参数
        if layer.layer_type == "卷积层":
            # 输入通道数
            in_channels = QSpinBox()
            in_channels.setRange(1, 512)
            in_channels.setValue(layer.params["in_channels"])
            in_channels.valueChanged.connect(
                lambda v: self.update_param_and_refresh(layer, "in_channels", v))
            self.params_layout.addRow("输入通道数:", in_channels)
            
            # 输出通道数
            out_channels = QSpinBox()
            out_channels.setRange(1, 512)
            out_channels.setValue(layer.params["out_channels"])
            out_channels.valueChanged.connect(
                lambda v: self.update_param_and_refresh(layer, "out_channels", v))
            self.params_layout.addRow("输出通道数:", out_channels)
            
            # 卷积核大小
            kernel = QSpinBox()
            kernel.setRange(1, 7)
            kernel.setValue(layer.params["kernel_size"])
            kernel.valueChanged.connect(
                lambda v: self.update_param_and_refresh(layer, "kernel_size", v))
            self.params_layout.addRow("卷积核大小:", kernel)
            
            # 步长
            stride = QSpinBox()
            stride.setRange(1, 3)
            stride.setValue(layer.params["stride"])
            stride.valueChanged.connect(
                lambda v: self.update_param_and_refresh(layer, "stride", v))
            self.params_layout.addRow("步长:", stride)
            
            # 填充
            padding = QSpinBox()
            padding.setRange(0, 3)
            padding.setValue(layer.params["padding"])
            padding.valueChanged.connect(
                lambda v: self.update_param_and_refresh(layer, "padding", v))
            self.params_layout.addRow("填充:", padding)
            
        elif layer.layer_type == "池化层":
            # 池化类型
            mode = QComboBox()
            mode.addItems(["max", "avg"])
            mode.setCurrentText(layer.params["mode"])
            mode.currentTextChanged.connect(
                lambda v: self.update_param_and_refresh(layer, "mode", v))
            self.params_layout.addRow("池化类型:", mode)
            
            # 池化窗口大小
            kernel = QSpinBox()
            kernel.setRange(1, 4)
            kernel.setValue(layer.params["kernel_size"])
            kernel.valueChanged.connect(
                lambda v: self.update_param_and_refresh(layer, "kernel_size", v))
            self.params_layout.addRow("窗口大小:", kernel)
            
            # 步长
            stride = QSpinBox()
            stride.setRange(1, 4)
            stride.setValue(layer.params["stride"])
            stride.valueChanged.connect(
                lambda v: self.update_param_and_refresh(layer, "stride", v))
            self.params_layout.addRow("步长:", stride)
            
        elif layer.layer_type == "全连接层":
            # 输入特征数
            in_features = QSpinBox()
            in_features.setRange(1, 10000)
            in_features.setValue(layer.params["in_features"])
            in_features.valueChanged.connect(
                lambda v: self.update_param_and_refresh(layer, "in_features", v))
            self.params_layout.addRow("输入特征数:", in_features)
            
            # 输出特征数
            out_features = QSpinBox()
            out_features.setRange(1, 10000)
            out_features.setValue(layer.params["out_features"])
            out_features.valueChanged.connect(
                lambda v: self.update_param_and_refresh(layer, "out_features", v))
            self.params_layout.addRow("输出特征数:", out_features)
            
        elif layer.layer_type == "激活函数":
            # 激活函数类型
            type_combo = QComboBox()
            type_combo.addItems(["ReLU", "Tanh", "Sigmoid"])
            type_combo.setCurrentText(layer.params["type"])
            type_combo.currentTextChanged.connect(
                lambda v: self.update_param_and_refresh(layer, "type", v))
            self.params_layout.addRow("激活函数:", type_combo)

    def update_param_and_refresh(self, layer: LayerItem, param_name: str, value: any):
        """更新参数并刷新显示"""
        layer.params[param_name] = value
        self.update_canvas()  # 更新画布显示
    
    def update_canvas(self):
        """更新画布显示"""
        self.scene.clear()
        
        # 设置画布背景
        self.scene.setBackgroundBrush(QBrush(QColor(245, 245, 245)))
        
        # 绘制层
        for i, layer in enumerate(self.layers):
            # 设置层的位置
            x_pos = 200
            y_pos = 50 + i * 120
            layer.pos = QPointF(x_pos, y_pos)
            
            # 绘制层的背景矩形
            rect = QGraphicsRectItem(layer.pos.x(), layer.pos.y(), 200, 80)
            rect.setPen(QPen(Qt.black, 2))
            rect.setBrush(QBrush(layer.color))
            rect.setFlag(QGraphicsItem.ItemIsSelectable)
            rect.setFlag(QGraphicsItem.ItemIsMovable)  # 允许移动
            rect.setAcceptHoverEvents(True)
            rect.layer = layer  # 存储层的引用
            self.scene.addItem(rect)  # 先添加到场景
            
            # 添加层的标题
            title = self.scene.addText(layer.layer_type, QFont("Arial", 10, QFont.Bold))
            title.setDefaultTextColor(Qt.black)
            title.setPos(
                layer.pos.x() + (200 - title.boundingRect().width()) / 2,
                layer.pos.y() + 5
            )
            title.setParentItem(rect)  # 设置为矩形的子项
            
            # 添加层的参数信息
            param_text = "\n".join([f"{k}: {v}" for k, v in layer.params.items()])
            params = self.scene.addText(param_text, QFont("Arial", 8))
            params.setDefaultTextColor(Qt.black)
            params.setPos(
                layer.pos.x() + 10,
                layer.pos.y() + 25
            )
            params.setParentItem(rect)  # 设置为矩形的子项
            
            # 绘制连接线（如果有前一个层）
            if layer.prev_layers:
                for prev_layer in layer.prev_layers:
                    start_x = prev_layer.pos.x() + 100
                    start_y = prev_layer.pos.y() + 80
                    end_x = layer.pos.x() + 100
                    end_y = layer.pos.y()
                    
                    # 绘制连接线
                    line = self.scene.addLine(
                        start_x, start_y, end_x, end_y,
                        QPen(Qt.black, 2)
                    )

    def save_model(self):
        """保存模型结构"""
        if self.user_id is None:
            QMessageBox.warning(self, "警告", "请先登录！")
            return

        # 弹出输入对话框，获取用户输入的文件名
        file_name, ok = QInputDialog.getText(self, "保存模型", "请输入模型文件名:", QLineEdit.Normal, "")

        if ok and file_name:  # 确保用户没有取消操作且输入了文件名
            try:
                # 创建模型实例
                model = NNModel()
                
                # 遍历所有层，按顺序添加到模型中
                for layer in self.layers:
                    # 根据层类型创建对应的层实例
                    if layer.layer_type == "卷积层":
                        nn_layer = NNLayer("Conv2d", {
                            "in_channels": layer.params["in_channels"],
                            "out_channels": layer.params["out_channels"],
                            "kernel_size": layer.params["kernel_size"],
                            "stride": layer.params["stride"],
                            "padding": layer.params["padding"]
                        })
                    elif layer.layer_type == "池化层":
                        nn_layer = NNLayer("MaxPool2d" if layer.params["mode"] == "max" else "AvgPool2d", {
                            "kernel_size": layer.params["kernel_size"],
                            "stride": layer.params["stride"]
                        })
                    elif layer.layer_type == "全连接层":
                        nn_layer = NNLayer("Linear", {
                            "in_features": layer.params["in_features"],
                            "out_features": layer.params["out_features"]
                        })
                    elif layer.layer_type == "激活函数":
                        nn_layer = NNLayer(layer.params["type"].capitalize(), {})
                    
                    # 添加层到模型
                    model.add_layer(nn_layer)
                
                # 保存模型，传入用户ID
                model.save(name=file_name, user_id=self.user_id)
                QMessageBox.information(self, "成功", "模型保存成功！")
                
                # 发送模型加载信号
                self.model_loaded.emit(model)
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存模型失败: {str(e)}")
        elif not ok:
            QMessageBox.warning(self, "警告", "保存操作已取消。")
        else:
            QMessageBox.warning(self, "警告", "请输入有效的文件名。")
    
    def clear_canvas(self):
        """清空画布"""
        self.layers = []
        self.scene.clear()
        self.show_layer_params(None)

class ModelBuilderView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.model_builder = parent
        self.setScene(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setSceneRect(0, 0, 600, 400)
        self.setDragMode(QGraphicsView.RubberBandDrag)  # 允许框选
    
    def mousePressEvent(self, event):
        """处理鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            clicked_item = self.scene().itemAt(scene_pos, self.transform())
            
            if isinstance(clicked_item, QGraphicsRectItem) and hasattr(clicked_item, 'layer'):
                print(f"选中层: {clicked_item.layer.layer_type}")
                self.model_builder.show_layer_params(clicked_item.layer)
                
                # 重置所有矩形的画笔
                for item in self.scene().items():
                    if isinstance(item, QGraphicsRectItem):
                        item.setPen(QPen(Qt.black, 2))
                
                # 高亮当前选中的矩形
                clicked_item.setPen(QPen(Qt.blue, 3))
        
        super().mousePressEvent(event) 