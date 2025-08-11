#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mailcow邮箱接收器
用于连接自建的Mailcow邮箱服务器，接收和解析验证邮件
"""

import imaplib
import email
from email.header import decode_header
import re
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Optional

class MailcowReceiver:
    """
    Mailcow邮箱接收器
    用于连接自建的Mailcow邮箱服务器，接收验证邮件并提取k值
    """
    
    def __init__(self, imap_server: str, imap_port: int = 993, use_ssl: bool = True):
        """
        初始化Mailcow接收器
        
        Args:
            imap_server: IMAP服务器地址
            imap_port: IMAP端口，默认993（SSL）
            use_ssl: 是否使用SSL，默认True
        """
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.use_ssl = use_ssl
        self.imap = None
        self.email_address = None
        self.password = None
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
    def connect(self, email_address: str, password: str) -> bool:
        """
        连接到邮箱
        
        Args:
            email_address: 邮箱地址
            password: 邮箱密码
            
        Returns:
            bool: 连接是否成功
        """
        try:
            self.email_address = email_address
            self.password = password
            
            # 创建IMAP连接
            if self.use_ssl:
                self.imap = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            else:
                self.imap = imaplib.IMAP4(self.imap_server, self.imap_port)
            
            # 登录
            self.imap.login(email_address, password)
            
            # 选择收件箱
            self.imap.select('INBOX')
            
            self.logger.info(f"成功连接到邮箱: {email_address}")
            return True
            
        except Exception as e:
            self.logger.error(f"连接邮箱失败: {e}")
            return False
    
    def disconnect(self):
        """
        断开邮箱连接
        """
        if self.imap:
            try:
                self.imap.close()
                self.imap.logout()
                self.logger.info("邮箱连接已断开")
            except Exception as e:
                self.logger.error(f"断开连接时出错: {e}")
            finally:
                self.imap = None
    
    def get_recent_emails(self, count: int = 10, sender_filter: str = None) -> List[Dict]:
        """
        获取最近的邮件
        
        Args:
            count: 获取邮件数量
            sender_filter: 发件人过滤器，如"yes24.com"
            
        Returns:
            List[Dict]: 邮件列表
        """
        if not self.imap:
            self.logger.error("未连接到邮箱")
            return []
        
        try:
            # 搜索邮件
            search_criteria = 'ALL'
            if sender_filter:
                search_criteria = f'FROM "{sender_filter}"'
            
            status, messages = self.imap.search(None, search_criteria)
            if status != 'OK':
                self.logger.error("搜索邮件失败")
                return []
            
            # 获取邮件ID列表
            email_ids = messages[0].split()
            
            # 获取最近的邮件（倒序）
            recent_ids = email_ids[-count:] if len(email_ids) >= count else email_ids
            recent_ids.reverse()  # 最新的在前
            
            emails = []
            for email_id in recent_ids:
                email_data = self._fetch_email(email_id)
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except Exception as e:
            self.logger.error(f"获取邮件失败: {e}")
            return []
    
    def _fetch_email(self, email_id: bytes) -> Optional[Dict]:
        """
        获取单封邮件的详细信息
        
        Args:
            email_id: 邮件ID
            
        Returns:
            Dict: 邮件信息
        """
        try:
            status, msg_data = self.imap.fetch(email_id, '(RFC822)')
            if status != 'OK':
                return None
            
            # 解析邮件
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # 提取基本信息
            subject = self._decode_header(email_message['Subject'])
            from_addr = self._decode_header(email_message['From'])
            date = email_message['Date']
            
            # 提取邮件内容
            body_text, body_html = self._extract_body(email_message)
            
            return {
                'id': email_id.decode(),
                'subject': subject,
                'from': from_addr,
                'date': date,
                'body_text': body_text,
                'body_html': body_html
            }
            
        except Exception as e:
            self.logger.error(f"获取邮件详情失败: {e}")
            return None
    
    def _decode_header(self, header: str) -> str:
        """
        解码邮件头部信息
        
        Args:
            header: 邮件头部
            
        Returns:
            str: 解码后的字符串
        """
        if not header:
            return ""
        
        try:
            decoded_parts = decode_header(header)
            decoded_string = ""
            
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        decoded_string += part.decode(encoding)
                    else:
                        decoded_string += part.decode('utf-8', errors='ignore')
                else:
                    decoded_string += part
            
            return decoded_string
            
        except Exception as e:
            self.logger.error(f"解码头部失败: {e}")
            return str(header)
    
    def _extract_body(self, email_message) -> tuple:
        """
        提取邮件正文内容
        
        Args:
            email_message: 邮件消息对象
            
        Returns:
            tuple: (纯文本内容, HTML内容)
        """
        body_text = ""
        body_html = ""
        
        try:
            if email_message.is_multipart():
                # 多部分邮件
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    # 跳过附件
                    if "attachment" in content_disposition:
                        continue
                    
                    if content_type == "text/plain":
                        body_text = self._decode_body(part)
                    elif content_type == "text/html":
                        body_html = self._decode_body(part)
            else:
                # 单部分邮件
                content_type = email_message.get_content_type()
                if content_type == "text/plain":
                    body_text = self._decode_body(email_message)
                elif content_type == "text/html":
                    body_html = self._decode_body(email_message)
            
            return body_text, body_html
            
        except Exception as e:
            self.logger.error(f"提取邮件正文失败: {e}")
            return "", ""
    
    def _decode_body(self, part) -> str:
        """
        解码邮件正文部分
        
        Args:
            part: 邮件部分
            
        Returns:
            str: 解码后的内容
        """
        try:
            body = part.get_payload(decode=True)
            if isinstance(body, bytes):
                # 尝试不同的编码
                encodings = ['utf-8', 'gbk', 'gb2312', 'iso-8859-1']
                for encoding in encodings:
                    try:
                        return body.decode(encoding)
                    except UnicodeDecodeError:
                        continue
                # 如果都失败了，使用错误忽略模式
                return body.decode('utf-8', errors='ignore')
            else:
                return str(body)
                
        except Exception as e:
            self.logger.error(f"解码邮件正文失败: {e}")
            return ""
    
    def extract_k_value(self, email_data: Dict) -> Optional[str]:
        """
        从YES24验证邮件中提取k值
        
        Args:
            email_data: 邮件数据
            
        Returns:
            str: 提取到的k值，如果没有找到返回None
        """
        try:
            # 优先从HTML内容中提取
            if email_data.get('body_html'):
                k_value = self._extract_k_from_html(email_data['body_html'])
                if k_value:
                    return k_value
            
            # 从纯文本中提取
            if email_data.get('body_text'):
                k_value = self._extract_k_from_text(email_data['body_text'])
                if k_value:
                    return k_value
            
            return None
            
        except Exception as e:
            self.logger.error(f"提取k值失败: {e}")
            return None
    
    def _extract_k_from_html(self, html_content: str) -> Optional[str]:
        """
        从HTML内容中提取k值
        
        Args:
            html_content: HTML内容
            
        Returns:
            str: k值
        """
        try:
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 查找所有链接
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                # 查找YES24验证链接
                if 'yes24.com' in href and 'FnMyAuthentication.aspx' in href:
                    # 提取k参数
                    k_match = re.search(r'[?&]k=([^&]+)', href)
                    if k_match:
                        return k_match.group(1)
            
            # 如果没有找到链接，尝试正则表达式
            k_match = re.search(r'yes24\.com[^\s]*[?&]k=([^&\s]+)', html_content)
            if k_match:
                return k_match.group(1)
            
            return None
            
        except Exception as e:
            self.logger.error(f"从HTML提取k值失败: {e}")
            return None
    
    def _extract_k_from_text(self, text_content: str) -> Optional[str]:
        """
        从纯文本内容中提取k值
        
        Args:
            text_content: 纯文本内容
            
        Returns:
            str: k值
        """
        try:
            # 使用正则表达式查找YES24验证链接
            k_match = re.search(r'yes24\.com[^\s]*[?&]k=([^&\s]+)', text_content)
            if k_match:
                return k_match.group(1)
            
            return None
            
        except Exception as e:
            self.logger.error(f"从文本提取k值失败: {e}")
            return None
    
    def wait_for_verification_email(self, timeout: int = 300, check_interval: int = 10) -> Optional[str]:
        """
        等待验证邮件并提取k值
        
        Args:
            timeout: 超时时间（秒）
            check_interval: 检查间隔（秒）
            
        Returns:
            str: 提取到的k值，超时返回None
        """
        if not self.imap:
            self.logger.error("未连接到邮箱")
            return None
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # 获取最近的邮件
                emails = self.get_recent_emails(count=5, sender_filter="yes24.com")
                
                for email_data in emails:
                    # 检查是否是验证邮件
                    if self._is_verification_email(email_data):
                        k_value = self.extract_k_value(email_data)
                        if k_value:
                            self.logger.info(f"找到验证邮件，k值: {k_value}")
                            return k_value
                
                # 等待下次检查
                time.sleep(check_interval)
                
            except Exception as e:
                self.logger.error(f"等待验证邮件时出错: {e}")
                time.sleep(check_interval)
        
        self.logger.warning(f"等待验证邮件超时（{timeout}秒）")
        return None
    
    def _is_verification_email(self, email_data: Dict) -> bool:
        """
        判断是否是验证邮件
        
        Args:
            email_data: 邮件数据
            
        Returns:
            bool: 是否是验证邮件
        """
        try:
            subject = email_data.get('subject', '').lower()
            from_addr = email_data.get('from', '').lower()
            
            # 检查发件人
            if 'yes24' not in from_addr:
                return False
            
            # 检查主题关键词
            verification_keywords = ['verification', 'verify', 'confirm', 'authentication']
            for keyword in verification_keywords:
                if keyword in subject:
                    return True
            
            # 检查邮件内容
            body_text = email_data.get('body_text', '').lower()
            body_html = email_data.get('body_html', '').lower()
            
            content = body_text + body_html
            if 'verification' in content or 'authenticate' in content:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"判断验证邮件失败: {e}")
            return False

def create_mailcow_receiver(imap_server: str, imap_port: int = 993) -> MailcowReceiver:
    """
    创建Mailcow接收器实例
    
    Args:
        imap_server: IMAP服务器地址
        imap_port: IMAP端口
        
    Returns:
        MailcowReceiver: 接收器实例
    """
    return MailcowReceiver(imap_server, imap_port)