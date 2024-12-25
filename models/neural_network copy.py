import json
import torch
import torch.nn as nn
from typing import List, Dict, Any
from database.db_manager import DatabaseManager

class NNLayer:
    def __init__(self, layer_type: str, params: Dict[str, Any]):
        self.type = layer_type
        self.params = params
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "params": self.params
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NNLayer':
        return cls(data["type"], data["params"])
    
    def to_pytorch(self) -> nn.Module:
        """将层配置转换为PyTorch层"""
        if self.type == "Conv2d":
            # 处理padding参数
            if "padding" in self.params:
                if isinstance(self.params["padding"], str):
                    if self.params["padding"] == "same":
                        # 计算same padding的具体数值
                        kernel_size = self.params.get("kernel_size", 1)
                        if isinstance(kernel_size, int):
                            self.params["padding"] = kernel_size // 2
                        elif isinstance(kernel_size, tuple):
                            self.params["padding"] = tuple(k // 2 for k in kernel_size)
                    else:
                        # 如果不是"same"，则设置为0
                        self.params["padding"] = 0
            return nn.Conv2d(**self.params)
        elif self.type == "MaxPool2d":
            return nn.MaxPool2d(**self.params)
        elif self.type == "AvgPool2d":
            return nn.AvgPool2d(**self.params)
        elif self.type == "Linear":
            return nn.Linear(**self.params)
        elif self.type == "Relu":
            return nn.ReLU(inplace=True)
        elif self.type == "Sigmoid":
            return nn.Sigmoid()
        elif self.type == "Tanh":
            return nn.Tanh()
        else:
            raise ValueError(f"不支持的层类型: {self.type}")

class NNModel(nn.Module):
    def __init__(self):
        super(NNModel, self).__init__()
        self.layers: List[NNLayer] = []
        self.db = DatabaseManager()
        self.pytorch_layers = nn.ModuleList()
        self.task_type = "classification"  # 默认为分类任务
    
    def set_task(self, task_type: str):
        """设置任务类型：'classification' 或 'regression'"""
        self.task_type = task_type
    
    def add_layer(self, layer: NNLayer):
        self.layers.append(layer)
        self.pytorch_layers.append(layer.to_pytorch())
    
    def forward(self, x):
        # 确保输入是浮点类型
        if not isinstance(x, torch.FloatTensor) and not isinstance(x, torch.cuda.FloatTensor):
            x = x.float()
        
        for layer in self.pytorch_layers:
            x = layer(x)
        return x
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "layers": [layer.to_dict() for layer in self.layers],
            "task_type": self.task_type
        }
    
    def save(self, name: str = "default_model"):
        """保存模型到数据库"""
        model_data = json.dumps(self.to_dict())
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO models (name, architecture, parameters)
                VALUES (?, ?, ?)
                """,
                (name, model_data, "{}")
            )
        # 同时保存PyTorch模型参数
        torch.save({
            'state_dict': self.state_dict(),
            'task_type': self.task_type
        }, f"{name}.pth")
    
    @classmethod
    def load(cls, model_id: int = None) -> 'NNModel':
        """从数据库加载模型"""
        model = cls()
        model_data = model.db.get_model_by_id(model_id)
        if model_data:
            data = json.loads(model_data["architecture"])
            model.task_type = data.get("task_type", "classification")
            for layer_data in data["layers"]:
                model.add_layer(NNLayer.from_dict(layer_data))
            # 加载模型参数
            try:
                checkpoint = torch.load(f"{model_data['name']}.pth")
                if isinstance(checkpoint, dict):
                    model.load_state_dict(checkpoint['state_dict'])
                    model.task_type = checkpoint.get('task_type', 'classification')
                else:
                    model.load_state_dict(checkpoint)
            except:
                pass
            return model
        raise Exception("找不到指定的模型") 