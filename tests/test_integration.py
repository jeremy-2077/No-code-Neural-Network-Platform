#!/usr/bin/env python3
"""
集成测试
测试各个组件之间的协作和数据流
"""

import sys
import os
import unittest
import tempfile
import shutil
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from services.user_service import UserService
from database.db_manager import DatabaseManager
from database.connection_pool import DatabaseConnectionPool
from config.config_manager import ConfigManager, AppConfig
from utils.logger import logger


class TestUserServiceIntegration(unittest.TestCase):
    """测试用户服务与数据库的集成"""
    
    def setUp(self):
        # 使用临时数据库
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # 创建测试用的数据库管理器
        self.db_manager = DatabaseManager(self.temp_db.name)
        
        # 创建用户服务实例
        self.user_service = UserService()
        # 替换数据库连接
        self.user_service.db = self.db_manager
    
    def tearDown(self):
        # 清理临时文件
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_user_registration_and_login_flow(self):
        """测试完整的用户注册和登录流程"""
        # 1. 注册新用户
        success, message = self.user_service.register("testuser", "password123")
        self.assertTrue(success)
        self.assertIn("注册成功", message)
        
        # 2. 使用正确凭据登录
        success, user_id, message = self.user_service.login("testuser", "password123")
        self.assertTrue(success)
        self.assertIsNotNone(user_id)
        self.assertEqual(self.user_service.get_current_user_id(), user_id)
        
        # 3. 检查用户状态
        self.assertTrue(self.user_service.is_logged_in())
        self.assertEqual(self.user_service.get_current_username(), "testuser")
        
        # 4. 登出
        self.user_service.logout()
        self.assertFalse(self.user_service.is_logged_in())
        self.assertIsNone(self.user_service.get_current_user_id())
    
    def test_password_security_integration(self):
        """测试密码安全性集成"""
        # 注册用户
        success, message = self.user_service.register("secureuser", "securepass123")
        self.assertTrue(success)
        
        # 验证密码不会明文存储
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE username = ?", ("secureuser",))
            stored_password = cursor.fetchone()[0]
            # bcrypt哈希的密码应该以$2b$开头且不等于原密码
            self.assertTrue(stored_password.startswith('$2b$'))
            self.assertNotEqual(stored_password, "securepass123")
    
    def test_duplicate_username_handling(self):
        """测试重复用户名处理"""
        # 注册第一个用户
        success1, message1 = self.user_service.register("duplicate", "password1")
        self.assertTrue(success1)
        
        # 尝试注册同名用户
        success2, message2 = self.user_service.register("duplicate", "password2")
        self.assertFalse(success2)
        self.assertIn("已存在", message2)


class TestConfigIntegration(unittest.TestCase):
    """测试配置管理器集成"""
    
    def setUp(self):
        # 使用临时配置文件
        self.temp_config = tempfile.NamedTemporaryFile(
            delete=False, suffix='.json', mode='w'
        )
        self.temp_config.close()
        
        self.config_manager = ConfigManager(self.temp_config.name)
    
    def tearDown(self):
        if os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)
    
    def test_config_persistence(self):
        """测试配置持久化"""
        # 修改配置
        self.config_manager.update_ui_config(theme="light", window_width=1400)
        self.config_manager.update_database_config(pool_size=10)
        
        # 创建新的配置管理器实例
        new_config_manager = ConfigManager(self.temp_config.name)
        config = new_config_manager.get_config()
        
        # 验证配置已持久化
        self.assertEqual(config.ui.theme, "light")
        self.assertEqual(config.ui.window_width, 1400)
        self.assertEqual(config.database.pool_size, 10)
    
    def test_config_export_import(self):
        """测试配置导出导入"""
        # 修改配置
        self.config_manager.update_ui_config(theme="light")
        
        # 导出配置
        export_path = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        export_path.close()
        
        try:
            success = self.config_manager.export_config(export_path.name)
            self.assertTrue(success)
            
            # 重置配置
            self.config_manager.reset_to_default()
            self.assertEqual(self.config_manager.get_config().ui.theme, "dark")
            
            # 导入配置
            success = self.config_manager.import_config(export_path.name)
            self.assertTrue(success)
            self.assertEqual(self.config_manager.get_config().ui.theme, "light")
            
        finally:
            if os.path.exists(export_path.name):
                os.unlink(export_path.name)


class TestDatabaseConnectionPoolIntegration(unittest.TestCase):
    """测试数据库连接池集成"""
    
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.pool = DatabaseConnectionPool(self.temp_db.name, pool_size=3)
    
    def tearDown(self):
        self.pool.close_all()
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_concurrent_connections(self):
        """测试并发连接处理"""
        connections = []
        
        # 获取多个连接
        for i in range(3):
            conn = self.pool.get_connection()
            self.assertIsNotNone(conn)
            connections.append(conn)
        
        # 验证连接可用
        for conn in connections:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            self.assertEqual(result[0], 1)
        
        # 返回连接
        for conn in connections:
            self.pool.return_connection(conn)
    
    def test_connection_context_manager(self):
        """测试连接上下文管理器"""
        # 使用上下文管理器
        with self.pool.get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            cursor.execute("INSERT INTO test VALUES (1)")
            conn.commit()  # 显式提交事务
        
        # 验证事务已提交
        with self.pool.get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM test")
            count = cursor.fetchone()[0]
            self.assertEqual(count, 1)


class TestEndToEndWorkflow(unittest.TestCase):
    """端到端工作流测试"""
    
    def setUp(self):
        # 创建临时环境
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = os.path.join(self.temp_dir, 'test.db')
        self.temp_config = os.path.join(self.temp_dir, 'config.json')
        
        # 初始化组件
        self.config_manager = ConfigManager(self.temp_config)
        self.db_manager = DatabaseManager(self.temp_db)
        self.user_service = UserService()
        self.user_service.db = self.db_manager
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_user_workflow(self):
        """测试完整的用户工作流"""
        # 1. 用户注册
        success, message = self.user_service.register("workflow_user", "password123")
        self.assertTrue(success)
        
        # 2. 用户登录
        success, user_id, message = self.user_service.login("workflow_user", "password123")
        self.assertTrue(success)
        
        # 3. 配置管理
        self.config_manager.update_ui_config(theme="light")
        config = self.config_manager.get_config()
        self.assertEqual(config.ui.theme, "light")
        
        # 4. 数据库操作
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            # 创建测试表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_models (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    model_name TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # 插入测试数据
            cursor.execute(
                "INSERT INTO user_models (user_id, model_name) VALUES (?, ?)",
                (user_id, "test_model")
            )
            
            # 验证数据
            cursor.execute(
                "SELECT model_name FROM user_models WHERE user_id = ?",
                (user_id,)
            )
            result = cursor.fetchone()
            self.assertEqual(result[0], "test_model")
        
        # 5. 用户登出
        self.user_service.logout()
        self.assertFalse(self.user_service.is_logged_in())


def run_integration_tests():
    """运行所有集成测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestUserServiceIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseConnectionPoolIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEndWorkflow))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("=" * 60)
    print("运行集成测试")
    print("=" * 60)
    
    success = run_integration_tests()
    
    if success:
        print("\n🎉 所有集成测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 部分集成测试失败")
        sys.exit(1) 