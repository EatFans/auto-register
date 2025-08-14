import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'email'))
from email_fetcher import EmailFetcher
from util.emai_util import extract_melon_code_value

# 使用示例
if __name__ == "__main__":
    # 配置日志

    # 示例：QQ邮箱
    qq_fetcher = EmailFetcher('1437657457@qq.com', 'nxipsohiztzjgfai')

    if qq_fetcher.connect():
        # 获取指定发件人的最新邮件
        emails = qq_fetcher.get_emails_from_sender(
            sender='noreply_melonticket@kakaoent.com'
            # 默认只获取最新的1封邮件
        )

        for email_info in emails:
            print(f"邮件主题: {email_info['subject']}")
            print(f"发件人: {email_info['from']}")
            print(f"日期: {email_info['date']}")

            # 提取验证码
            print(extract_melon_code_value(email_info['body']))

            # 标记为已读
            qq_fetcher.mark_as_read(email_info['id'])
            print("-" * 50)

        qq_fetcher.disconnect()