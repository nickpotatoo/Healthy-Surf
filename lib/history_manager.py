import tkinter as tk
from datetime import datetime

from . import moretk
from . import json_encrypt

class HistoryRecorder:
    """进行历史记录与保存以及提供管理接口，单例模式"""
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, master):
        self._master = master
        self._history = {} # 如果值为list则为[int:总时间, int:0点-1点时间, int:1点-2点时间,...]，如果值为str则为总时间
        self._current_history_value_type = list # 当前历史记录的值类型，默认为list，后续会根据读取到的历史记录自动调整为str或list

        self._time_gap = 5000 # 计时间隔，单位ms，默认5000ms

        self._total_time = 0
        self._total_time_format = tk.StringVar()
        self.total_time_format_refresh()
        self._time_date = datetime.now().strftime('%Y%m%d')
        self._old_time_date = self._time_date

        self._history_viewer = None

        self.load_history()

        self._master.after(self._time_gap, self._timer_tick)

    def load_history(self):
        """加载历史记录"""
        self._history.clear()
        self._history = json_encrypt.load_json(file_name="history.json", SECRET_KEY=json_encrypt.SECRET_KEY, default={self._time_date: [0 for i in range(25)]})

        if self._time_date in self._history.keys():
            if type(self._history[self._time_date]) == list:
                self._total_time = self._history[self._time_date][0]
            else:
                self._total_time = int(self._history[self._time_date])
                self._current_history_value_type = str

            self.total_time_format_refresh()
            
        else:
            self._history[self._time_date] = [0 for i in range(25)]

    def write_history(self):
        """写入历史记录"""
        json_encrypt.write_json(save_file_name="history.json", save_file=self._history, SECRET_KEY=json_encrypt.SECRET_KEY)

    def _timer_tick(self, if_circulate:bool = True): # 对总时间进行增加并写入历史记录，if_circulate表示是否循环调用
        """计时器滴答"""
        self._total_time_add()

        self.write_history()

        if if_circulate:
            self._master.after(self._time_gap, self._timer_tick)

    def _total_time_add(self):
        """总时间增加"""
        self.time_date_refresh()
        if self._time_date != self._old_time_date: # 日期改变，重置总时间
            self._old_time_date = self._time_date
            self._total_time_reset()
            self.write_history()

        self._total_time += self._time_gap//1000
        self.total_time_format_refresh()

        if self._current_history_value_type == list:
            if self._time_date not in self._history.keys():
                self._history[self._time_date] = [0 for i in range(25)]
            self._history[self._time_date][0] = self._total_time
            self._history[self._time_date][int(datetime.now().strftime('%H')) + 1] += self._time_gap
        else:
            self._history[self._time_date] = str(self._total_time)

    def _total_time_reset(self):
        """重置总时间"""
        self._total_time = 0
        self.total_time_format_refresh()

        self._history[self._time_date] = [0 for i in range(25)]
        self._current_history_value_type = list

    def total_time_format_refresh(self):
        """刷新总时间的格式"""
        hour = self._total_time // 3600
        min = self._total_time % 3600 // 60
        sec = self._total_time % 60

        self._total_time_format.set('您今日已累计使用电脑%d小时%d分钟%d秒'%(hour, min, sec))

    def time_date_refresh(self):
        """刷新日期"""
        self._old_time_date = self._time_date
        self._time_date = datetime.now().strftime('%Y%m%d')

    def get(self):
        """获取StringVar类型的总时间"""
        return self._total_time_format
    
    def get_history(self):
        """获取历史记录"""
        # return copy.deepcopy(self._history)
        return self._history
    
    def delete_history(self, time_date:str):
        """删除历史记录"""
        if time_date in self._history.keys():
            if time_date == self._time_date:
                self._total_time_reset()
            else:
                del self._history[time_date]
            self.write_history()

class HistoryManager(tk.Toplevel):
    """提供历史记录管理界面，搭配HistoryRecorder使用"""
    def __init__(self, master, config:dict, history_recorder:HistoryRecorder, when_config_change:callable = None, when_history_delete:callable = None):
        super().__init__(master)
        self._master = master
        self._history_recorder = history_recorder
        self._when_config_change = when_config_change
        self._when_history_delete = when_history_delete
        self._history = self._history_recorder.get_history()

        self.config = config
        if "if_ask_delete_history" not in self.config.keys():
            self.config['if_ask_delete_history'] = True

        self.title('使用历史')
        self.geometry('662x400')
        self.configure(bg='white')
        self.resizable(False, False)

        self.lift()
        
        self._scollbar = tk.Scrollbar(self, bd=2, width=30)
        self._scollbar.pack(side = 'right', fill= 'y' )

        self._button_frame = tk.Frame(self)
        
        self._delete_button = tk.Button(self._button_frame, bd=2, height=1, width=10, font='微软雅黑', bg='grey', fg='white', text='删除', command=self._on_delete_button)
        self._delete_button.pack(side='left', padx= 5)

        self._refresh_button = tk.Button(self._button_frame, bd=2, height=1, width=10, font='微软雅黑', bg='grey', fg='white', text='刷新', command=lambda:self.history_listbox_refresh_all(False))
        self._refresh_button.pack(side='right', padx= 5)

        self._button_frame.pack(side='bottom', pady=10)

        self._history_listbox = tk.Listbox(self, yscrollcommand=self._scollbar.set, width= 662, height= 15, font=('微软雅黑', 14))    

        if self.config['if_ask_delete_history']:
            self._ask_window = moretk.CfmWindow(self, text = "确认删除选中的历史记录？", font_b='微软雅黑', font_l='微软雅黑', on_cancel=self._ask_window_on_cancel, on_confirm=self._ask_window_on_confirm, enable_check_button=True, check_button_text="不再提示")
        
        self.history_listbox_refresh_all(True)
        
        self._history_listbox.pack()
        
    def history_listbox_refresh_all(self, if_circulate:bool = False):
        """刷新界面，if_circulate表示是否循环调用"""
        self._history_update()
        self._history_listbox.delete(0,tk.END)
        self._history_insert()
        if if_circulate:
            self.after(60000, lambda: self.history_listbox_refresh_all(True))

    def _history_update(self):
        """刷新历史记录"""
        self._history = self._history_recorder.get_history()

    def _history_insert(self):
        """将历史记录插入界面"""
        for key in self._history:
            if type(self._history[key]) == list:
                time = self._history[key][0]
            else:
                time = int(self._history[key])

            gap_hour = time // 3600
            gap_min = time % 3600 // 60
            gap_sec = time % 60

            v = '%s:%d小时%d分钟%d秒'%(key, gap_hour, gap_min, gap_sec)
            self._history_listbox.insert(tk.END, v)

    def _ask_window_on_confirm(self):
        """确认删除历史记录"""
        self._history_listbox_delete()
        if self._ask_window.get_checkbutton_value():
            self.config['if_ask_delete_history'] = False
            self._when_config_change()
        self._ask_window.withdraw()

    def _ask_window_on_cancel(self):
        """取消删除历史记录"""
        if self._ask_window.get_checkbutton_value():
            self.config['if_ask_delete_history'] = False
            self._when_config_change()
        self._ask_window.withdraw()

    def _on_delete_button(self):
        """删除按钮被点击"""
        if self._history_listbox.curselection():
            if self.config['if_ask_delete_history']:
                self._ask_window.show()
            else:
                self._history_listbox_delete()

    def _history_listbox_delete(self):
        """删除选中的历史记录，调用传入函数并传入所删除的time_date参数并刷新界面"""
        n = self._history_listbox.curselection()
        
        time_date = self._history_listbox.get(n).split(':')[0]

        self._history_listbox.delete(n)

        self._history_recorder.delete_history(time_date)

        if self._when_history_delete:
            self._when_history_delete(time_date)

    def history_update(self, history:dict):
        """更新历史记录"""
        self._history = history
        self.history_listbox_refresh_all()
            
# if __name__ == "__main__":
#     root = tk.Tk()
#     history_recorder = HistoryRecorder(root, config={'if_ask_delete_history': True}, when_config_change=lambda: print("配置已改变"))
#     root.mainloop()