#!/usr/bin/env python3
"""
测试重构后的代码
验证各个组件是否正常工作
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from services.user_service import UserService
from utils.logger import logger, ErrorHandler
from database.connection_pool import DatabaseConnectionPool


class TestUserService(unittest.TestCase):
    """测试用户服务"""
    
    def setUp(self):
        self.user_service = UserService()
    
    def test_login_with_empty_credentials(self):
        """测试空凭据登录"""
        success, user_id, message = self.user_service.login("", "")
        self.assertFalse(success)
        self.assertIsNone(user_id)
        self.assertIn("不能为空", message)
    
    def test_register_with_short_username(self):
        """测试用户名过短的注册"""
        success, message = self.user_service.register("ab", "password123")
        self.assertFalse(success)
        self.assertIn("至少需要3个字符", message)
    
    def test_register_with_short_password(self):
        """测试密码过短的注册"""
        success, message = self.user_service.register("testuser", "12345")
        self.assertFalse(success)
        self.assertIn("至少需要6个字符", message)


class TestLogger(unittest.TestCase):
    """测试日志系统"""
    
    def test_logger_singleton(self):
        """测试日志器单例模式"""
        from utils.logger import Logger
        logger1 = Logger()
        logger2 = Logger()
        self.assertIs(logger1, logger2)
    
    def test_error_handler(self):
        """测试错误处理器"""
        test_exception = Exception("测试异常")
        error_msg = ErrorHandler.handle_database_error(test_exception, "测试操作")
        self.assertIn("测试操作失败", error_msg)
        self.assertIn("测试异常", error_msg)


class TestConnectionPool(unittest.TestCase):
    """测试数据库连接池"""
    
    def setUp(self):
        # 使用临时数据库进行测试
        self.test_db_path = ":memory:"
        self.pool = DatabaseConnectionPool(self.test_db_path, pool_size=2)
    
    def test_connection_pool_creation(self):
        """测试连接池创建"""
        self.assertEqual(self.pool.pool_size, 2)
        self.assertTrue(self.pool._initialized)
    
    def test_get_connection(self):
        """测试获取连接"""
        conn = self.pool.get_connection()
        self.assertIsNotNone(conn)
        # 测试连接是否有效
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        self.assertEqual(result[0], 1)
        
        # 返回连接
        self.pool.return_connection(conn)
    
    def tearDown(self):
        self.pool.close_all()


def run_import_tests():
    """运行导入测试"""
    print("测试模块导入...")
    
    try:
        # 测试服务层导入
        from services.user_service import UserService
        print("✓ UserService 导入成功")
        
        # 测试日志系统导入
        from utils.logger import logger, ErrorHandler
        print("✓ Logger 系统导入成功")
        
        # 测试数据库连接池导入
        from database.connection_pool import get_connection_pool
        print("✓ 数据库连接池导入成功")
        
        # 测试UI组件导入
        from ui.components.model_dialog import GeneratedModelsDialog
        print("✓ UI组件导入成功")
        
        return True
        
    except ImportError as e:
        print(f"✗ 导入失败: {str(e)}")
        return False


def run_basic_functionality_tests():
    """运行基本功能测试"""
    print("\n测试基本功能...")
    
    try:
        # 测试用户服务
        user_service = UserService()
        success, user_id, message = user_service.login("", "")
        assert not success, "空凭据登录应该失败"
        print("✓ 用户服务基本功能正常")
        
        # 测试日志系统
        logger.info("测试日志信息")
        print("✓ 日志系统正常")
        
        # 测试错误处理
        test_exception = Exception("测试异常")
        error_msg = ErrorHandler.handle_ui_error(test_exception)
        assert "测试异常" in error_msg, "错误处理应该包含异常信息"
        print("✓ 错误处理系统正常")
        
        return True
        
    except Exception as e:
        print(f"✗ 基本功能测试失败: {str(e)}")
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("神经网络平台重构验证测试")
    print("=" * 60)
    
    # 运行导入测试
    import_success = run_import_tests()
    
    # 运行基本功能测试
    functionality_success = run_basic_functionality_tests()
    
    # 运行单元测试
    print("\n运行单元测试...")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestUserService))
    suite.addTests(loader.loadTestsFromTestCase(TestLogger))
    suite.addTests(loader.loadTestsFromTestCase(TestConnectionPool))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结:")
    print(f"导入测试: {'✓ 通过' if import_success else '✗ 失败'}")
    print(f"功能测试: {'✓ 通过' if functionality_success else '✗ 失败'}")
    print(f"单元测试: {'✓ 通过' if result.wasSuccessful() else '✗ 失败'}")
    
    if import_success and functionality_success and result.wasSuccessful():
        print("\n🎉 所有测试通过！重构成功！")
        return 0
    else:
        print("\n❌ 部分测试失败，需要检查代码")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 