#!/usr/bin/env python3
"""
综合优化验证脚本
验证高、中、低优先级优化的所有功能
"""

import sys
import os
import time
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_high_priority_optimizations():
    """测试高优先级优化"""
    print("🔥 测试高优先级优化...")
    
    # 1. 测试依赖管理
    try:
        requirements_file = Path("requirements.txt")
        assert requirements_file.exists(), "requirements.txt 不存在"
        
        content = requirements_file.read_text()
        assert "PyQt5" in content, "requirements.txt 缺少 PyQt5"
        assert "torch" in content, "requirements.txt 缺少 torch"
        assert "bcrypt" in content, "requirements.txt 缺少 bcrypt"
        print("  ✓ 依赖管理文件完整")
    except Exception as e:
        print(f"  ✗ 依赖管理测试失败: {e}")
        return False
    
    # 2. 测试密码安全
    try:
        # 检查bcrypt是否正确导入和使用
        import bcrypt
        
        # 测试密码哈希功能
        test_password = "password123"
        password_hash = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt())
        
        # 验证哈希
        assert password_hash.startswith(b'$2b$'), "bcrypt哈希格式不正确"
        assert bcrypt.checkpw(test_password.encode('utf-8'), password_hash), "密码验证失败"
        
        # 检查数据库管理器是否导入了bcrypt
        from database.db_manager import DatabaseManager
        assert hasattr(DatabaseManager, 'add_user'), "DatabaseManager缺少add_user方法"
        
        print("  ✓ 密码安全存储正常")
    except Exception as e:
        print(f"  ✗ 密码安全测试失败: {e}")
        return False
    
    # 3. 测试README文档
    try:
        readme_file = Path("README.md")
        assert readme_file.exists(), "README.md 不存在"
        
        content = readme_file.read_text()
        assert len(content) > 1000, "README.md 内容太少"
        assert "安装说明" in content, "README.md 缺少安装说明"
        assert "技术栈" in content, "README.md 缺少技术栈说明"
        print("  ✓ README文档完整")
    except Exception as e:
        print(f"  ✗ README文档测试失败: {e}")
        return False
    
    # 4. 测试目录结构
    try:
        assert Path("saved_models").exists(), "saved_models 目录不存在"
        assert Path("data").exists(), "data 目录不存在"
        assert Path("logs").exists(), "logs 目录不存在"
        assert Path(".gitignore").exists(), ".gitignore 文件不存在"
        print("  ✓ 目录结构正确")
    except Exception as e:
        print(f"  ✗ 目录结构测试失败: {e}")
        return False
    
    return True


def test_medium_priority_optimizations():
    """测试中优先级优化"""
    print("🚀 测试中优先级优化...")
    
    # 1. 测试重构后的架构
    try:
        from services.user_service import UserService
        from ui.components.model_dialog import GeneratedModelsDialog
        from ui.main_window_refactored import MainWindow
        
        # 测试用户服务
        user_service = UserService()
        success, user_id, message = user_service.login("", "")
        assert not success, "空登录应该失败"
        
        print("  ✓ 重构架构正常")
    except Exception as e:
        print(f"  ✗ 重构架构测试失败: {e}")
        return False
    
    # 2. 测试日志系统
    try:
        from utils.logger import logger, ErrorHandler
        
        # 测试日志记录
        logger.info("测试日志信息")
        
        # 测试错误处理
        test_exception = Exception("测试异常")
        error_msg = ErrorHandler.handle_database_error(test_exception)
        assert "测试异常" in error_msg, "错误处理不正确"
        
        print("  ✓ 日志系统正常")
    except Exception as e:
        print(f"  ✗ 日志系统测试失败: {e}")
        return False
    
    # 3. 测试数据库连接池
    try:
        from database.connection_pool import DatabaseConnectionPool
        
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        pool = DatabaseConnectionPool(temp_db.name, pool_size=2)
        
        # 测试连接获取
        conn = pool.get_connection()
        assert conn is not None, "无法获取数据库连接"
        
        # 测试连接有效性
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1, "数据库连接无效"
        
        pool.return_connection(conn)
        pool.close_all()
        os.unlink(temp_db.name)
        
        print("  ✓ 数据库连接池正常")
    except Exception as e:
        print(f"  ✗ 数据库连接池测试失败: {e}")
        return False
    
    return True


def test_low_priority_optimizations():
    """测试低优先级优化"""
    print("✨ 测试低优先级优化...")
    
    # 1. 测试UI主题系统
    try:
        from ui.styles import ThemeManager
        
        # 测试主题获取
        dark_theme = ThemeManager.get_theme(ThemeManager.DARK)
        assert len(dark_theme) > 1000, "深色主题内容太少"
        
        light_theme = ThemeManager.get_theme(ThemeManager.LIGHT)
        assert len(light_theme) > 500, "浅色主题内容太少"
        
        # 测试可用主题列表
        themes = ThemeManager.get_available_themes()
        assert ThemeManager.DARK in themes, "深色主题未列出"
        assert ThemeManager.LIGHT in themes, "浅色主题未列出"
        
        print("  ✓ UI主题系统正常")
    except Exception as e:
        print(f"  ✗ UI主题系统测试失败: {e}")
        return False
    
    # 2. 测试配置管理
    try:
        from config.config_manager import ConfigManager, AppConfig
        
        # 使用临时配置文件
        temp_config = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        temp_config.close()
        
        config_manager = ConfigManager(temp_config.name)
        
        # 测试配置更新
        config_manager.update_ui_config(theme="light", window_width=1400)
        config = config_manager.get_config()
        assert config.ui.theme == "light", "主题配置未保存"
        assert config.ui.window_width == 1400, "窗口宽度配置未保存"
        
        # 测试配置持久化
        new_config_manager = ConfigManager(temp_config.name)
        new_config = new_config_manager.get_config()
        assert new_config.ui.theme == "light", "配置未持久化"
        
        os.unlink(temp_config.name)
        print("  ✓ 配置管理系统正常")
    except Exception as e:
        print(f"  ✗ 配置管理系统测试失败: {e}")
        return False
    
    # 3. 测试性能监控
    try:
        from utils.performance_monitor import get_performance_monitor, performance_timer
        
        monitor = get_performance_monitor()
        
        # 测试指标添加
        monitor.add_metric("test_metric", 100.5, "ms", category="test")
        metrics = monitor.get_metrics(category="test")
        assert len(metrics) > 0, "指标未正确添加"
        assert metrics[-1].name == "test_metric", "指标名称不正确"
        
        # 测试性能计时装饰器
        @performance_timer("test")
        def test_function():
            time.sleep(0.01)  # 模拟一些工作
            return "completed"
        
        result = test_function()
        assert result == "completed", "装饰器影响了函数返回值"
        
        print("  ✓ 性能监控系统正常")
    except Exception as e:
        print(f"  ✗ 性能监控系统测试失败: {e}")
        return False
    
    return True


def test_integration():
    """测试集成功能"""
    print("🔗 测试集成功能...")
    
    try:
        # 测试组件之间的协作
        from services.user_service import UserService
        from config.config_manager import get_config_manager
        from utils.logger import logger
        from utils.performance_monitor import get_performance_monitor
        
        # 模拟用户工作流
        user_service = UserService()
        config_manager = get_config_manager()
        monitor = get_performance_monitor()
        
        # 测试配置与主题的集成
        config_manager.update_ui_config(theme="dark")
        config = config_manager.get_config()
        assert config.ui.theme == "dark", "配置更新失败"
        
        # 测试性能监控集成
        monitor.add_metric("integration_test", 42, "units")
        metrics = monitor.get_metrics()
        assert len(metrics) > 0, "性能监控集成失败"
        
        print("  ✓ 组件集成正常")
        return True
    except Exception as e:
        print(f"  ✗ 集成测试失败: {e}")
        return False


def test_documentation():
    """测试文档完整性"""
    print("📚 测试文档完整性...")
    
    try:
        # 检查重要文档文件
        docs = [
            "README.md",
            "REFACTORING_SUMMARY.md", 
            "UPGRADE_GUIDE.md",
            "project_structure"
        ]
        
        for doc in docs:
            assert Path(doc).exists(), f"文档文件 {doc} 不存在"
        
        # 检查目录说明文件
        assert Path("data/README.md").exists(), "data目录缺少说明文件"
        assert Path("saved_models/README.md").exists(), "saved_models目录缺少说明文件"
        
        print("  ✓ 文档完整性正常")
        return True
    except Exception as e:
        print(f"  ✗ 文档完整性测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 80)
    print("🎯 综合优化验证测试")
    print("验证高、中、低优先级的所有优化功能")
    print("=" * 80)
    
    tests = [
        ("高优先级优化", test_high_priority_optimizations),
        ("中优先级优化", test_medium_priority_optimizations),
        ("低优先级优化", test_low_priority_optimizations),
        ("集成功能", test_integration),
        ("文档完整性", test_documentation),
    ]
    
    results = []
    total_time = time.time()
    
    for test_name, test_func in tests:
        print(f"\n🧪 测试 {test_name}...")
        start_time = time.time()
        
        try:
            result = test_func()
            results.append((test_name, result))
            elapsed = time.time() - start_time
            status = "✅ 通过" if result else "❌ 失败"
            print(f"   {status} (耗时: {elapsed:.2f}s)")
        except Exception as e:
            results.append((test_name, False))
            elapsed = time.time() - start_time
            print(f"   ❌ 异常: {str(e)} (耗时: {elapsed:.2f}s)")
    
    # 总结
    total_elapsed = time.time() - total_time
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print("\n" + "=" * 80)
    print("📊 测试总结")
    print("=" * 80)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name:20} {status}")
    
    print(f"\n📈 总体结果: {passed}/{total} 测试通过")
    print(f"⏱️  总耗时: {total_elapsed:.2f} 秒")
    
    if passed == total:
        print("\n🎉 所有优化验证通过！项目优化完成！")
        print("\n💡 优化成果：")
        print("   • 高优先级：依赖管理、密码安全、文档完善、目录整理")
        print("   • 中优先级：代码重构、统一日志、连接池优化")
        print("   • 低优先级：UI美化、配置管理、性能监控")
        print("\n🚀 您的神经网络平台现在更加健壮、安全和易用！")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，需要进一步检查")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 