import tkinter as tk
import os
import moretk
from typing import Callable
from PIL import Image, ImageTk 

class PictureViewer(tk.Toplevel):
    """浏览截图界面"""
    def __init__(self, master=None, path=None, config:dict=None, on_config_change_func:Callable=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        if not path or not master or not on_config_change_func or config is None:
            raise ValueError("缺少参数")

        self.picture_list = []
        self.picture_labels = []
        self.chosen_picture = None
        self.config = config
        self.on_config_change_func = on_config_change_func

        self.master = master
        self.path = path
        self.is_shown = False
        self.title("截屏浏览")
        self.geometry("850x600")
        self.resizable(False, False)

        self.frame = tk.Frame(self)
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.frame, bg='white', width=850, height=500)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.image_frame = tk.Frame(self.canvas, bg='white')
        self.image_frame.bind("<Configure>", lambda event : self.canvas.configure(scrollregion=self.canvas.bbox("all"))) #更新滚动区域
        self.canvas.create_window((0, 0), window=self.image_frame, anchor='nw')

        self.withdraw() #初始化时隐藏窗口

        self.scrollbar = tk.Scrollbar(self.frame, orient='vertical', bd=1, width=30, command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky='ns')

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)) #绑定滚轮滚动
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

        self.button_frame = tk.Frame(self)
        self.button_frame.grid(row=1, column=0, pady=10)

        self.delete_button = tk.Button(self.button_frame, text="删除", bg='grey', fg='white', command=self._ask_if_delete, height=2, width=18, font=('微软雅黑', 15)) #删除按钮
        self.delete_button.grid(row=1, column=0, pady=10)

        self.refresh_button = tk.Button(self.button_frame, text="刷新", bg='grey', fg='white', command=self.refresh, height=2, width=18, font=('微软雅黑', 15)) #刷新按钮
        self.refresh_button.grid(row=1, column=1, padx=10, pady=10)

        self.notice = moretk.NoticeWindow(self, _title="错误", text="未选择图片！", btext="确认", font_l=("微软雅黑", 14), font_b=("微软雅黑", 10), command=lambda:self.notice.withdraw())

        if "if_ask_delete_screenshot" not in self.config:
            self.config['if_ask_delete_screenshot'] = True

        if self.config['if_ask_delete_screenshot']:
            self.confirm_window = moretk.CfmWindow(self, _title="删除确认", text="确认删除所选图片？", font_l=("微软雅黑", 13), font_b=("微软雅黑", 10), on_confirm = self._on_cfmwindow_confirm, confirm_button_text="确认", on_cancel= self._on_cfmwindow_cancel, cancel_button_text="取消", enable_check_button=True, check_button_text="不再提示")
    
    def set_config(self):
        """设置配置"""
        self.config['if_ask_delete_screenshot'] = not self.confirm_window.get_checkbutton_value()
        self.on_config_change_func()
    
    def _on_mousewheel(self, event): #鼠标滚轮滚动事件
        self.canvas.yview_scroll(-int(event.delta/120), "units")

    def _on_cfmwindow_confirm(self): #确认删除所选图片
        self._delete_chosen_picture()
        self.set_config()
        self.confirm_window.withdraw()

    def _on_cfmwindow_cancel(self): #取消删除所选图片
        self.set_config()
        self.confirm_window.withdraw()

    def _ask_if_delete(self): #询问是否删除所选图片
        if not self.chosen_picture:
            self.notice.show()
        else:
            if self.config['if_ask_delete_screenshot']:
                self.confirm_window.show()
            else:
                self._delete_chosen_picture()

    def _delete_chosen_picture(self):  #删除所选图片
        if self.chosen_picture:
            try:
                index = self.picture_labels.index(self.chosen_picture)
                image_name = os.listdir(self.path)[index]
                os.remove(self.path + "\\" + image_name)
            except Exception as e:
                notice = moretk.NoticeWindow(self, _title="错误", text="删除图片时出错！\n错误信息："+str(e), btext="确认", font_l=("微软雅黑", 10), font_b=("微软雅黑", 10), command=lambda: notice.destroy())
                notice.show()

            self.chosen_picture = None
            self.refresh()
        else:
            raise RuntimeError("chosen_picture为空，无法删除！")

    def _on_label_click(self, event): #单击图片标签时执行
        if self.chosen_picture and self.chosen_picture != event.widget:
            self.chosen_picture.config(bg='white')
        event.widget.config(bg='lightblue')
        self.chosen_picture = event.widget

    def _on_label_double_click(self, event): #双击图片标签时执行
        print("double clicked")

    def _build_image_frame(self): #构建图片显示区域
        self.picture_labels.clear()

        r=c=0
        for n in self.picture_list:
            label = tk.Label(self.image_frame, image=n, border = 10,bg='white')
            label.grid(row = r, column = c)

            label.bind("<Button-1>", self._on_label_click)
            label.bind("<Double-Button-1>", self._on_label_double_click)
            label.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)) #绑定滚轮滚动
            label.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

            self.picture_labels.append(label)
            c+=1
            if c == 3:
                c = 0
                r += 1

    def show(self): 
        """显示窗口"""
        if self.state() != 'withdrawn':
            self.withdraw() 
            self.deiconify()
        else:
            self.deiconify()
        self.lift()
        self.is_shown = True
        self.chosen_picture = None

        self._load_image()
        self._build_image_frame()

    def refresh(self):
        """刷新窗口内容"""
        if self.state() != 'withdrawn':
            self.lift()

            for n in self.image_frame.winfo_children():
                n.destroy()

            self.chosen_picture = None

            self._load_image()
            self._build_image_frame()
        else:
            raise RuntimeError("窗口未显示，无法刷新！")

    def _load_image(self):
        self.picture_list.clear()
        for n in os.listdir(self.path):
            image = Image.open(self.path+"\\"+n)
            image = image.resize((250, 150))
            photo = ImageTk.PhotoImage(image)
            if n[:5] == 'hssp_':
                self.picture_list.append(photo)

    def withdraw(self):
        """隐藏窗口"""
        super().withdraw()
        self.is_shown = False
        self.chosen_picture = None

        for n in self.image_frame.winfo_children():
            n.destroy()
        
        self.picture_list.clear()
        self.picture_labels.clear()

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("400x300")
    root.title("测试moretk模块")

    pv = PictureViewer(root, path=".\\screenshot", config={}, on_config_change_func=lambda : print("配置已更改"))
    pv.show()

    root.mainloop()