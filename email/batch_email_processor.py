"""
批量邮件处理器
用于管理大批量邮箱注册后的邮件接收和验证处理
"""

import threading
import time
import logging
from typing import Dict, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from mailcow_receiver import MailcowReceiver

class BatchEmailProcessor:
    """
    批量邮件处理器
    管理多个邮箱的验证邮件接收和k值提取
    """
    
    def __init__(self, imap_server: str, imap_port: int = 993, max_workers: int = 10):
        """
        初始化批量邮件处理器
        
        Args:
            imap_server: IMAP服务器地址
            imap_port: IMAP端口
            max_workers: 最大并发工作线程数
        """
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.max_workers = max_workers
        
        # 邮箱状态管理
        self.email_status = {}  # {email: {status, k_value, receiver, last_check}}
        self.status_lock = threading.Lock()
        
        # 回调函数
        self.on_k_value_found = None  # 找到k值时的回调
        self.on_status_update = None  # 状态更新时的回调
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
    def set_callbacks(self, on_k_value_found: Callable = None, on_status_update: Callable = None):
        """
        设置回调函数
        
        Args:
            on_k_value_found: 找到k值时的回调函数 (email, k_value)
            on_status_update: 状态更新时的回调函数 (email, status, message)
        """
        self.on_k_value_found = on_k_value_found
        self.on_status_update = on_status_update
    
    def add_email_account(self, email: str, password: str) -> bool:
        """
        添加邮箱账户到处理队列
        
        Args:
            email: 邮箱地址
            password: 邮箱密码
            
        Returns:
            bool: 添加是否成功
        """
        try:
            with self.status_lock:
                if email in self.email_status:
                    self.logger.warning(f"邮箱 {email} 已存在")
                    return False
                
                # 创建接收器
                receiver = MailcowReceiver(self.imap_server, self.imap_port)
                
                # 测试连接
                if not receiver.connect(email, password):
                    self.logger.error(f"邮箱 {email} 连接失败")
                    return False
                
                receiver.disconnect()  # 先断开，后续使用时再连接
                
                # 添加到状态管理
                self.email_status[email] = {
                    'status': 'waiting',  # waiting, checking, found, timeout, error
                    'password': password,
                    'k_value': None,
                    'receiver': receiver,
                    'last_check': None,
                    'check_count': 0
                }
                
                self._update_status(email, 'waiting', '等待验证邮件')
                return True
                
        except Exception as e:
            self.logger.error(f"添加邮箱 {email} 失败: {e}")
            return False
    
    def remove_email_account(self, email: str):
        """
        移除邮箱账户
        
        Args:
            email: 邮箱地址
        """
        with self.status_lock:
            if email in self.email_status:
                # 断开连接
                receiver = self.email_status[email].get('receiver')
                if receiver:
                    receiver.disconnect()
                
                del self.email_status[email]
                self.logger.info(f"已移除邮箱: {email}")
    
    def start_monitoring(self, timeout: int = 300, check_interval: int = 10):
        """
        开始监控所有邮箱的验证邮件
        
        Args:
            timeout: 每个邮箱的超时时间（秒）
            check_interval: 检查间隔（秒）
        """
        if not self.email_status:
            self.logger.warning("没有邮箱需要监控")
            return
        
        self.logger.info(f"开始监控 {len(self.email_status)} 个邮箱")
        
        # 使用线程池并发处理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 为每个邮箱创建监控任务
            futures = {}
            for email in list(self.email_status.keys()):
                future = executor.submit(self._monitor_single_email, email, timeout, check_interval)
                futures[future] = email
            
            # 等待所有任务完成
            for future in as_completed(futures):
                email = futures[future]
                try:
                    result = future.result()
                    self.logger.info(f"邮箱 {email} 监控完成: {result}")
                except Exception as e:
                    self.logger.error(f"邮箱 {email} 监控出错: {e}")
                    self._update_status(email, 'error', f'监控出错: {e}')
    
    def _monitor_single_email(self, email: str, timeout: int, check_interval: int) -> str:
        """
        监控单个邮箱的验证邮件
        
        Args:
            email: 邮箱地址
            timeout: 超时时间
            check_interval: 检查间隔
            
        Returns:
            str: 监控结果
        """
        start_time = time.time()
        
        try:
            # 获取邮箱信息
            with self.status_lock:
                if email not in self.email_status:
                    return "邮箱不存在"
                
                email_info = self.email_status[email]
                receiver = email_info['receiver']
                password = email_info['password']
            
            # 连接邮箱
            if not receiver.connect(email, password):
                self._update_status(email, 'error', '连接失败')
                return "连接失败"
            
            self._update_status(email, 'checking', '正在检查邮件')
            
            # 循环检查邮件
            while time.time() - start_time < timeout:
                try:
                    # 更新检查次数
                    with self.status_lock:
                        if email in self.email_status:
                            self.email_status[email]['check_count'] += 1
                            self.email_status[email]['last_check'] = time.time()
                    
                    # 获取最近的邮件
                    emails = receiver.get_recent_emails(count=5, sender_filter="yes24.com")
                    
                    for email_data in emails:
                        # 检查是否是验证邮件
                        if receiver._is_verification_email(email_data):
                            k_value = receiver.extract_k_value(email_data)
                            if k_value:
                                # 找到k值
                                with self.status_lock:
                                    if email in self.email_status:
                                        self.email_status[email]['k_value'] = k_value
                                
                                self._update_status(email, 'found', f'找到k值: {k_value}')
                                
                                # 调用回调函数
                                if self.on_k_value_found:
                                    try:
                                        self.on_k_value_found(email, k_value)
                                    except Exception as e:
                                        self.logger.error(f"回调函数执行失败: {e}")
                                
                                receiver.disconnect()
                                return f"找到k值: {k_value}"
                    
                    # 等待下次检查
                    time.sleep(check_interval)
                    
                except Exception as e:
                    self.logger.error(f"检查邮箱 {email} 时出错: {e}")
                    time.sleep(check_interval)
            
            # 超时
            receiver.disconnect()
            self._update_status(email, 'timeout', f'超时（{timeout}秒）')
            return "超时"
            
        except Exception as e:
            self.logger.error(f"监控邮箱 {email} 失败: {e}")
            self._update_status(email, 'error', f'监控失败: {e}')
            return f"监控失败: {e}"
    
    def _update_status(self, email: str, status: str, message: str):
        """
        更新邮箱状态
        
        Args:
            email: 邮箱地址
            status: 状态
            message: 状态消息
        """
        with self.status_lock:
            if email in self.email_status:
                self.email_status[email]['status'] = status
        
        self.logger.info(f"邮箱 {email} 状态更新: {status} - {message}")
        
        # 调用状态更新回调
        if self.on_status_update:
            try:
                self.on_status_update(email, status, message)
            except Exception as e:
                self.logger.error(f"状态更新回调执行失败: {e}")
    
    def get_status_summary(self) -> Dict:
        """
        获取所有邮箱的状态摘要
        
        Returns:
            Dict: 状态摘要
        """
        with self.status_lock:
            summary = {
                'total': len(self.email_status),
                'waiting': 0,
                'checking': 0,
                'found': 0,
                'timeout': 0,
                'error': 0,
                'details': {}
            }
            
            for email, info in self.email_status.items():
                status = info['status']
                summary[status] = summary.get(status, 0) + 1
                
                summary['details'][email] = {
                    'status': status,
                    'k_value': info.get('k_value'),
                    'check_count': info.get('check_count', 0),
                    'last_check': info.get('last_check')
                }
            
            return summary
    
    def get_k_values(self) -> Dict[str, str]:
        """
        获取所有已找到的k值
        
        Returns:
            Dict: {email: k_value}
        """
        with self.status_lock:
            k_values = {}
            for email, info in self.email_status.items():
                if info.get('k_value'):
                    k_values[email] = info['k_value']
            return k_values
    
    def stop_monitoring(self):
        """
        停止监控并清理资源
        """
        with self.status_lock:
            for email, info in self.email_status.items():
                receiver = info.get('receiver')
                if receiver:
                    receiver.disconnect()
            
            self.email_status.clear()
        
        self.logger.info("已停止所有邮箱监控")
    
    def wait_for_all_k_values(self, timeout: int = 600) -> Dict[str, str]:
        """
        等待所有邮箱的k值
        
        Args:
            timeout: 总超时时间
            
        Returns:
            Dict: {email: k_value}
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            summary = self.get_status_summary()
            
            # 检查是否所有邮箱都完成了（找到k值、超时或出错）
            active_count = summary['waiting'] + summary['checking']
            if active_count == 0:
                break
            
            time.sleep(5)  # 等待5秒后再检查
        
        return self.get_k_values()

def create_batch_processor(imap_server: str, imap_port: int = 993, max_workers: int = 10) -> BatchEmailProcessor:
    """
    创建批量邮件处理器
    
    Args:
        imap_server: IMAP服务器地址
        imap_port: IMAP端口
        max_workers: 最大并发数
        
    Returns:
        BatchEmailProcessor: 处理器实例
    """
    return BatchEmailProcessor(imap_server, imap_port, max_workers)