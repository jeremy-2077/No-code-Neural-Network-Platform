"""
用户管理服务
处理用户相关的业务逻辑
"""
from database.db_manager import DatabaseManager
from typing import Optional, Tuple


class UserService:
    """用户管理服务类"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.current_user_id: Optional[int] = None
        self.current_username: Optional[str] = None
    
    def login(self, username: str, password: str) -> Tuple[bool, Optional[int], str]:
        """
        用户登录
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            (是否成功, 用户ID, 消息)
        """
        if not username or not password:
            return False, None, "用户名和密码不能为空"
        
        try:
            success, user_id = self.db.verify_user(username, password)
            if success:
                self.current_user_id = user_id
                self.current_username = username
                return True, user_id, "登录成功"
            else:
                return False, None, "用户名或密码错误"
        except Exception as e:
            return False, None, f"登录失败: {str(e)}"
    
    def register(self, username: str, password: str) -> Tuple[bool, str]:
        """
        用户注册
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            (是否成功, 消息)
        """
        if not username or not password:
            return False, "用户名和密码不能为空"
        
        if len(username) < 3:
            return False, "用户名至少需要3个字符"
        
        if len(password) < 6:
            return False, "密码至少需要6个字符"
        
        try:
            if self.db.add_user(username, password):
                return True, "注册成功，请登录"
            else:
                return False, "用户名已存在"
        except Exception as e:
            return False, f"注册失败: {str(e)}"
    
    def logout(self):
        """用户登出"""
        self.current_user_id = None
        self.current_username = None
    
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        return self.current_user_id is not None
    
    def get_current_user_id(self) -> Optional[int]:
        """获取当前用户ID"""
        return self.current_user_id
    
    def get_current_username(self) -> Optional[str]:
        """获取当前用户名"""
        return self.current_username
    
    def get_user_info(self, user_id: int = None) -> Optional[dict]:
        """
        获取用户信息
        
        Args:
            user_id: 用户ID，如果为None则获取当前用户信息
            
        Returns:
            用户信息字典或None
        """
        target_user_id = user_id or self.current_user_id
        if not target_user_id:
            return None
        
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, username, created_at FROM users WHERE id = ?",
                    (target_user_id,)
                )
                result = cursor.fetchone()
                if result:
                    return {
                        "id": result[0],
                        "username": result[1],
                        "created_at": result[2]
                    }
        except Exception as e:
            print(f"获取用户信息失败: {str(e)}")
        
        return None 