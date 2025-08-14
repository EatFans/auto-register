# 注册管理器工厂类
from typing import Dict, Type
from register.base_register import BaseRegisterManager
from register.yes24_register import Yes24RegisterManager

class RegisterManagerFactory:
    """
    注册管理器工厂类
    用于根据网站类型创建对应的注册管理器
    """
    
    # 注册的网站管理器映射
    _managers: Dict[str, Type[BaseRegisterManager]] = {
        'Yes24': Yes24RegisterManager,
        # 可以在这里添加更多网站的注册管理器
        # 'Amazon': AmazonRegisterManager,
        # 'eBay': EbayRegisterManager,
    }
    
    @classmethod
    def get_available_websites(cls) -> list:
        """
        获取所有可用的网站列表
        :return: 网站名称列表
        """
        return list(cls._managers.keys())
    
    @classmethod
    def create_manager(cls, website: str, log_callback=None, app_instance=None) -> BaseRegisterManager:
        """
        创建指定网站的注册管理器
        :param website: 网站名称
        :param log_callback: 日志回调函数
        :param app_instance: 应用实例
        :return: 注册管理器实例
        """
        if website not in cls._managers:
            raise ValueError(f"不支持的网站: {website}。支持的网站: {', '.join(cls.get_available_websites())}")
        
        manager_class = cls._managers[website]
        return manager_class(log_callback=log_callback, app_instance=app_instance)
    
    @classmethod
    def register_website(cls, website: str, manager_class: Type[BaseRegisterManager]):
        """
        注册新的网站管理器
        :param website: 网站名称
        :param manager_class: 管理器类
        """
        if not issubclass(manager_class, BaseRegisterManager):
            raise TypeError("管理器类必须继承自BaseRegisterManager")
        
        cls._managers[website] = manager_class
    
    @classmethod
    def is_website_supported(cls, website: str) -> bool:
        """
        检查是否支持指定网站
        :param website: 网站名称
        :return: 是否支持
        """
        return website in cls._managers
