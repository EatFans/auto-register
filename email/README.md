# 邮件抓取器 (EmailFetcher)

通用邮件抓取器，支持主流邮箱服务（QQ邮箱、Gmail、Outlook等），用于接收和处理指定发件人的邮件。

## 功能特性

- 🔧 **自动配置**: 根据邮箱地址自动识别IMAP服务器配置
- 📧 **多邮箱支持**: 支持QQ、Gmail、Outlook、163、126、新浪、雅虎等主流邮箱
- 🔍 **智能搜索**: 支持按发件人、主题、日期等条件搜索邮件
- 🔐 **验证码提取**: 内置多种验证码提取模式，支持自定义正则表达式
- ⏰ **等待机制**: 支持等待指定发件人邮件，适用于自动化场景
- 📝 **完整解析**: 支持HTML和纯文本邮件解析
- 🛡️ **安全连接**: 支持SSL/TLS加密连接

## 支持的邮箱服务

| 邮箱服务 | 域名 | IMAP服务器 | 端口 |
|---------|------|------------|------|
| QQ邮箱 | qq.com, foxmail.com | imap.qq.com | 993 |
| Gmail | gmail.com, googlemail.com | imap.gmail.com | 993 |
| Outlook | outlook.com, hotmail.com, live.com, msn.com | outlook.office365.com | 993 |
| 163邮箱 | 163.com | imap.163.com | 993 |
| 126邮箱 | 126.com | imap.126.com | 993 |
| 新浪邮箱 | sina.com, sina.cn | imap.sina.com | 993 |
| 雅虎邮箱 | yahoo.com, yahoo.cn | imap.mail.yahoo.com | 993 |

## 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 基本使用

```python
from email_fetcher import EmailFetcher
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)

# 创建邮件抓取器（自动配置）
fetcher = EmailFetcher('your_email@qq.com', 'your_app_password')

# 连接邮箱
if fetcher.connect():
    # 获取指定发件人的最新邮件
    emails = fetcher.get_emails_from_sender(
        sender='noreply@example.com',
        subject_keywords=['验证', 'verification'],  # 主题关键词
        unseen_only=True  # 只获取未读邮件
        # 默认只获取最新的1封邮件
    )
    
    for email_info in emails:
        print(f"邮件主题: {email_info['subject']}")
        print(f"发件人: {email_info['from']}")
        
        # 提取验证码
        verification_code = fetcher.extract_verification_code(email_info['body'])
        if verification_code:
            print(f"验证码: {verification_code}")
        
        # 标记为已读
        fetcher.mark_as_read(email_info['id'])
    
    # 断开连接
    fetcher.disconnect()
```

### 自定义配置

```python
from email_fetcher import EmailFetcher, EmailConfig

# 自定义邮箱配置
custom_config = EmailConfig(
    email_address='your_email@custom.com',
    password='your_password',
    imap_server='imap.custom.com',
    imap_port=993,
    use_ssl=True
)

fetcher = EmailFetcher('your_email@custom.com', 'your_password', custom_config)
```

### 搜索邮件

```python
# 搜索特定发件人的邮件
email_ids = fetcher.search_emails(sender='noreply@example.com')

# 搜索包含特定主题的邮件
email_ids = fetcher.search_emails(subject='验证码')

# 搜索未读邮件
email_ids = fetcher.search_emails(unseen_only=True)

# 组合搜索条件
email_ids = fetcher.search_emails(
    sender='noreply@example.com',
    subject='验证',
    since_date='01-Jan-2024',
    unseen_only=True
)
```

### 获取邮件详情

```python
for email_id in email_ids:
    email_info = fetcher.fetch_email(email_id)
    if email_info:
        print(f"主题: {email_info['subject']}")
        print(f"发件人: {email_info['from']}")
        print(f"日期: {email_info['date']}")
        print(f"正文: {email_info['body'][:100]}...")
```

### 验证码提取

```python
# 使用默认模式提取验证码
code = fetcher.extract_verification_code(email_content)

# 使用自定义正则表达式
custom_patterns = [
    r'PIN[：:]*\s*([0-9]{4})',  # PIN码
    r'激活码[：:]*\s*([A-Z0-9]{8})',  # 激活码
]
code = fetcher.extract_verification_code(email_content, custom_patterns)
```

## 邮箱配置说明

### QQ邮箱

1. 登录QQ邮箱网页版
2. 进入「设置」→「账户」
3. 开启「IMAP/SMTP服务」
4. 获取授权码（不是QQ密码）
5. 使用授权码作为密码

```python
fetcher = EmailFetcher('your_qq@qq.com', 'your_authorization_code')
```

### Gmail

1. 开启两步验证
2. 生成应用专用密码
3. 使用应用专用密码

```python
fetcher = EmailFetcher('your_email@gmail.com', 'your_app_password')
```

### Outlook

可以直接使用账户密码，但建议使用应用密码：

1. 登录Microsoft账户
2. 进入安全设置
3. 生成应用密码

```python
fetcher = EmailFetcher('your_email@outlook.com', 'your_password')
```

## API 参考

### EmailFetcher 类

#### 初始化

```python
EmailFetcher(email_address: str, password: str, custom_config: Optional[EmailConfig] = None)
```

#### 主要方法

- `connect() -> bool`: 连接邮箱服务器
- `disconnect()`: 断开连接
- `select_folder(folder: str = 'INBOX') -> bool`: 选择邮箱文件夹
- `search_emails(**kwargs) -> List[int]`: 搜索邮件
- `fetch_email(email_id: int) -> Optional[Dict]`: 获取邮件详情
- `get_emails_from_sender(sender: str, **kwargs) -> List[Dict]`: 获取指定发件人邮件
- `extract_verification_code(content: str, patterns: Optional[List[str]] = None) -> Optional[str]`: 提取验证码
- `mark_as_read(email_id: int) -> bool`: 标记已读
- `delete_email(email_id: int) -> bool`: 删除邮件

### EmailConfig 类

```python
EmailConfig(
    email_address: str,
    password: str,
    imap_server: str,
    imap_port: int = 993,
    use_ssl: bool = True,
    verify_ssl: bool = False  # 是否验证SSL证书
)
```

## 错误处理

```python
try:
    fetcher = EmailFetcher('your_email@qq.com', 'password')
    if fetcher.connect():
        # 执行邮件操作
        pass
    else:
        print("连接失败，请检查邮箱配置")
except ValueError as e:
    print(f"配置错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")
finally:
    if fetcher.connected:
        fetcher.disconnect()
```

## SSL证书配置

### 默认配置（推荐）

默认情况下，邮件抓取器禁用SSL证书验证以避免证书问题：

```python
# 自动配置默认禁用SSL验证
fetcher = EmailFetcher('your_email@qq.com', 'your_password')
# 等同于 verify_ssl=False
```

### 启用SSL验证（更安全）

如果需要更高的安全性，可以启用SSL证书验证：

```python
# 启用SSL证书验证
secure_config = EmailConfig(
    email_address='your_email@gmail.com',
    password='your_password',
    imap_server='imap.gmail.com',
    imap_port=993,
    use_ssl=True,
    verify_ssl=True  # 启用SSL证书验证
)
fetcher = EmailFetcher('your_email@gmail.com', 'your_password', secure_config)
```

### SSL证书问题解决

如果遇到SSL证书错误（如 `CERTIFICATE_VERIFY_FAILED`），可以：

1. **使用默认配置**（推荐）：自动禁用SSL验证
2. **手动禁用SSL验证**：
   ```python
   config = EmailConfig(..., verify_ssl=False)
   ```
3. **更新证书**：更新系统证书或Python环境

## 注意事项

1. **安全性**: 不要在代码中硬编码密码，建议使用环境变量或配置文件
2. **频率限制**: 避免频繁连接和查询，可能触发邮箱服务商的限制
3. **网络环境**: 确保网络能够访问邮箱服务器
4. **授权码**: QQ邮箱和Gmail需要使用授权码/应用密码，不是登录密码
5. **SSL证书**: 默认禁用SSL验证以避免证书问题，如需更高安全性可启用

## 常见问题

### Q: 连接失败怎么办？

A: 检查以下几点：
- 邮箱地址和密码是否正确
- 是否开启了IMAP服务
- 是否使用了正确的授权码/应用密码
- 网络是否能访问邮箱服务器

### Q: 找不到验证码怎么办？

A: 可以尝试：
- 检查邮件内容格式
- 使用自定义正则表达式模式
- 查看完整的邮件正文

### Q: 支持其他邮箱吗？

A: 可以通过自定义配置支持其他邮箱服务，只需要知道IMAP服务器地址和端口。

## 许可证

本项目采用 MIT 许可证。