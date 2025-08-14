#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用邮件抓取器
支持主流邮箱服务（QQ邮箱、Gmail、Outlook等）
用于接收和处理指定发件人的邮件
"""

import imaplib
import email
import re
import ssl
from typing import List, Dict, Optional, Tuple
from email.header import decode_header
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import logging


class EmailConfig:
    """邮箱配置类"""
    
    def __init__(self, email_address: str, password: str, imap_server: str, 
                 imap_port: int = 993, use_ssl: bool = True, verify_ssl: bool = False):
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.use_ssl = use_ssl
        self.verify_ssl = verify_ssl  # 是否验证SSL证书


class EmailFetcher:
    """通用邮件抓取器"""
    
    # 主流邮箱服务器配置
    IMAP_SERVERS = {
        # QQ邮箱
        'qq.com': {'server': 'imap.qq.com', 'port': 993, 'ssl': True},
        'foxmail.com': {'server': 'imap.qq.com', 'port': 993, 'ssl': True},
        
        # Gmail
        'gmail.com': {'server': 'imap.gmail.com', 'port': 993, 'ssl': True},
        'googlemail.com': {'server': 'imap.gmail.com', 'port': 993, 'ssl': True},
        
        # Outlook/Hotmail
        'outlook.com': {'server': 'outlook.office365.com', 'port': 993, 'ssl': True},
        'hotmail.com': {'server': 'outlook.office365.com', 'port': 993, 'ssl': True},
        'live.com': {'server': 'outlook.office365.com', 'port': 993, 'ssl': True},
        'msn.com': {'server': 'outlook.office365.com', 'port': 993, 'ssl': True},
        
        # 163邮箱
        '163.com': {'server': 'imap.163.com', 'port': 993, 'ssl': True},
        
        # 126邮箱
        '126.com': {'server': 'imap.126.com', 'port': 993, 'ssl': True},
        
        # 新浪邮箱
        'sina.com': {'server': 'imap.sina.com', 'port': 993, 'ssl': True},
        'sina.cn': {'server': 'imap.sina.com', 'port': 993, 'ssl': True},
        
        # 雅虎邮箱
        'yahoo.com': {'server': 'imap.mail.yahoo.com', 'port': 993, 'ssl': True},
        'yahoo.cn': {'server': 'imap.mail.yahoo.com', 'port': 993, 'ssl': True},
    }
    
    def __init__(self, email_address: str, password: str, custom_config: Optional[EmailConfig] = None):
        """
        初始化邮件抓取器
        
        Args:
            email_address: 邮箱地址
            password: 邮箱密码或应用专用密码
            custom_config: 自定义邮箱配置（可选）
        """
        self.email_address = email_address
        self.password = password
        self.imap = None
        self.connected = False
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
        # 获取邮箱配置
        if custom_config:
            self.config = custom_config
        else:
            self.config = self._get_email_config(email_address)
    
    def _get_email_config(self, email_address: str) -> EmailConfig:
        """根据邮箱地址自动获取配置"""
        domain = email_address.split('@')[1].lower()
        
        if domain in self.IMAP_SERVERS:
            server_info = self.IMAP_SERVERS[domain]
            return EmailConfig(
                email_address=email_address,
                password=self.password,
                imap_server=server_info['server'],
                imap_port=server_info['port'],
                use_ssl=server_info['ssl'],
                verify_ssl=False  # 默认不验证SSL证书，避免证书问题
            )
        else:
            raise ValueError(f"不支持的邮箱域名: {domain}。支持的域名: {list(self.IMAP_SERVERS.keys())}")
    
    def connect(self) -> bool:
        """连接到邮箱服务器"""
        try:
            if self.config.use_ssl:
                # 创建SSL上下文
                context = ssl.create_default_context()
                
                # 根据配置决定是否验证SSL证书
                if not self.config.verify_ssl:
                    # 跳过SSL证书验证（用于解决证书问题）
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    self.logger.warning("SSL证书验证已禁用，这可能存在安全风险")
                
                self.imap = imaplib.IMAP4_SSL(self.config.imap_server, self.config.imap_port, ssl_context=context)
            else:
                self.imap = imaplib.IMAP4(self.config.imap_server, self.config.imap_port)
            
            # 登录
            self.imap.login(self.config.email_address, self.config.password)
            self.connected = True
            self.logger.info(f"成功连接到邮箱: {self.config.email_address}")
            return True
            
        except Exception as e:
            self.logger.error(f"连接邮箱失败: {str(e)}")
            self.connected = False
            return False
    
    def disconnect(self):
        """断开邮箱连接"""
        if self.imap and self.connected:
            try:
                self.imap.close()
                self.imap.logout()
                self.connected = False
                self.logger.info("已断开邮箱连接")
            except Exception as e:
                self.logger.error(f"断开连接时出错: {str(e)}")
    
    def select_folder(self, folder: str = 'INBOX') -> bool:
        """选择邮箱文件夹"""
        if not self.connected:
            self.logger.error("邮箱未连接")
            return False
        
        try:
            status, messages = self.imap.select(folder)
            if status == 'OK':
                self.logger.info(f"成功选择文件夹: {folder}")
                return True
            else:
                self.logger.error(f"选择文件夹失败: {folder}")
                return False
        except Exception as e:
            self.logger.error(f"选择文件夹时出错: {str(e)}")
            return False
    
    def search_emails(self, sender: Optional[str] = None, subject: Optional[str] = None, 
                     since_date: Optional[str] = None, unseen_only: bool = False) -> List[int]:
        """搜索邮件
        
        Args:
            sender: 发件人邮箱地址
            subject: 邮件主题关键词
            since_date: 起始日期 (格式: 'DD-MMM-YYYY', 例如: '01-Jan-2024')
            unseen_only: 是否只搜索未读邮件
            
        Returns:
            邮件ID列表
        """
        if not self.connected:
            self.logger.error("邮箱未连接")
            return []
        
        # 构建搜索条件
        search_criteria = []
        
        if sender:
            search_criteria.append(f'FROM "{sender}"')
        
        if subject:
            search_criteria.append(f'SUBJECT "{subject}"')
        
        if since_date:
            search_criteria.append(f'SINCE {since_date}')
        
        if unseen_only:
            search_criteria.append('UNSEEN')
        
        # 如果没有指定条件，搜索所有邮件
        if not search_criteria:
            search_criteria = ['ALL']
        
        search_string = ' '.join(search_criteria)
        
        try:
            status, messages = self.imap.search(None, search_string)
            if status == 'OK':
                email_ids = messages[0].split()
                email_ids = [int(id) for id in email_ids]
                self.logger.info(f"找到 {len(email_ids)} 封邮件")
                return email_ids
            else:
                self.logger.error(f"搜索邮件失败: {status}")
                return []
        except Exception as e:
            self.logger.error(f"搜索邮件时出错: {str(e)}")
            return []
    
    def fetch_email(self, email_id: int) -> Optional[Dict]:
        """获取邮件详情
        
        Args:
            email_id: 邮件ID
            
        Returns:
            邮件信息字典，包含主题、发件人、收件人、日期、正文等
        """
        if not self.connected:
            self.logger.error("邮箱未连接")
            return None
        
        try:
            status, msg_data = self.imap.fetch(str(email_id), '(RFC822)')
            if status != 'OK':
                self.logger.error(f"获取邮件失败: {email_id}")
                return None
            
            # 解析邮件
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # 提取邮件信息
            email_info = {
                'id': email_id,
                'subject': self._decode_header(email_message['Subject']),
                'from': self._decode_header(email_message['From']),
                'to': self._decode_header(email_message['To']),
                'date': email_message['Date'],
                'message_id': email_message['Message-ID'],
                'content_type': email_message.get_content_type(),
                'body': self._extract_body(email_message),
                'html_body': self._extract_html_body(email_message),
                'text_body': self._extract_text_body(email_message)
            }
            
            return email_info
            
        except Exception as e:
            self.logger.error(f"获取邮件时出错: {str(e)}")
            return None
    
    def _decode_header(self, header: str) -> str:
        """解码邮件头"""
        if not header:
            return ''
        
        try:
            decoded_parts = decode_header(header)
            decoded_string = ''
            
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
            self.logger.error(f"解码邮件头时出错: {str(e)}")
            return str(header)
    
    def _extract_body(self, email_message) -> str:
        """提取邮件正文（优先HTML，其次文本）"""
        html_body = self._extract_html_body(email_message)
        if html_body:
            return html_body
        
        text_body = self._extract_text_body(email_message)
        return text_body or ''
    
    def _extract_html_body(self, email_message) -> str:
        """提取HTML正文"""
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == 'text/html':
                        charset = part.get_content_charset() or 'utf-8'
                        body = part.get_payload(decode=True)
                        if isinstance(body, bytes):
                            return body.decode(charset, errors='ignore')
                        return str(body)
            else:
                if email_message.get_content_type() == 'text/html':
                    charset = email_message.get_content_charset() or 'utf-8'
                    body = email_message.get_payload(decode=True)
                    if isinstance(body, bytes):
                        return body.decode(charset, errors='ignore')
                    return str(body)
        except Exception as e:
            self.logger.error(f"提取HTML正文时出错: {str(e)}")
        
        return ''
    
    def _extract_text_body(self, email_message) -> str:
        """提取纯文本正文"""
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == 'text/plain':
                        charset = part.get_content_charset() or 'utf-8'
                        body = part.get_payload(decode=True)
                        if isinstance(body, bytes):
                            return body.decode(charset, errors='ignore')
                        return str(body)
            else:
                if email_message.get_content_type() == 'text/plain':
                    charset = email_message.get_content_charset() or 'utf-8'
                    body = email_message.get_payload(decode=True)
                    if isinstance(body, bytes):
                        return body.decode(charset, errors='ignore')
                    return str(body)
        except Exception as e:
            self.logger.error(f"提取文本正文时出错: {str(e)}")
        
        return ''
    
    def extract_verification_code(self, email_content: str, patterns: Optional[List[str]] = None) -> Optional[str]:
        """从邮件内容中提取验证码
        
        Args:
            email_content: 邮件内容（HTML或文本）
            patterns: 自定义正则表达式模式列表
            
        Returns:
            提取到的验证码，如果没有找到则返回None
        """
        if not email_content:
            return None
        
        # 如果是HTML内容，先提取纯文本
        if '<html' in email_content.lower() or '<body' in email_content.lower():
            try:
                soup = BeautifulSoup(email_content, 'html.parser')
                text_content = soup.get_text()
            except Exception:
                text_content = email_content
        else:
            text_content = email_content
        
        # 默认验证码匹配模式
        default_patterns = [
            r'验证码[：:]*\s*([A-Za-z0-9]{4,8})',  # 中文验证码
            r'verification code[：:]*\s*([A-Za-z0-9]{4,8})',  # 英文验证码
            r'code[：:]*\s*([A-Za-z0-9]{4,8})',  # 简单code
            r'([A-Za-z0-9]{6})',  # 6位数字字母组合
            r'([0-9]{4,8})',  # 4-8位纯数字
            r'\b([A-Z0-9]{4,8})\b',  # 4-8位大写字母数字组合
        ]
        
        # 使用自定义模式或默认模式
        search_patterns = patterns or default_patterns
        
        for pattern in search_patterns:
            try:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    # 返回第一个匹配的验证码
                    code = matches[0] if isinstance(matches[0], str) else matches[0][0]
                    self.logger.info(f"找到验证码: {code}")
                    return code
            except Exception as e:
                self.logger.error(f"正则匹配时出错: {str(e)}")
                continue
        
        self.logger.warning("未找到验证码")
        return None
    
    def get_emails_from_sender(self, sender: str, subject_keywords: Optional[List[str]] = None, 
                              unseen_only: bool = False, limit: int = 1) -> List[Dict]:
        """获取指定发件人的邮件
        
        Args:
            sender: 发件人邮箱地址
            subject_keywords: 主题关键词列表（可选）
            unseen_only: 是否只获取未读邮件
            limit: 最大邮件数量限制，默认为1（只获取最新的一封）
            
        Returns:
            邮件信息列表，按时间倒序排列（最新的在前）
        """
        if not self.connected:
            if not self.connect():
                return []
        
        if not self.select_folder():
            return []
        
        try:
            # 搜索邮件
            email_ids = self.search_emails(sender=sender, unseen_only=unseen_only)
            
            # 按时间倒序排列（最新的在前）
            email_ids = sorted(email_ids, reverse=True)
            
            # 限制邮件数量（取最新的邮件）
            if limit > 0:
                email_ids = email_ids[:limit]
            
            emails = []
            for email_id in email_ids:
                email_info = self.fetch_email(email_id)
                if email_info:
                    # 检查主题关键词（如果指定）
                    if subject_keywords:
                        subject = email_info.get('subject', '').lower()
                        if not any(keyword.lower() in subject for keyword in subject_keywords):
                            continue
                    
                    emails.append(email_info)
            
            self.logger.info(f"找到来自 {sender} 的 {len(emails)} 封邮件")
            return emails
            
        except Exception as e:
            self.logger.error(f"获取邮件时出错: {str(e)}")
            return []
    
    def mark_as_read(self, email_id: int) -> bool:
        """标记邮件为已读"""
        if not self.connected:
            return False
        
        try:
            self.imap.store(str(email_id), '+FLAGS', '\\Seen')
            return True
        except Exception as e:
            self.logger.error(f"标记邮件已读时出错: {str(e)}")
            return False
    
    def delete_email(self, email_id: int) -> bool:
        """删除邮件"""
        if not self.connected:
            return False
        
        try:
            self.imap.store(str(email_id), '+FLAGS', '\\Deleted')
            self.imap.expunge()
            return True
        except Exception as e:
            self.logger.error(f"删除邮件时出错: {str(e)}")
            return False
    
    def get_folder_list(self) -> List[str]:
        """获取邮箱文件夹列表"""
        if not self.connected:
            return []
        
        try:
            status, folders = self.imap.list()
            if status == 'OK':
                folder_list = []
                for folder in folders:
                    # 解析文件夹名称
                    folder_name = folder.decode().split('"')[-2]
                    folder_list.append(folder_name)
                return folder_list
        except Exception as e:
            self.logger.error(f"获取文件夹列表时出错: {str(e)}")
        
        return []


# 使用示例
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # 示例：QQ邮箱
    qq_fetcher = EmailFetcher('1437657457@qq.com', 'nxipsohiztzjgfai')
    
    if qq_fetcher.connect():
        # 获取指定发件人的最新邮件
        emails = qq_fetcher.get_emails_from_sender(
            sender='eatfan0921@163.com'
            # 默认只获取最新的1封邮件
        )
        
        for email_info in emails:
            print(f"邮件主题: {email_info['subject']}")
            print(f"发件人: {email_info['from']}")
            print(f"日期: {email_info['date']}")
            
            # 提取验证码
            code = qq_fetcher.extract_verification_code(email_info['body'])
            if code:
                print(f"验证码: {code}")
            
            # 标记为已读
            qq_fetcher.mark_as_read(email_info['id'])
            print("-" * 50)
        
        qq_fetcher.disconnect()