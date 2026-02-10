from typing import Callable
from . import json_encrypt
from . import moretk
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

    def register(self, config_name:str = None, default_value = None, config:dict[str] = None):
        """注册或修改一个默认配置项"""
        if config_name is not None and type(config_name) != str:
            raise TypeError("config_name must be a string")
        
        if config_name is not None and default_value is not None:
            self.default_config[config_name] = default_value
            if config_name not in self._config:
                self._config[config_name] = default_value
        elif (config_name is not None and default_value is None) or (config_name is None and default_value is not None):
            raise ValueError("config_name and default_value must be both provided")

        if config is not None:
            for key, value in config.items():
                if type(key) != str:
                    raise TypeError("the key of config must be a string")
                
                self.default_config[key] = value
                if key not in self._config:
                    self._config[key] = value

        self.write_config()

    def unregister(self, config_name:str = None, config:dict[str] = None):
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
        """设置配置项，可以一次性设置多个，也可以单独设置一个，会自动校验以及写入更改后的配置项"""
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
        elif (config_name is not None and config_value is None) or (config_name is None and config_value is not None):
            raise ValueError("config_name and config_value must be both provided")
        
        if not self.verify_config():
            self.write_config()

    def verify_config(self):
        """验证配置项是否齐全，不齐全则补齐"""
        change_flag = False
        for key in self.default_config:
            if key not in self._config:
                self._config[key] = self.default_config[key]
                change_flag = True
                print(f"配置项 {key} 不存在，已重置为默认值")
            elif type(self._config[key]) != type(self.default_config[key]): # 类型不匹配则重置为默认值
                self._config[key] = self.default_config[key]
                change_flag = True
                print(f"配置项 {key} 类型不匹配，已重置为默认值")

        if change_flag:
            self.write_config()
        
        return change_flag

    def get_config(self, config_name:str|list[str] = None):
        """获取配置项，可以一次性获取多个，返回字典类型，
        也可以单独获取一个，返回对应数据类型，
        如果config_name为None则返回全部配置项，不存在则返回None"""
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
    
class ConfigManager(tk.Toplevel):
    """配置管理界面，自动调用ConfigManage接口，搭配ConfigManage使用"""
    def __init__(self, master, config_manage_instance:ConfigManage, when_config_change_call:Callable = None, when_window_destroy_call:Callable = None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self._master = master
        self._config_manage_instance = config_manage_instance
        self._when_config_change_call = when_config_change_call
        self._when_window_destroy_call = when_window_destroy_call
        self._password_change_window = None  # 用于修改密码的窗口，避免重复打开

        self._if_change = False  # 用于确认是否发生修改

        self._temp_config = self._config_manage_instance.get_config()  # 用于在界面上修改时暂存修改后的配置项，直到点击保存才写入ConfigManage实例
        
        self.title('设置界面')
        self.geometry('600x400')
        self.configure(bg='white')
        self.resizable(False, False)

        self._screenshot_gap_list_real = [0, 5*1000, 30*1000, 60*1000, 5*60*1000, 15*60*1000]
        self._screenshot_gap_list = ['关闭', '5秒', '30秒', '1分钟', '5分钟', '15分钟']
        self._screenshot_gap_textcombobox = moretk.TextComboBox(self, text="截屏间隔", font_l=('微软雅黑', 14),font_c=('微软雅黑', 12), values=self._screenshot_gap_list, bg="white")
        self._screenshot_gap_textcombobox.current(next(i for i, v in enumerate(self._screenshot_gap_list_real) if v == self._temp_config["ss_shotgap"]))
        self._screenshot_gap_textcombobox.pack(pady=10)

        self._screenshot_max_amount_list_real = [5, 50, 100, 1000]
        self._screenshot_max_amount_list = ['5张', '50张', '100张', '1000张']
        self._screenshot_max_amount_textcombobox = moretk.TextComboBox(self, text="最大保存数量", font_l=('微软雅黑', 14), font_c=('微软雅黑', 12), bg="white", values=self._screenshot_max_amount_list)
        self._screenshot_max_amount_textcombobox.current(next(i for i, v in enumerate(self._screenshot_max_amount_list_real) if v == self._temp_config["ss_max_amount"]))
        self._screenshot_max_amount_textcombobox.pack(pady=10)

        self._screenshot_quality_list_real = [1, 2, 4, 8]
        self._screenshot_quality_list = ['1倍质量', '2倍质量', '4倍质量', '8倍质量']
        self._screenshot_quality_textcombobox = moretk.TextComboBox(self, text="图片质量", font_l=('微软雅黑', 14), font_c=('微软雅黑', 12), bg="white", values=self._screenshot_quality_list)
        self._screenshot_quality_textcombobox.current(next(i for i, v in enumerate(self._screenshot_quality_list_real) if v == self._temp_config["ss_quality"]))
        self._screenshot_quality_textcombobox.pack(pady=10)

        self._screenshot_path_inputbox = moretk.PathInputBox(self, text="截屏保存路径", font_a=('微软雅黑', 10), font_r=('微软雅黑', 14), default_path=self._temp_config["ss_path"], bg="white")
        self._screenshot_path_inputbox.pack(pady=10)

        
        self._password_change_button = tk.Button(self, bd=2, height=1, width=10, font=('微软雅黑',10), bg='grey', fg='white', text='修改密码', command=self._on_password_change_button)
        self._password_change_button.pack(pady=10)

        self._quitway_frame = tk.Frame(self, bg="white")
        self._quitway_label = tk.Label(self, text='  当退出时，软件将：',font=('微软雅黑', 14),fg="#000000", bg='white')
        self._quitway_label.pack(pady=5,anchor='center')
        self._quitway_checkbutton_var_1 = tk.BooleanVar()
        self._quitway_checkbutton_var_2 = tk.BooleanVar()
        self._quitway_checkbutton_1 = tk.Checkbutton(self._quitway_frame,font=('微软雅黑', 11),bg='white',text='直接退出',variable=self._quitway_checkbutton_var_1,command=self._on_quitway_checkbutton_1)
        self._quitway_checkbutton_2 = tk.Checkbutton(self._quitway_frame,font=('微软雅黑', 11),bg='white',text='最小化',variable=self._quitway_checkbutton_var_2,command=self._on_quitway_checkbutton_2)
        self._quitway_checkbutton_1.deselect()
        self._quitway_checkbutton_2.deselect()
        if self._config_manage_instance.get_config("if_quit_judge") == 1:
            self._quitway_checkbutton_1.select()
        elif self._config_manage_instance.get_config("if_quit_judge") == 0:
            self._quitway_checkbutton_2.select()
        self._quitway_checkbutton_1.pack(side='left', padx=5)
        self._quitway_checkbutton_2.pack(side='right', padx=5)
        self._quitway_frame.pack(pady=5)

        config_button_frame = tk.Frame(self, bg="white")
        config_save_button = tk.Button(config_button_frame,bd=2,height=1,width=10,font='微软雅黑',bg='grey',fg='white',text='保存',command=self._on_config_save_button)
        config_cancel_button = tk.Button(config_button_frame,bd=2,height=1,width=10,font='微软雅黑',bg='grey',fg='white',text='取消',command=self._on_config_cancel_button)
        config_save_button.pack(side="left", padx=5)
        config_cancel_button.pack(side="right", padx=5)
        config_button_frame.pack(pady=10)

        moretk.ToolTip(self._screenshot_path_inputbox, text=self._temp_config["ss_path"])

        self._screenshot_gap_textcombobox.bind("<Button-1>",lambda event : self._change())  #用于确认是否发生修改
        self._screenshot_max_amount_textcombobox.bind("<Button-1>", lambda event : self._change())
        self._screenshot_quality_textcombobox.bind("<Button-1>", lambda event : self._change())
        self._screenshot_path_inputbox.bind("<AddressChange>", lambda event : self._change())
        self._quitway_checkbutton_1.bind("<Button-1>",lambda event : self._change())
        self._quitway_checkbutton_2.bind("<Button-1>",lambda event : self._change())

        self.protocol("WM_DELETE_WINDOW", self._if_save_window)  # 点击窗口右上角的关闭按钮时调用if_save函数，确认是否保存

    def destroy(self):
        """重写destroy函数，在销毁窗口后调用when_window_destroy_call"""
        super().destroy()
        
        if self._when_window_destroy_call is not None:
            self._when_window_destroy_call()

    def _on_password_change_button(self):
        """点击修改密码按钮的响应函数"""
        if self._password_change_window is None:
            self._password_change_window = moretk.PasswordCangeWindow(self, self._temp_config["password_key"], self._when_password_change)
        else:
            self._password_change_window.lift()

    def _on_quitway_checkbutton_1(self):
        if self._quitway_checkbutton_var_1.get():
            self._quitway_checkbutton_2.deselect()

    def _on_quitway_checkbutton_2(self):
        if self._quitway_checkbutton_var_2.get():
            self._quitway_checkbutton_1.deselect()

    def _when_password_change(self, password):
        """当密码成功修改时调用"""
        self._temp_config['password_key'] = password
        self._change()
        self._password_change_window = None

    def _change(self):  # 用于确认是否发生修改
        self._if_change = True

    def _on_config_save_button(self):
        """点击保存按钮的响应函数"""
        self.save_and_write_config()
        self.destroy()

    def _on_config_cancel_button(self):
        """点击取消按钮的响应函数"""
        self.destroy()

    def update_config(self):
        """将界面上的修改写入temp_config"""
        self._temp_config['ss_path'] = self._screenshot_path_inputbox.path_get()
        self._temp_config['ss_max_amount'] = self._screenshot_max_amount_list_real[self._screenshot_max_amount_textcombobox.current()]
        self._temp_config['ss_quality'] = self._screenshot_quality_list_real[self._screenshot_quality_textcombobox.current()]
        self._temp_config['ss_shotgap'] = self._screenshot_gap_list_real[self._screenshot_gap_textcombobox.current()]
        if self._quitway_checkbutton_var_1.get():
            self._temp_config['if_quit_judge'] = 1
        elif self._quitway_checkbutton_var_2.get():
            self._temp_config['if_quit_judge'] = 0
        else:
            self._temp_config['if_quit_judge'] = -1

    def save_and_write_config(self):
        """保存并写入配置文件"""
        self.update_config()
        self._config_manage_instance.set_config(config=self._temp_config)
        self._config_manage_instance.write_config()

        if self._when_config_change_call is not None:
            self._when_config_change_call()

    def _if_save_window(self):  # 确认保存界面
        if self._if_change:
            if_save_window = tk.Toplevel(self)
            if_save_window.title('是否保存')
            if_save_window.geometry('400x150')
            if_save_window.configure(bg='white')
            if_save_window.resizable(False, False)

            label = tk.Label(if_save_window, text='是否保存', font=('微软雅黑', 20), fg="#000000", bg='white')
            label.pack(side='top', pady=20)

            button_y = tk.Button(if_save_window,bd=2,height=1,width=6,font=('微软雅黑', 13),bg='grey',fg='white',text='保存',command=lambda : (self.update_config(), self._config_manage_instance.write_config(), if_save_window.destroy(), self.destroy()))
            button_n = tk.Button(if_save_window,bd=2,height=1,width=6,font=('微软雅黑', 13),bg='grey',fg='white',text='取消',command=lambda : (if_save_window.destroy(), self.destroy()))
            button_y.pack(side='left', padx=60)
            button_n.pack(side='right', padx=60)
        else:
            self.destroy()