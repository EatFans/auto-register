# 邮件处理模块

本模块提供了完整的邮件接收和验证处理功能，专门用于处理大批量邮箱注册后的验证邮件接收和k值提取。

## 功能特性

- 🔗 **Mailcow支持**: 专门为自建Mailcow邮箱服务器优化
- 📧 **邮件接收**: 通过IMAP协议接收邮件
- 🔍 **智能解析**: 自动解析HTML和纯文本邮件内容
- 🎯 **k值提取**: 专门提取YES24验证邮件中的k参数
- ⚡ **批量处理**: 支持多线程并发处理多个邮箱
- 📊 **状态监控**: 实时监控处理状态和进度
- 🔄 **自动重试**: 智能等待和重试机制

## 文件说明

### 核心模块

- **`mailcow_receiver.py`**: Mailcow邮箱接收器，处理单个邮箱的连接和邮件解析
- **`batch_email_processor.py`**: 批量邮件处理器，管理多个邮箱的并发处理
- **`email_usage_example.py`**: 使用示例，展示各种使用场景

### 原有文件

- **`email_handler.py`**: 原有的邮件处理类（保持兼容）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置Mailcow服务器

```python
# 配置你的Mailcow服务器信息
IMAP_SERVER = "mail.yourdomain.com"  # 你的Mailcow服务器地址
IMAP_PORT = 993                      # IMAP端口（SSL）
```

### 3. 单个邮箱处理

```python
from email.mailcow_receiver import create_mailcow_receiver

# 创建接收器
receiver = create_mailcow_receiver("mail.yourdomain.com", 993)

# 连接邮箱
if receiver.connect("test@yourdomain.com", "password"):
    # 等待验证邮件
    k_value = receiver.wait_for_verification_email(timeout=300)
    if k_value:
        print(f"找到k值: {k_value}")
    
    receiver.disconnect()
```

### 4. 批量邮箱处理

```python
from email.batch_email_processor import create_batch_processor

# 创建批量处理器
processor = create_batch_processor("mail.yourdomain.com", 993, max_workers=10)

# 设置回调函数
def on_k_value_found(email, k_value):
    print(f"邮箱 {email} 找到k值: {k_value}")

processor.set_callbacks(on_k_value_found=on_k_value_found)

# 添加邮箱账户
email_accounts = [
    {"email": "test1@yourdomain.com", "password": "pass1"},
    {"email": "test2@yourdomain.com", "password": "pass2"},
    # 更多邮箱...
]

for account in email_accounts:
    processor.add_email_account(account["email"], account["password"])

# 开始监控
processor.start_monitoring(timeout=300, check_interval=10)

# 获取结果
k_values = processor.get_k_values()
for email, k_value in k_values.items():
    print(f"{email}: {k_value}")

# 清理资源
processor.stop_monitoring()
```

## 与注册流程集成

### 典型的集成流程

1. **批量注册邮箱账户**
   ```python
   # 调用注册API
   for email_data in registration_list:
       register_api.register_account(email_data)
   ```

2. **添加到邮件监控**
   ```python
   processor = create_batch_processor(imap_server, imap_port)
   for email_data in registration_list:
       processor.add_email_account(email_data["email"], email_data["password"])
   ```

3. **监控验证邮件**
   ```python
   processor.start_monitoring(timeout=300)
   ```

4. **处理验证结果**
   ```python
   k_values = processor.get_k_values()
   for email, k_value in k_values.items():
       verification_url = f"https://ticket.yes24.com/Pages/English/member/FnMyAuthentication.aspx?k={k_value}"
       # 完成验证
   ```

## 配置说明

### Mailcow IMAP配置

- **服务器地址**: 你的Mailcow服务器域名或IP
- **端口**: 993 (IMAPS) 或 143 (IMAP)
- **SSL**: 建议使用SSL (端口993)
- **认证**: 使用邮箱完整地址和密码

### 性能调优

- **max_workers**: 并发线程数，建议根据服务器性能调整（默认10）
- **check_interval**: 检查间隔，建议10-30秒（默认10秒）
- **timeout**: 单个邮箱超时时间，建议300-600秒（默认300秒）

## 错误处理

### 常见错误及解决方案

1. **连接失败**
   - 检查IMAP服务器地址和端口
   - 确认邮箱账户和密码正确
   - 检查网络连接

2. **认证失败**
   - 确认邮箱密码正确
   - 检查Mailcow是否启用IMAP服务
   - 确认邮箱账户未被锁定

3. **邮件解析失败**
   - 检查邮件格式是否正确
   - 确认邮件内容包含验证链接
   - 查看日志获取详细错误信息

## 日志配置

```python
import logging

# 配置日志级别
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 安全注意事项

1. **密码安全**: 不要在代码中硬编码密码，使用环境变量或配置文件
2. **连接安全**: 建议使用SSL连接（端口993）
3. **权限控制**: 确保邮箱账户只有必要的权限
4. **日志安全**: 避免在日志中记录敏感信息

## 示例场景

详细的使用示例请参考 `email_usage_example.py` 文件，包含：

- 单个邮箱处理示例
- 批量邮箱处理示例
- 与注册流程集成示例

## 技术支持

如果遇到问题，请检查：

1. 依赖包是否正确安装
2. Mailcow服务器配置是否正确
3. 邮箱账户是否有效
4. 网络连接是否正常
5. 查看详细的错误日志