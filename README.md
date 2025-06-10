# 无代码神经网络可视化编程平台

一个基于 PyQt5 的无代码神经网络搭建、训练和部署平台，让用户无需编程基础即可轻松构建深度学习模型。

## ✨ 主要功能

- 🔍 **数据分析**：可视化数据分布、统计信息和特征分析
- 🧱 **模型搭建**：拖拽式神经网络层构建，支持多种层类型
- 🎯 **模型训练**：实时训练监控，损失和准确率可视化
- 🚀 **模型应用**：模型推理和结果可视化
- 🤖 **AI助手**：智能模型推荐和参数优化建议
- 👤 **用户管理**：安全的用户注册和登录系统

## 🛠️ 技术栈

- **前端界面**：PyQt5
- **深度学习**：PyTorch
- **数据处理**：Pandas, NumPy
- **数据可视化**：Matplotlib, Seaborn
- **数据库**：SQLite3
- **机器学习**：Scikit-learn
- **AI服务**：OpenAI API

## 📦 安装说明

### 环境要求
- Python 3.8+
- 建议使用虚拟环境

### 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd No-code-Neural-Network-Platform
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 运行程序
```bash
python main.py
```

## 🚀 快速开始

1. **注册账户**：首次使用需要注册新用户账户
2. **登录系统**：使用注册的用户名和密码登录
3. **数据分析**：上传数据集并进行可视化分析
4. **搭建模型**：使用拖拽界面构建神经网络模型
5. **训练模型**：配置训练参数并开始训练
6. **模型应用**：使用训练好的模型进行推理

## 📁 项目结构

```
No-code-Neural-Network-Platform/
├── main.py                 # 程序入口
├── requirements.txt        # 依赖管理
├── database/              # 数据库相关
│   └── db_manager.py      # 数据库管理器
├── models/                # 模型相关
│   ├── neural_network.py  # 神经网络模型
│   └── data_processor.py  # 数据处理器
├── ui/                    # 用户界面
│   ├── main_window.py     # 主窗口
│   ├── login_page.py      # 登录页面
│   ├── data_analysis_page.py    # 数据分析页面
│   ├── model_builder_page.py    # 模型搭建页面
│   ├── training_page.py         # 训练页面
│   ├── inference_page.py        # 推理页面
│   └── ai_assistance.py         # AI助手
└── utils/                 # 工具类
    └── visualizer.py      # 可视化工具
```

## 🔐 安全特性

- 使用 bcrypt 进行密码哈希存储
- 用户数据隔离，只能访问自己的模型和数据
- 参数化查询防止 SQL 注入

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🐛 问题反馈

如果您遇到任何问题，请通过以下方式联系：

- 提交 [Issue](../../issues)
- 发送邮件至 [your-email@example.com]

## 🔧 开发计划

- [ ] 支持更多神经网络层类型
- [ ] 添加模型部署功能
- [ ] 支持分布式训练
- [ ] 增加模型压缩和优化功能
- [ ] 添加更多数据预处理选项
