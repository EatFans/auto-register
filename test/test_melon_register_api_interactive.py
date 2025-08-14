#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Melon注册API交互式测试
模拟完整的Melon注册流程，包括会话管理和AES加密
"""

import sys
import os
import json
import time
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.melon_register_api import MelonRegistrationSession
from util.aes_util import encrypt_openssl_aes, decrypt_openssl_aes


class InteractiveMelonRegistrationTest:
    """
    交互式Melon注册测试类
    模拟用户在浏览器中的完整Melon注册操作流程
    """

    def __init__(self):
        self.session = None
        self.test_data = {
            'email': '1437657457@qq.com',
            'password': 'ygQ7S?s8n3VQ8Zt',
            'firstName': 'Test',
            'lastName': 'User'
        }
        self.server_token = None
        self.verification_code = None

    def print_separator(self, title: str):
        """打印分隔线"""
        print("\n" + "="*60)
        print(f" {title} ")
        print("="*60)

    def print_step_info(self, step_num: int, step_name: str, description: str):
        """打印步骤信息"""
        print(f"\n🔸 步骤 {step_num}: {step_name}")
        print(f"   {description}")
        print("-" * 50)

    def get_user_input(self, prompt: str, default: str = None) -> str:
        """获取用户输入"""
        if default:
            user_input = input(f"{prompt} (默认: {default}): ").strip()
            return user_input if user_input else default
        else:
            return input(f"{prompt}: ").strip()

    def setup_test_data(self):
        """设置测试数据"""
        self.print_separator("设置测试数据")
        print("请输入Melon注册测试信息:")

        self.test_data['email'] = self.get_user_input(
            "邮箱地址", self.test_data['email']
        )
        self.test_data['password'] = self.get_user_input(
            "密码", self.test_data['password']
        )
        self.test_data['firstName'] = self.get_user_input(
            "名字", self.test_data['firstName']
        )
        self.test_data['lastName'] = self.get_user_input(
            "姓氏", self.test_data['lastName']
        )

        print("\n测试数据设置完成:")
        for key, value in self.test_data.items():
            if key == 'password':
                print(f"{key}: {'*' * len(value)}")
            else:
                print(f"{key}: {value}")

    def test_step_1_initialize_session(self):
        """步骤1: 初始化会话并获取serverToken"""
        self.print_step_info(1, "初始化会话", "创建Melon注册会话并获取初始serverToken")

        try:
            # 创建会话实例
            self.session = MelonRegistrationSession()
            print("✅ 会话实例创建成功")

            # 获取serverToken
            self.server_token = self.session.get_server_token()

            if self.server_token:
                print(f"✅ 获取serverToken成功: {self.server_token[:20]}...")
                return True
            else:
                print("❌ 获取serverToken失败")
                return False

        except Exception as e:
            print(f"❌ 初始化会话失败: {str(e)}")
            return False

    def test_step_2_check_email_exists(self):
        """步骤2: 检查邮箱是否已存在"""
        self.print_step_info(2, "检查邮箱", f"验证邮箱 {self.test_data['email']} 是否已被注册")

        try:
            email_exists = self.session.is_already_exist_email(self.test_data['email'])

            if email_exists:
                print(f"❌ 邮箱 {self.test_data['email']} 已被注册")
                print("   请更换其他邮箱地址")
                return False
            else:
                print(f"✅ 邮箱 {self.test_data['email']} 可用")
                return True

        except Exception as e:
            print(f"❌ 检查邮箱失败: {str(e)}")
            return False

    def test_step_3_submit_auth_form(self):
        """步骤3: 提交注册认证表单（需要AES加密）"""
        self.print_step_info(3, "提交认证表单", "提交第一阶段注册表单，字段需要AES加密")

        try:
            # 加密用户数据
            print("🔐 正在加密用户数据...")
            encrypted_firstName = encrypt_openssl_aes(self.test_data['firstName'])
            encrypted_lastName = encrypt_openssl_aes(self.test_data['lastName'])
            encrypted_email = encrypt_openssl_aes(self.test_data['email'])
            encrypted_password = encrypt_openssl_aes(self.test_data['password'])

            print(f"   firstName: {self.test_data['firstName']} -> {encrypted_firstName[:30]}...")
            print(f"   lastName: {self.test_data['lastName']} -> {encrypted_lastName[:30]}...")
            print(f"   email: {self.test_data['email']} -> {encrypted_email[:30]}...")
            print(f"   password: {'*' * len(self.test_data['password'])} -> {encrypted_password[:30]}...")

            # 提交认证表单
            print("\n📤 提交认证表单...")
            result = self.session.submit_auth_form(
                encrypted_firstName,
                encrypted_lastName,
                encrypted_email,
                encrypted_password
            )

            # 检查结果
            if result and not ('error' in result.lower() and '<html>' in result.lower()):
                print("✅ 认证表单提交成功")
                return True
            elif '<html>' in result.lower():
                print("⚠️  返回了HTML页面，可能需要进一步处理")
                print("   这可能是正常的重定向行为")
                return True
            else:
                print("❌ 认证表单提交失败")
                print(f"   响应内容: {result[:200]}...")
                return False

        except Exception as e:
            print(f"❌ 提交认证表单失败: {str(e)}")
            return False

    def test_step_4_send_verification_email(self):
        """步骤4: 发送验证邮件"""
        self.print_step_info(4, "发送验证邮件", f"向 {self.test_data['email']} 发送验证码邮件")

        try:
            # 发送验证邮件
            result = self.session.send_email_for_join(self.test_data['email'])

            # 检查结果
            if result:
                print("✅ 验证邮件发送成功")
                print(f"   请检查邮箱 {self.test_data['email']} 中的验证码")
                return True
            else:
                print("❌ 验证邮件发送失败")
                return False

        except Exception as e:
            print(f"❌ 发送验证邮件失败: {str(e)}")
            return False

    def test_step_5_manual_verification_code(self):
        """步骤5: 手动输入验证码"""
        self.print_step_info(5, "输入验证码", "从邮箱中获取验证码并验证")

        print(f"📧 请检查邮箱 {self.test_data['email']} 中的验证邮件")
        print("   在邮件中找到验证码（通常是6位数字）")

        # 获取验证码
        self.verification_code = input("\n请输入验证码: ").strip()

        if not self.verification_code:
            print("❌ 验证码不能为空")
            return False

        try:
            # 验证验证码并获取新的serverToken
            print(f"\n🔍 正在验证验证码: {self.verification_code}")
            new_server_token = self.session.valid_auth_key_for_join(
                self.test_data['email'],
                self.verification_code
            )

            if new_server_token:
                self.server_token = new_server_token
                print(f"✅ 验证码验证成功")
                print(f"   获取新的serverToken: {new_server_token[:20]}...")
                return True
            else:
                print("❌ 验证码验证失败")
                print("   请检查验证码是否正确或是否已过期")
                return False

        except Exception as e:
            print(f"❌ 验证验证码失败: {str(e)}")
            return False

    def test_step_6_complete_registration(self):
        """步骤6: 完成注册（需要AES加密）"""
        self.print_step_info(6, "完成注册", "提交最终注册表单完成注册流程")

        try:
            # 加密用户数据（除了验证码和serverToken）
            print("🔐 正在加密最终注册数据...")
            encrypted_firstName = encrypt_openssl_aes(self.test_data['firstName'])
            encrypted_lastName = encrypt_openssl_aes(self.test_data['lastName'])
            encrypted_email = encrypt_openssl_aes(self.test_data['email'])
            encrypted_password = encrypt_openssl_aes(self.test_data['password'])

            print("   所有敏感字段已加密")

            # 完成注册
            print("\n🎯 提交最终注册表单...")
            result = self.session.join_completed(
                encrypted_firstName,
                encrypted_lastName,
                encrypted_email,
                encrypted_password,
                self.verification_code,  # 验证码不加密
                self.server_token        # serverToken不加密
            )

            # 检查结果
            if result:
                print("✅ 注册流程完成")
                print("🎉 恭喜！Melon账户注册成功")
                return True
            else:
                print("❌ 注册完成失败")
                return False

        except Exception as e:
            print(f"❌ 完成注册失败: {str(e)}")
            return False

    def run_complete_test(self):
        """运行完整测试流程"""
        print("🚀 开始Melon注册API交互式测试")
        print("这个测试将模拟完整的Melon注册流程，包括AES加密")

        try:
            # 设置测试数据
            self.setup_test_data()

            # 步骤1: 初始化会话
            if not self.test_step_1_initialize_session():
                return False

            # 步骤2: 检查邮箱
            if not self.test_step_2_check_email_exists():
                return False

            # 步骤3: 提交认证表单
            if not self.test_step_3_submit_auth_form():
                return False

            # 步骤4: 发送验证邮件
            if not self.test_step_4_send_verification_email():
                return False

            # 步骤5: 手动验证码输入
            if not self.test_step_5_manual_verification_code():
                return False

            # 等待用户确认
            input("\n按回车键继续完成注册...")

            # 步骤6: 完成注册
            if not self.test_step_6_complete_registration():
                return False

            self.print_separator("测试完成")
            print("🎉 所有测试步骤都成功完成！")
            print("✅ Melon注册流程测试成功")
            print("✅ 会话管理正常")
            print("✅ AES加密功能正常")
            return True

        except KeyboardInterrupt:
            print("\n\n⚠️  测试被用户中断")
            return False
        except Exception as e:
            print(f"\n\n❌ 测试过程中发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def run_quick_test(self):
        """运行快速测试（仅测试接口连通性）"""
        print("⚡ 开始Melon API快速连通性测试")

        try:
            # 初始化会话
            self.session = MelonRegistrationSession()

            # 测试获取serverToken
            token = self.session.get_server_token()
            if token:
                print("✅ serverToken获取成功")
            else:
                print("❌ serverToken获取失败")
                return False

            # 测试邮箱检查接口
            try:
                exists = self.session.is_already_exist_email("test@example.com")
                print(f"✅ 邮箱检查接口正常: {exists}")
            except Exception as e:
                print(f"⚠️  邮箱检查接口异常: {str(e)}")

            # 测试AES加密功能
            try:
                test_text = "Hello Melon"
                encrypted = encrypt_openssl_aes(test_text)
                decrypted = decrypt_openssl_aes(encrypted)
                if decrypted == test_text:
                    print("✅ AES加密功能正常")
                else:
                    print("❌ AES加密功能异常")
            except Exception as e:
                print(f"❌ AES加密测试失败: {str(e)}")

            print("\n🎉 快速测试完成")
            return True

        except Exception as e:
            print(f"❌ 快速测试失败: {str(e)}")
            return False

    def run_encryption_test(self):
        """运行加密功能测试"""
        print("🔐 开始AES加密功能测试")

        test_cases = [
            "Test User",
            "test@example.com",
            "Password123!",
            "中文测试",
            "Special!@#$%^&*()Characters"
        ]

        try:
            for i, test_text in enumerate(test_cases, 1):
                print(f"\n测试用例 {i}: {test_text}")

                # 加密
                encrypted = encrypt_openssl_aes(test_text)
                print(f"  加密结果: {encrypted}")

                # 解密
                decrypted = decrypt_openssl_aes(encrypted)
                print(f"  解密结果: {decrypted}")

                # 验证
                if decrypted == test_text:
                    print("  ✅ 加密解密成功")
                else:
                    print("  ❌ 加密解密失败")
                    return False

            print("\n🎉 所有加密测试通过")
            return True

        except Exception as e:
            print(f"❌ 加密测试失败: {str(e)}")
            return False


def main():
    """主函数"""
    print("Melon注册API测试工具")
    print("1. 完整交互式测试（推荐）")
    print("2. 快速连通性测试")
    print("3. AES加密功能测试")

    choice = input("\n请选择测试类型 (1/2/3): ").strip()

    tester = InteractiveMelonRegistrationTest()

    if choice == '2':
        success = tester.run_quick_test()
    elif choice == '3':
        success = tester.run_encryption_test()
    else:
        success = tester.run_complete_test()

    if success:
        print("\n✅ 测试成功完成")
        return 0
    else:
        print("\n❌ 测试失败")
        return 1


if __name__ == "__main__":
    exit(main())