# 测试melon注册接口
from api.melon_register_api import *
from util.aes_util import *

if __name__ == '__main__':
    fistName = "Test"
    lastName = "User"
    email = "2180654922@qq.com"
    password = "fdsahjir1232"

    # 获取第一阶段的serverToken
    serverToken = melon_get_server_token()

    # 提交第一阶段的注册表单
    melon_auth_for_join(fistName, lastName, email, password, serverToken)

    # 发送邮箱验证码
    send_email_for_join(email)

    # 手动获取一下邮箱的code
    code:str = input().strip()

    # 验证邮件验证码，获取第二阶段的serverToken
    serverToken = valid_auth_key_for_join(email,code)

    # 提交最终注册表单
    melon_join_completed(fistName, lastName, email, password,code,serverToken)