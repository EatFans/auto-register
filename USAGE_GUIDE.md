# 注册机使用指南

## 概述

本注册机已经完成重构，集成了完整的注册流程，包括邮箱验证、邮箱激活和最终注册。系统现在使用统一的会话管理，确保注册过程的连续性和成功率。

## 主要改进

### 1. 完整的注册流程
- ✅ **邮箱验证**: 自动验证邮箱地址有效性
- ✅ **会话管理**: 统一管理整个注册过程的会话状态
- ✅ **错误处理**: 详细的错误信息和异常处理
- ✅ **多线程支持**: 支持并发注册提高效率
- ✅ **数据导出**: 自动导出注册结果到Excel文件

### 2. 新的架构设计
- **RegistrationSession类**: 统一会话状态管理
- **RegistrationManager类**: 完整注册流程管理
- **RegisterManager类**: 主要的注册业务逻辑
- **向后兼容**: 保持原有API的兼容性

## 使用方式

### 方式1: 图形界面 (推荐)

```bash
python main.py
```

启动图形界面后：
1. 选择注册模式（随机生成/导入数据）
2. 配置基础参数（邮箱域名、注册数量等）
3. 设置导出路径
4. 点击"开始注册"按钮

### 方式2: 编程接口

#### 随机生成模式
```python
from register.register import RegisterManager

# 创建注册管理器
register_manager = RegisterManager()

# 执行随机生成注册
register_manager.register_accounts_random(
    domain="gmail.com",
    count=5,
    name="",  # 空字符串表示随机生成
    birthday="1990-01-01",
    country="中国",
    gender="男",
    export_path="注册结果.xlsx",
    thread_count=3
)
```

#### 导入数据模式
```python
from register.register import RegisterManager

# 准备用户数据
user_data = [
    {
        'name': '张三',
        'birthday': '1990-01-01',
        'country': '中国',
        'gender': '男'
    },
    {
        'name': '李四',
        'birthday': '1992-05-15',
        'country': '中国',
        'gender': '女'
    }
]

# 创建注册管理器
register_manager = RegisterManager()

# 执行导入数据注册
register_manager.register_accounts_import(
    domain="gmail.com",
    user_data=user_data,
    export_path="注册结果.xlsx",
    thread_count=2
)
```

### 方式3: 底层API调用

```python
from api.register_api import RegistrationManager as APIRegistrationManager

# 使用API管理器进行完整注册流程
with APIRegistrationManager() as api_manager:
    # 步骤1: 验证邮箱
    verify_result = api_manager.verify_email_only('test@gmail.com')
    
    # 步骤2: 激活邮箱（需要从邮件获取k_token）
    # activate_result = api_manager.activate_email_only('test@gmail.com', 'k_token')
    
    # 步骤3: 提交注册
    register_result = api_manager.register_only(
        email='test@gmail.com',
        password='password123',
        surname='张',
        firstname='三',
        nation=43,
        birth='19900101',
        gender='m'
    )
```

## 配置参数说明

### 基础参数
- **邮箱域名**: 生成邮箱地址使用的域名（如：gmail.com）
- **注册数量**: 要注册的账号数量
- **线程数**: 并发注册的线程数（建议1-10，过多可能被服务器限制）
- **导出路径**: 注册结果保存的Excel文件路径

### 用户信息参数
- **姓名**: 用户姓名（随机模式下可留空自动生成）
- **生日**: 格式为YYYY-MM-DD（如：1990-01-01）
- **国家**: 国家名称（如：中国、美国等）
- **性别**: 男/女 或 m/f

### 国家代码映射
系统内置了常用国家的代码映射：
- 中国: 43
- 美国: 1
- 日本: 81
- 韩国: 82
- 英国: 44
- 德国: 49
- 法国: 33
- 加拿大: 1
- 澳大利亚: 61

## 测试系统

运行测试脚本验证系统功能：

```bash
python test_registration.py
```

测试选项：
1. API函数基本功能测试
2. 单个账号注册流程测试
3. 导入数据模式注册测试
4. 全部测试

## 注意事项

### 1. 邮件激活处理
当前版本的邮件激活步骤需要手动处理：
1. 系统会发送验证邮件到指定邮箱
2. 用户需要手动点击邮件中的激活链接
3. 从激活链接中获取k_token参数
4. 将k_token用于后续的注册步骤

**未来版本将集成自动邮件处理功能**

### 2. 会话状态管理
- 系统使用requests.Session自动管理Cookie和会话状态
- 确保整个注册流程在同一会话中完成
- 避免"Your information is not found"错误

### 3. 错误处理
- 系统提供详细的错误日志
- 支持重试机制
- 自动处理网络异常和超时

### 4. 性能优化
- 支持多线程并发注册
- 建议线程数不超过10个
- 避免对目标服务器造成过大压力

## 故障排除

### 常见问题

1. **邮箱验证失败**
   - 检查网络连接
   - 确认邮箱域名格式正确
   - 查看详细错误日志

2. **注册失败**
   - 确保邮箱已经通过验证
   - 检查用户信息格式是否正确
   - 验证国家代码映射

3. **导出失败**
   - 检查导出路径是否有写入权限
   - 确认目录存在
   - 检查磁盘空间

### 日志分析
系统提供彩色日志输出：
- 🔵 蓝色：信息提示
- 🟡 黄色：警告信息
- 🟢 绿色：成功操作
- 🔴 红色：错误信息

## 扩展功能

### 邮件处理器集成
系统预留了邮件处理器接口，可以集成自动邮件处理功能：

```python
# 集成邮件处理器（示例）
register_manager.integrate_email_processor(email_processor)
```

### 自定义国家代码
可以扩展国家代码映射表：

```python
# 在_get_country_code方法中添加更多映射
country_mapping = {
    '中国': 43,
    '新加坡': 65,
    # 添加更多国家...
}
```

## 版本信息

- **当前版本**: 2.0.0
- **更新日期**: 2024年
- **主要特性**: 完整注册流程、会话管理、多线程支持

## 技术支持

如遇到问题，请：
1. 查看详细的错误日志
2. 运行测试脚本验证系统状态
3. 检查网络连接和目标服务器状态
4. 参考本文档的故障排除部分

---

**注意**: 请合理使用本工具，遵守相关网站的服务条款和法律法规。