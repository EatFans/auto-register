# TODO melon网站注册

from register.base_register import BaseRegisterManager


class MelonRegisterManager(BaseRegisterManager):
    """
        Melon网站注册管理器
    """

    def get_website_name(self) -> str:
        """
        获取网站名称
        :return: 网站名称
        """
        return "Melon"

    def validate_config(self, **kwargs) -> bool:
        """
        验证Melon注册配置
        :param kwargs: 配置参数
        :return: 配置是否有效
        """
        # Melon注册使用临时邮箱API，不需要域名配置
        # 可以在这里添加其他必要的配置验证

        self.log(f"Melon注册配置验证通过（使用临时邮箱API）", "green")
        return True