import json
import torch
import torch.nn as nn
from typing import List, Dict, Any
from database.db_manager import DatabaseManager
import os

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
        self.user_id = None
    
    def add_layer(self, layer: NNLayer):
        self.layers.append(layer)
        self.pytorch_layers.append(layer.to_pytorch())
    
    def forward(self, x):
        for layer in self.pytorch_layers:
            x = layer(x)
        return x
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "layers": [layer.to_dict() for layer in self.layers]
        }
    
    def save(self, name: str = "default_model", user_id: int = None):
        """保存模型到数据库，必须指定用户ID"""
        if user_id is None:
            raise ValueError("必须提供用户ID才能保存模型")
            
        self.user_id = user_id
        model_data = json.dumps(self.to_dict())
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            # 检查是否已存在同名模型
            cursor.execute(
                "SELECT id FROM models WHERE user_id=? AND name=?",
                (user_id, name)
            )
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有模型
                cursor.execute(
                    """
                    UPDATE models 
                    SET architecture=?, parameters=?, updated_at=datetime('now', 'localtime')
                    WHERE user_id=? AND name=?
                    """,
                    (model_data, "{}", user_id, name)
                )
            else:
                # 创建新模型
                cursor.execute(
                    """
                    INSERT INTO models (user_id, name, architecture, parameters, created_at)
                    VALUES (?, ?, ?, ?, datetime('now', 'localtime'))
                    """,
                    (user_id, name, model_data, "{}")
                )
        
        # 确保保存目录存在
        save_dir = "models/saved"
        os.makedirs(save_dir, exist_ok=True)
        
        # 保存PyTorch模型参数
        try:
            save_path = os.path.join(save_dir, f"{user_id}_{name}.pth")
            torch.save(self.state_dict(), save_path)
        except Exception as e:
            raise Exception(f"保存模型参数失败: {str(e)}")
    
    @classmethod
    def load(cls, model_id: int = None, user_id: int = None) -> 'NNModel':
        """从数据库加载模型，必须指定用户ID，只能加载用户自己的模型"""
            
        model = cls()
        model.user_id = user_id
        
        with model.db.get_connection() as conn:
            cursor = conn.cursor()
            # 只加载属于该用户的模型
            cursor.execute(
                """
                SELECT id, name, architecture 
                FROM models 
                WHERE id=? AND user_id=?
                """,
                (model_id, user_id)
            )
            model_data = cursor.fetchone()
            
            if model_data:
                model_id, name, architecture = model_data
                data = json.loads(architecture)
                
                # 重建模型结构
                for layer_data in data["layers"]:
                    model.add_layer(NNLayer.from_dict(layer_data))
                
                # 尝试加载模型参数
                save_dir = "models/saved"
                param_path = os.path.join(save_dir, f"{user_id}_{name}.pth")
                if os.path.exists(param_path):
                    try:
                        model.load_state_dict(torch.load(param_path))
                    except Exception as e:
                        print(f"加载模型参数失败: {str(e)}")
                
                return model
            
            raise Exception("找不到指定的模型或无权访问")
    
    def get_user_models(self, user_id: int) -> List[Dict]:
        """获取用户的所有模型"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, name, created_at
                FROM models
                WHERE user_id=?
                ORDER BY created_at DESC
                """,
                (user_id,)
            )
            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "created_at": row[2]
                }
                for row in cursor.fetchall()
            ] 