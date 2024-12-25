from openai import OpenAI
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, 
                           QPushButton, QHBoxLayout, QTabWidget,
                           QLabel, QComboBox, QSpinBox, QDoubleSpinBox,
                           QFormLayout, QMessageBox, QLineEdit)
import json
import sqlite3
import os

class NetworkGeneratorWidget(QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout()
        
        #模型名字
        self.name = QLineEdit()
        self.name.setPlaceholderText("请输入模型名字")
        layout.addRow("模型名字:", self.name)

        # 任务类型选择
        self.task_type = QComboBox()
        self.task_type.addItems(["图像分类", "目标检测", "图像分割", 
                                "文本分类", "序列预测", "自然语言处理"])
        layout.addRow("任务类型:", self.task_type)
        
        # 数据规模设置
        self.data_size = QSpinBox()
        self.data_size.setRange(100, 1000000)
        self.data_size.setValue(10000)
        layout.addRow("数据规模:", self.data_size)
        
        # 模型复杂度设置
        self.model_complexity = QComboBox()
        self.model_complexity.addItems(["简单", "中等", "复杂"])
        layout.addRow("模型复杂度:", self.model_complexity)
        
        # 训练时间预算
        self.time_budget = QSpinBox()
        self.time_budget.setRange(1, 72)
        self.time_budget.setValue(24)
        layout.addRow("训练时间预算(小时):", self.time_budget)
        
        # 特殊需求输入
        self.special_requirements = QTextEdit()
        self.special_requirements.setMaximumHeight(100)
        layout.addRow("特殊需求:", self.special_requirements)
        
        # 生成按钮
        self.generate_button = QPushButton("生成神经网络")
        self.generate_button.clicked.connect(self.generate_network)
        layout.addRow(self.generate_button)
        
        # 生成结果显示
        self.generation_result = QTextEdit()
        self.generation_result.setReadOnly(True)
        layout.addRow("生成结果:", self.generation_result)
        
        self.setLayout(layout)

    def generate_network(self):
        try:
            prompt = f"""请为以下需求生成一个神经网络模型架构:
            任务类型: {self.task_type.currentText()}
            数据规模: {self.data_size.value()}
            模型复杂度: {self.model_complexity.currentText()}
            训练时间预算: {self.time_budget.value()}小时
            特殊需求: {self.special_requirements.toPlainText()}
            
            请仅返回一个JSON格式的神经网络架构，格式如下
            {{
                "layers": [
                    {{
                        "type": "卷积层",
                        "params": {{
                            "kernel_size": [3, 3],
                            "filters": 32,
                            "stride": 1,
                            "padding": "same"
                        }}
                    }},
                    {{
                        "type": "池化层",
                        "params": {{
                            "pool_size": [2, 2],
                            "stride": 2,
                            "pool_type": "max"
                        }}
                    }}
                ],
                "parameters": {{}}
            }}

            要求：
            1. 只返回JSON格式数据，不要包含任何其他文字
            2. 所有层的type必须使用中文：卷积层、池化层、全连接层、批归一化层、激活层等
            3. params中包含该层所需的所有参数
            4. 必须包含parameters字段，通常为空对象
            5. 根据任务类型和复杂度要求生成合适的网络结构
            """
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个神经网络架构家。请只返回JSON格式的模型架构，不要包含任何其他说明文字。"},
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
            
            # 获取响应内容并清理
            content = response.choices[0].message.content.strip()
            # 如果响应包含多余的内容，只保留JSON部分
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].strip()
            
            # 解析JSON并验证
            try:
                model_spec = json.loads(content)
            except json.JSONDecodeError as e:
                raise ValueError(f"生成的内容不是有效的JSON格式: {str(e)}\n内容: {content}")
            
            # 验证基本结构
            if not isinstance(model_spec, dict) or 'layers' not in model_spec:
                raise ValueError("生成的模型缺少layers字段")
            
            # 验证每一层的格式
            for layer in model_spec['layers']:
                if not isinstance(layer, dict) or 'type' not in layer or 'params' not in layer:
                    raise ValueError("层定义格式不正确")
                
            # 保存到数据库
            model_id = self.save_to_database(model_spec)
            
            # 生成实现文件
            self.generate_implementation_files(model_id, model_spec)
            
            # 显示结果（确保中文正确显示）
            formatted_result = json.dumps(model_spec, indent=2, ensure_ascii=False)
            self.generation_result.setText(formatted_result)
            
            QMessageBox.information(self, "成功", 
                f"神经网络模型已生成并保存!\n模型ID: {model_id}")
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"生成失败: {str(e)}")
    
    def validate_model_spec(self, model_spec):
        """验证模型规范的完整性"""
        if "layers" not in model_spec:
            raise ValueError("模型规范缺少layers定义")
        
        if "parameters" not in model_spec:
            raise ValueError("模型规范缺少parameters字段")
        
        if not isinstance(model_spec["layers"], list):
            raise ValueError("layers必须是列表类型")
        
        if not isinstance(model_spec["parameters"], dict):
            raise ValueError("parameters必须是字典类型")
        
        for layer in model_spec["layers"]:
            if "type" not in layer:
                raise ValueError("层定义缺少type字段")
            if "params" not in layer:
                raise ValueError("层定义缺少params字段")
            if not isinstance(layer["params"], dict):
                raise ValueError("params必须是字典类型")
    
    def generate_implementation_files(self, model_id, model_spec):
        """生成模型实现文件"""
        try:
            # 创建模型目录
            model_dir = f"generated_models/model_{model_id}"
            os.makedirs(model_dir, exist_ok=True)
            
            # 生成模型实现文件
            model_code = self.generate_model_code(model_spec)
            with open(f"{model_dir}/model.py", "w", encoding="utf-8") as f:
                f.write(model_code)
            
            # 生成配置文件
            with open(f"{model_dir}/config.json", "w", encoding="utf-8") as f:
                json.dump(model_spec, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            raise Exception(f"生成实现文件失败: {str(e)}")
    
    def generate_model_code(self, model_spec):
        """根据模型规范生成PyTorch代码"""
        code = """import torch
import torch.nn as nn
import torch.nn.functional as F

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        
        # 定义网络层
"""
        
        # 计算特征图大小的辅助变量
        current_channels = 3  # 默认输入通道数
        current_size = 224   # 默认输入大小
        
        # 添加层定义
        for i, layer in enumerate(model_spec["layers"]):
            if layer["type"] == "卷积层":
                params = layer["params"]
                in_channels = current_channels
                out_channels = params['filters']
                code += f"        self.conv{i} = nn.Conv2d(in_channels={in_channels}, "
                code += f"out_channels={out_channels}, "
                code += f"kernel_size={params['kernel_size']}, "
                code += f"stride={params.get('stride', 1)}, "
                code += f"padding='{params.get('padding', 'valid')}')\n"
                current_channels = out_channels
                
            elif layer["type"] == "池化层":
                params = layer["params"]
                if params.get("pool_type", "max") == "max":
                    code += f"        self.pool{i} = nn.MaxPool2d("
                else:
                    code += f"        self.pool{i} = nn.AvgPool2d("
                code += f"kernel_size={params['pool_size']}, "
                code += f"stride={params.get('stride', None)})\n"
                
                # 更新特征图大小
                pool_size = params['pool_size'][0] if isinstance(params['pool_size'], list) else params['pool_size']
                current_size = current_size // pool_size
                
            elif layer["type"] == "全连接层":
                params = layer["params"]
                if i == 0 or model_spec["layers"][i-1]["type"] not in ["全连接层", "展平层"]:
                    # 如果是第一个全连接层，需要先计算输入特征数
                    in_features = current_channels * current_size * current_size
                    code += f"        self.flatten{i} = nn.Flatten()\n"
                else:
                    in_features = prev_units
                    
                units = params['units']
                code += f"        self.fc{i} = nn.Linear(in_features={in_features}, "
                code += f"out_features={units})\n"
                prev_units = units
                
            elif layer["type"] == "批归一化层":
                params = layer["params"]
                code += f"        self.bn{i} = nn.BatchNorm2d({current_channels})\n"
                
            elif layer["type"] == "展平层":
                code += f"        self.flatten{i} = nn.Flatten()\n"
                in_features = current_channels * current_size * current_size
                
        # 添加前向传播函数
        code += "\n    def forward(self, x):\n"
        for i, layer in enumerate(model_spec["layers"]):
            if layer["type"] == "卷积层":
                code += f"        x = self.conv{i}(x)\n"
            elif layer["type"] == "池化层":
                code += f"        x = self.pool{i}(x)\n"
            elif layer["type"] == "全连接层":
                if i == 0 or model_spec["layers"][i-1]["type"] not in ["全连接层", "展平层"]:
                    code += f"        x = self.flatten{i}(x)\n"
                code += f"        x = self.fc{i}(x)\n"
            elif layer["type"] == "批归一化层":
                code += f"        x = self.bn{i}(x)\n"
            elif layer["type"] == "展平层":
                code += f"        x = self.flatten{i}(x)\n"
            
            # 添加激活函数
            if "activation" in layer.get("params", {}):
                activation = layer["params"]["activation"]
                if activation == "relu":
                    code += "        x = F.relu(x)\n"
                elif activation == "sigmoid":
                    code += "        x = torch.sigmoid(x)\n"
                elif activation == "tanh":
                    code += "        x = torch.tanh(x)\n"
            
        code += "        return x\n"
        return code
    
    def save_to_database(self, model_spec):
        conn = sqlite3.connect('neural_network.db')
        cursor = conn.cursor()
        
        # 创建表（如果不存在）
        cursor.execute('''CREATE TABLE IF NOT EXISTS models
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT NOT NULL,              -- 模型名称
                          architecture TEXT NOT NULL,       -- 模型架构（JSON格式）
                          parameters TEXT NOT NULL DEFAULT '{}',  -- 模型参数（JSON格式）
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        try:
            # 将模型规范转换为JSON字符串，确保中文正确存储
            architecture_json = json.dumps({"layers": model_spec["layers"]}, ensure_ascii=False)
            parameters_json = json.dumps(model_spec.get("parameters", {}), ensure_ascii=False)
            
            # 获取模型名称
            model_name = self.name.text().strip()
            if not model_name:
                raise ValueError("请输入模型名称")
            
            # 插入数据
            cursor.execute('''INSERT INTO models
                             (name, architecture, parameters)
                             VALUES (?, ?, ?)''',
                          (model_name, architecture_json, parameters_json))
            
            model_id = cursor.lastrowid
            conn.commit()
            return model_id
            
        except sqlite3.Error as e:
            QMessageBox.warning(self, "数据库错误", f"保存模型时发生错误: {str(e)}")
            raise
        finally:
            conn.close()

class AIAssistantWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.client = OpenAI(
            api_key="sk-de1daa7af7c74e78b517ef6114d2ce6a",
            base_url="https://api.deepseek.com"
        )
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 创建标签页组件
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # 创建指南页面
        guide_widget = QWidget()
        guide_layout = QVBoxLayout()
        self.guide_text = QTextEdit()
        self.guide_text.setReadOnly(True)
        self.set_guide_content()
        guide_layout.addWidget(self.guide_text)
        guide_widget.setLayout(guide_layout)
        tab_widget.addTab(guide_widget, "使用指南")
        
        # 创建AI对话页面
        chat_widget = QWidget()
        chat_layout = QVBoxLayout()
        
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        chat_layout.addWidget(self.chat_history)
        
        self.user_input = QTextEdit()
        self.user_input.setMaximumHeight(100)
        chat_layout.addWidget(self.user_input)
        
        button_layout = QHBoxLayout()
        self.send_button = QPushButton("发送")
        self.send_button.clicked.connect(self.send_message)
        button_layout.addStretch()
        button_layout.addWidget(self.send_button)
        chat_layout.addLayout(button_layout)
        
        chat_widget.setLayout(chat_layout)
        tab_widget.addTab(chat_widget, "AI对话")
        
        # 添加神经网络生成器页面
        generator_widget = NetworkGeneratorWidget(self.client)
        tab_widget.addTab(generator_widget, "模型生成器")
        
        self.setLayout(layout)
    
    def set_guide_content(self):
        guide_content = """
# 神经网络可视化编程台使用指南

## 1. 基本功能介绍

### 1.1 数据分析
- 支持导入CSV、TXT等格式的数据文件
- 提供数据预处理功能：归一化、标准化、缺失值处理
- 数据可视化：直方图、散点图、相关性分析等

### 1.2 模型搭建
常用层说明：
1. 卷积层(Conv2D)：
   - 输入格式：[批次大小, 高度, 宽度, 通道数]
   - 参数说明：
     * filters：卷积核数量
     * kernel_size：卷积核大小，如(3,3)
     * strides：步长，默认(1,1)
     * padding：填充方式，'valid'或'same'

2. 池化层(MaxPooling2D)：
   - 输入格式：同卷积层
   - 参数说明：
     * pool_size：池化窗口大小，如(2,2)
     * strides：步长，默认与pool_size相同

3. 全连接层(Dense)：
   - 输入格式：[批次大小, 特征数量]
   - 参数说明���
     * units：输出维度
     * activation：激活函数，如'relu'、'sigmoid'

### 1.3 模型训练
训练参数设置：
- batch_size：批训练样本数量
- epochs：训练轮数
- learning_rate：学习率，建议范围0.1~0.0001
- optimizer：优化器选择（Adam、SGD等）

### 1.4 模型应用
- 支持模型保存和加载
- 批量数据预测
- 单样本预测

## 2. 使用技巧

### 2.1 数据预处理建议
- 进行数据归一化可以提高模型训练效率
- 检查并处理异常值和缺失值
- 合理划分训练集和测试集（建议比例8:2）

### 2.2 模型构建建议
- CNN网络建议：Conv -> ReLU -> Pool -> Conv -> ReLU -> Pool -> Dense
- RNN网络建议：Embedding -> LSTM/GRU -> Dense
- 注意防止过拟合：适当使用Dropout层
- 批标准化可以加快训练速度

### 2.3 训练技巧
- 从小学习开始尝试（如0.001）
- 使用早停法防止过拟合
- 监控验证集损失，适时调整参数
- 使用学习率衰减可提高模型性能

## 3. AI助手使用说明
- 在"AI对话"标签页中提问
- 可以询问具体的代码实现方式
- 可以请求解释报错信息
- 支持中文对话

如需更详细的帮助，请在AI对话页面提问。
"""
        self.guide_text.setMarkdown(guide_content)
        
    def send_message(self):
        user_message = self.user_input.toPlainText().strip()
        if not user_message:
            return
            
        # 显示用户消息
        self.chat_history.append(f"你: {user_message}")
        
        try:
            # 使用新的API调用方式
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个专业的深度学习助手,可以帮助用户解决神经网络相关问题。"},
                    {"role": "user", "content": user_message}
                ],
                stream=False
            )
            
            # 获取AI回复
            ai_response = response.choices[0].message.content
            self.chat_history.append(f"AI助手: {ai_response}\n")
            
        except Exception as e:
            self.chat_history.append(f"错误: {str(e)}\n")
            
        # 清空输入框
        self.user_input.clear() 