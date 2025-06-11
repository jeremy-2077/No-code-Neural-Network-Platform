#!/usr/bin/env python3
"""
测试推理页面模型加载流程
"""
import sys
import os
from unittest.mock import patch, MagicMock
from PyQt5.QtWidgets import QApplication, QDialog

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.inference_page import InferencePage
from models.neural_network import NNModel

def test_inference_load_flow():
    """测试推理页面的模型加载流程"""
    app = QApplication(sys.argv)
    
    # 1. 准备测试环境
    inference_page = InferencePage()
    
    # 2. Mock依赖项
    # Mock NNModel
    mock_model_instance = NNModel()
    mock_model_instance.layers = [MagicMock()] # 模拟非空模型
    
    # Mock get_user_models
    with patch('models.neural_network.NNModel.get_user_models') as mock_get_user_models:
        mock_get_user_models.return_value = [{'id': 1, 'name': 'test_model', 'created_at': '2023-01-01'}]
        
        # Mock load
        with patch('models.neural_network.NNModel.load') as mock_load:
            mock_load.return_value = mock_model_instance
            
            # Mock ModelSelectDialog
            with patch('ui.inference_page.ModelSelectDialog') as mock_dialog:
                mock_dialog_instance = mock_dialog.return_value
                mock_dialog_instance.exec_.return_value = QDialog.Accepted
                mock_dialog_instance.get_selected_model_id.return_value = 1
                
                # Mock QFileDialog
                with patch('ui.inference_page.QFileDialog.getOpenFileName') as mock_file_dialog:
                    mock_file_dialog.return_value = ('/fake/path/model.pth', 'Model Files (*.pth *.pt)')
                    
                    # Mock torch.load
                    with patch('torch.load') as mock_torch_load:
                        mock_torch_load.return_value = {} # 空的state_dict
                        
                        # 3. 执行测试
                        inference_page.load_model()
                        
                        # 4. 验证结果
                        mock_get_user_models.assert_called_once_with(user_id=None)
                        mock_dialog.assert_called()
                        mock_load.assert_called_once_with(model_id=1)
                        mock_file_dialog.assert_called()
                        mock_torch_load.assert_called_once_with('/fake/path/model.pth')
                        
                        assert inference_page.model is not None
                        assert "已加载模型" in inference_page.model_info_label.text()

    print("✅ 测试通过：InferencePage的加载流程符合预期。")

if __name__ == "__main__":
    test_inference_load_flow()
    app.quit() 