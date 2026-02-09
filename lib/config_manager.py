from . import json_encrypt
import tkinter as tk
import copy

class ConfigManage:
    """进行配置记录与保存以及提供管理接口，单例模式"""
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.default_config = {}
        self._config = {}

        self.load_config() # 加载配置文件

    def load_config(self):
        """加载配置文件"""
        self._config.clear()
        self._config = json_encrypt.load_json(file_name="config.json", SECRET_KEY=json_encrypt.SECRET_KEY)

        self.verify_config() # 加载后立即验证配置项是否齐全，不齐全则补齐

    def write_config(self):
        """写入配置文件"""
        json_encrypt.write_json(save_file_name="config.json", save_file=self._config, SECRET_KEY=json_encrypt.SECRET_KEY)

    def register(self, config_name:str, default_value, config:dict[str] = None):
        """注册或修改一个默认配置项"""
        if type(config_name) != str:
            raise TypeError("config_name must be a string")

        self.default_config[config_name] = default_value
        if config_name not in self._config:
            self._config[config_name] = default_value

        if config is not None:
            for key, value in config.items():
                if type(key) != str:
                    raise TypeError("the key of config must be a string")
                
                self.default_config[key] = value
                if key not in self._config:
                    self._config[key] = value

        self.write_config()

    def unregister(self, config_name:str, config:dict[str] = None):
        """注销一个配置项"""
        if config_name in self.default_config:
            del self.default_config[config_name]

        if config_name in self._config:
            del self._config[config_name]

        if config is not None:
            for key in config:
                if key in self.default_config:
                    del self.default_config[key]

                if key in self._config:
                    del self._config[key]

        self.write_config()
        
    def set_config(self, config_name:str = None, config_value = None, config:dict[str] = None):
        """设置配置项，可以一次性设置多个，也可以单独设置一个"""
        if config:
            for key, value in config.items():
                if key not in self._config:
                    self.register(key, value)
                else:
                    self._config[key] = value

        if config_name is not None and config_value is not None:
            if config_name not in self._config:
                self.register(config_name, config_value)
            else:
                self._config[config_name] = config_value
        else:
            raise ValueError("config_name and config_value must be both provided")
        
        self.write_config()

    def verify_config(self):
        """验证配置项是否齐全，不齐全则补齐"""
        change_flag = False
        for key in self.default_config:
            if key not in self._config:
                self._config[key] = self.default_config[key]
                change_flag = True
            elif type(self._config[key]) != type(self.default_config[key]): # 类型不匹配则重置为默认值
                self._config[key] = self.default_config[key]
                change_flag = True

        if change_flag:
            self.write_config()

    def get_config(self, config_name:str|list[str] = None) -> dict | any:
        """获取配置项，可以一次性获取多个，也可以单独获取一个，如果config_name为None则获取全部配置项，不存在则返回None"""
        ret = None
        if type(config_name) == str and config_name in self._config:
            ret = self._config[config_name]
        elif type(config_name) == list:
            ret = {}
            for key in config_name:
                if key in self._config:
                    ret[key] = self._config[key]
        elif config_name is None:
            ret = copy.deepcopy(self._config)

        return ret
    
class ConfigManager(ConfigManage):
    """配置管理界面，自动调用ConfigManage接口，搭配ConfigManage使用"""
    pass