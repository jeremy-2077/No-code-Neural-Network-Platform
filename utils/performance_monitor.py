"""
性能监控工具
监测应用程序的性能指标和资源使用情况
"""
import time
import psutil
import threading
from functools import wraps
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from utils.logger import logger


@dataclass
class PerformanceMetric:
    """性能指标数据"""
    name: str
    value: float
    unit: str
    timestamp: float
    category: str = "general"


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        # 监控间隔（秒）
        self.monitor_interval = 5.0
        
        # 最大保存的指标数量
        self.max_metrics = 1000
    
    def start_monitoring(self):
        """开始监控"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("性能监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        logger.info("性能监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                self._collect_system_metrics()
                time.sleep(self.monitor_interval)
            except Exception as e:
                logger.error(f"性能监控出错: {str(e)}")
    
    def _collect_system_metrics(self):
        """收集系统性能指标"""
        current_time = time.time()
        
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            self.add_metric("cpu_usage", cpu_percent, "%", current_time, "system")
            
            # 内存使用
            memory = psutil.virtual_memory()
            self.add_metric("memory_usage", memory.percent, "%", current_time, "system")
            self.add_metric("memory_used", memory.used / 1024 / 1024, "MB", current_time, "system")
            
            # 磁盘使用
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.add_metric("disk_usage", disk_percent, "%", current_time, "system")
            
            # 进程特定指标
            process = psutil.Process()
            self.add_metric("process_memory", process.memory_info().rss / 1024 / 1024, "MB", current_time, "process")
            self.add_metric("process_cpu", process.cpu_percent(), "%", current_time, "process")
            
        except Exception as e:
            logger.error(f"收集系统指标失败: {str(e)}")
    
    def add_metric(self, name: str, value: float, unit: str, timestamp: float = None, category: str = "general"):
        """添加性能指标"""
        if timestamp is None:
            timestamp = time.time()
        
        metric = PerformanceMetric(name, value, unit, timestamp, category)
        
        with self._lock:
            self.metrics.append(metric)
            
            # 清理旧指标
            if len(self.metrics) > self.max_metrics:
                self.metrics = self.metrics[-self.max_metrics:]
    
    def get_metrics(self, category: str = None, last_n: int = None) -> List[PerformanceMetric]:
        """获取性能指标"""
        with self._lock:
            metrics = self.metrics.copy()
        
        if category:
            metrics = [m for m in metrics if m.category == category]
        
        if last_n:
            metrics = metrics[-last_n:]
        
        return metrics
    
    def get_average_metric(self, name: str, time_window: float = 300) -> Optional[float]:
        """获取指定时间窗口内指标的平均值"""
        current_time = time.time()
        start_time = current_time - time_window
        
        with self._lock:
            values = [
                m.value for m in self.metrics
                if m.name == name and m.timestamp >= start_time
            ]
        
        if values:
            return sum(values) / len(values)
        return None
    
    def get_performance_summary(self) -> Dict[str, Dict[str, float]]:
        """获取性能摘要"""
        summary = {}
        
        # 按类别分组
        categories = set(m.category for m in self.metrics)
        
        for category in categories:
            category_metrics = self.get_metrics(category=category, last_n=100)
            
            if not category_metrics:
                continue
            
            # 按指标名称分组
            metric_names = set(m.name for m in category_metrics)
            category_summary = {}
            
            for name in metric_names:
                values = [m.value for m in category_metrics if m.name == name]
                if values:
                    category_summary[name] = {
                        'current': values[-1],
                        'average': sum(values) / len(values),
                        'min': min(values),
                        'max': max(values),
                        'count': len(values)
                    }
            
            summary[category] = category_summary
        
        return summary
    
    def export_metrics(self, file_path: str) -> bool:
        """导出指标到文件"""
        try:
            import json
            
            metrics_data = []
            for metric in self.metrics:
                metrics_data.append({
                    'name': metric.name,
                    'value': metric.value,
                    'unit': metric.unit,
                    'timestamp': metric.timestamp,
                    'category': metric.category
                })
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(metrics_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"性能指标已导出到: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出性能指标失败: {str(e)}")
            return False


# 全局性能监控器实例
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """获取全局性能监控器实例"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def performance_timer(category: str = "timing"):
    """性能计时装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.time()
                execution_time = (end_time - start_time) * 1000  # 转换为毫秒
                
                metric_name = f"{func.__module__}.{func.__name__}"
                monitor.add_metric(metric_name, execution_time, "ms", end_time, category)
                
                # 如果执行时间过长，记录警告
                if execution_time > 1000:  # 超过1秒
                    logger.warning(f"函数 {metric_name} 执行时间过长: {execution_time:.2f}ms")
        
        return wrapper
    return decorator


def log_memory_usage(prefix: str = ""):
    """记录内存使用情况"""
    try:
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        logger.info(f"{prefix}内存使用: {memory_mb:.2f} MB")
        
        monitor = get_performance_monitor()
        monitor.add_metric("memory_checkpoint", memory_mb, "MB", category="memory")
        
    except Exception as e:
        logger.error(f"记录内存使用失败: {str(e)}")


def measure_database_performance(func: Callable):
    """数据库操作性能测量装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        monitor = get_performance_monitor()
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            success = True
        except Exception as e:
            success = False
            raise
        finally:
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000
            
            # 记录数据库操作性能
            metric_name = f"db_{func.__name__}"
            monitor.add_metric(metric_name, execution_time, "ms", end_time, "database")
            
            # 记录操作结果
            result_metric = f"db_{func.__name__}_success"
            monitor.add_metric(result_metric, 1 if success else 0, "bool", end_time, "database")
            
            if execution_time > 500:  # 数据库操作超过500ms
                logger.warning(f"数据库操作 {func.__name__} 执行缓慢: {execution_time:.2f}ms")
        
        return result
    
    return wrapper


class PerformanceProfiler:
    """性能分析器"""
    
    def __init__(self, name: str):
        self.name = name
        self.start_time: Optional[float] = None
        self.monitor = get_performance_monitor()
    
    def __enter__(self):
        self.start_time = time.time()
        logger.debug(f"开始性能分析: {self.name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            end_time = time.time()
            duration = (end_time - self.start_time) * 1000
            
            self.monitor.add_metric(
                f"profile_{self.name}",
                duration,
                "ms",
                end_time,
                "profiling"
            )
            
            logger.debug(f"性能分析完成: {self.name}, 耗时: {duration:.2f}ms")


def profile_section(name: str):
    """创建性能分析上下文管理器"""
    return PerformanceProfiler(name) 