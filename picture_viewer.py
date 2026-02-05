import tkinter as tk
import os
import moretk
from typing import Callable
from PIL import Image, ImageTk 

class ImageTkViewing(tk.Toplevel):
    def __init__(self, master=None, path: str = None, image_path_list: list = None, before_shift_image: Callable = None):
        super().__init__(master)
        self._apply_high_quality = True
        self.quality_timer = None

        self.path = path
        self.image = Image.open(self.path)

        self.before_shift_image = before_shift_image
        if image_path_list:
            self.image_path_list = image_path_list
            try:
                self.image_index = self.image_path_list.index(self.path)
            except:
                raise ValueError("image_path_list中无法找到当前图片的路径")
        
        self.scale = 1.0

        tempt_list = self.path.split('\\')
        list_len = len(tempt_list)
        self.name = tempt_list[list_len-1]

        self.title(self.name)
        self.resizable(True, True)
        self.geometry(f"{self.image.width}x{self.image.height+50}")

        self.last_width = self.winfo_width()
        self.last_height = self.winfo_height()

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1,weight=0)

        self.canvas = tk.Canvas(self, width=self.image.width, height=self.image.height)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.image_item = self.canvas.create_image(0,0,anchor='nw')  #展示图片

        self.scrollbar_y = tk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.scrollbar_y.grid(row=0, column=1, sticky='ns')
        self.scrollbar_x = tk.Scrollbar(self, orient='horizontal', command=self.canvas.xview)
        self.scrollbar_x.grid(row=1, column=0, sticky='ew')
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)

        self.scrollbar_panel = tk.Frame(self, bg='white', width=self.scrollbar_y.winfo_width(), height=self.scrollbar_x.winfo_height())
        self.scrollbar_panel.grid(row=1, column=1, sticky='nsew')
        self.scrollbar_panel.grid_propagate(False)

        self.bind("<Configure>", self._on_resize)
        self.bind("<MouseWheel>", self._on_mousewheel)

        self.canvas.bind("<ButtonPress-1>", lambda event: self.canvas.scan_mark(event.x, event.y))
        self.canvas.bind("<B1-Motion>", lambda event: self.canvas.scan_dragto(event.x, event.y, gain=1))

        self.bottom_panel = tk.Frame(self, bg='white', height=50)  #下方白色镶板
        self.bottom_panel.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.bottom_panel.grid_propagate(False) #防止被子控件撑大

        self.button_frame = tk.Frame(self.bottom_panel, bg='white')
        self.button_frame.place(relx=0.5, rely=0.5, anchor='center')

        self.left_button = tk.Button(self.button_frame, text="←", width=5, bg='grey', fg='white', command=self._view_prev_image)
        self.left_button.pack(side='left', padx=10)

        self.right_button = tk.Button(self.button_frame, text="→", width=5, bg='grey', fg='white', command=self._view_next_image)
        self.right_button.pack(side='left', padx=10)

        self.bind("<Left>", lambda event: self._view_prev_image())
        self.bind("<Right>", lambda event: self._view_next_image())
        
        self._scale_limit_decide()
        self._update_image()

    def _view_prev_image(self):
        if self.before_shift_image:
            self.before_shift_image()

        if self.image_path_list:
            try:
                self.image_index = self.image_path_list.index(self.path)
            except:
                raise ValueError("image_path_list中无法找到当前图片的路径")
            
            if self.image_index > 0:
                self.image_change(self.image_path_list[self.image_index-1])

    def _view_next_image(self):
        if self.before_shift_image:
            self.before_shift_image()

        if self.image_path_list:
            try:
                self.image_index = self.image_path_list.index(self.path)
            except:
                raise ValueError("image_path_list中无法找到当前图片的路径")
            
            if self.image_index < len(self.image_path_list) - 1:
                self.image_change(self.image_path_list[self.image_index+1])
                

    def _scale_limit_decide(self):
        self.scale_upper_limits = 4000/self.image.width
        self.scale_lower_limits = 100/self.image.width

    def _update_image(self): #更新并绘制图片
        w = int(self.image.width * self.scale)
        h = int(self.image.height * self.scale)

        if not self._apply_high_quality:
            resized = self.image.resize((w, h), Image.NEAREST)
        else:
            resized = self.image.resize((w, h), Image.LANCZOS)
            
        self.tk_image = ImageTk.PhotoImage(resized)

        self.canvas.itemconfig(self.image_item, image = self.tk_image)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def _quality_shift(self): # 切换图片算法
        self._apply_high_quality = True
        self.quality_timer = None
        self._update_image()

    def _on_mousewheel(self, event):
        x = self.canvas.canvasx(event.x) # 获取缩放前的鼠标在 Canvas 内容中的绝对坐标 (画布坐标)
        y = self.canvas.canvasy(event.y)

        old_scale = self.scale
        if event.delta > 0:
            self.scale *= 1.1
        elif event.delta < 0:
            self.scale *= 0.9

        self.scale = max(self.scale_lower_limits, min(self.scale, self.scale_upper_limits))
        
        if old_scale == self.scale:
            return
        
        self._apply_high_quality = False

        self._update_image()

        new_x = x * (self.scale / old_scale)  # 计算鼠标在缩放后的新坐标（比例缩放）
        new_y = y * (self.scale / old_scale)

        scroll_x = (new_x - event.x) / self.canvas.bbox("all")[2] # 让 new_x 减去鼠标在窗口中的偏移量 event.x，得到画布新的左上角位置,然后换算成 0.0 到 1.0 的百分比传给 moveto
        scroll_y = (new_y - event.y) / self.canvas.bbox("all")[3]

        self.canvas.xview_moveto(scroll_x)
        self.canvas.yview_moveto(scroll_y)

        if not self._apply_high_quality: # 使进行滚动缩放时采用低质量图片算法，静止200ms后恢复为高质量算法
            if self.quality_timer:
                self.after_cancel(self.quality_timer)
            self.quality_timer = self.after(200, self._quality_shift)

    def _on_resize(self, event):
        if event.widget is not self:
            return
        
        if self.last_width == self.winfo_width() and self.last_height == self.winfo_height():
            return

        self._apply_high_quality = False

        self.last_width = self.winfo_width()
        self.last_height = self.winfo_height()

        scale_w = (event.width-self.scrollbar_y.winfo_width()) / self.image.width
        scale_h = (event.height-50-self.scrollbar_x.winfo_height()) / self.image.height
        self.scale = min(scale_w, scale_h)

        self.scale = max(self.scale_lower_limits, self.scale)
        self._update_image()

        if not self._apply_high_quality: # 使进行拉伸界面缩放时采用低质量图片算法，静止200ms后恢复为高质量算法
            if self.quality_timer:
                self.after_cancel(self.quality_timer)
            self.quality_timer = self.after(200, self._quality_shift)

    def image_change(self, path:str):
        try:
            self.image = Image.open(path)
            self.path = path
            self.image_index = self.image_path_list.index(self.path)
            self.scale = 1
            self.name = self.path.split('\\')[len(self.path.split('\\'))-1]
            self.title(self.name)
            self._update_image()
        except:
            raise ValueError("无效的图片路径或图片打开失败")

class PictureViewer(tk.Toplevel):
    """浏览截图界面"""
    def __init__(self, master=None, path=None, config:dict=None, on_config_change_func:Callable=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        if not path or not master or not on_config_change_func or config is None:
            raise ValueError("缺少参数")

        self.picture_name_list = []
        self.picture_list = []
        self.picture_labels = []
        self.chosen_picture = None
        self.config = config
        self.on_config_change_func = on_config_change_func

        self.viewer_list = []

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
        image_index = self.picture_labels.index(event.widget)
        image_name = self.picture_name_list[image_index]


        self.picture_path_list = [self.path + '\\' + i for i in self.picture_name_list]
        viewer = ImageTkViewing(self, path=self.path + "\\" + image_name, image_path_list=self.picture_path_list)
        self.viewer_list.append(viewer)

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
        self.picture_name_list.clear()
        for n in os.listdir(self.path):
            image = Image.open(self.path+"\\"+n)
            image = image.resize((250, 150))
            photo = ImageTk.PhotoImage(image)
            if n[:5] == 'hssp_':
                self.picture_list.append(photo)
            self.picture_name_list.append(n)

    def withdraw(self):
        """隐藏窗口"""
        super().withdraw()
        self.is_shown = False
        self.chosen_picture = None

        for n in self.image_frame.winfo_children():
            n.destroy()
        
        self.picture_name_list.clear()
        self.picture_list.clear()
        self.picture_labels.clear()

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("400x300")
    root.title("测试moretk模块")

    pv = PictureViewer(root, path=".\\screenshot", config={}, on_config_change_func=lambda : print("配置已更改"))
    pv.show()

    root.mainloop()