import tkinter as tk
import os
from . import moretk
from typing import Callable
from PIL import Image, ImageTk 

class OpenImage(tk.Toplevel):
    def __init__(self, master=None, path: str = None, init_image_name:str = None,shift_image_call: Callable = None, delete_image_call: Callable = None):
        super().__init__(master)
        self._apply_high_quality = True
        self._quality_timer = None

        self._path = path
        self._image_name = init_image_name
        self.delete_image_call = delete_image_call
        self.shift_image_call = shift_image_call

        self._image_list = []
        self._image_list_update()
        self._image_index = self._image_list.index(init_image_name)
        
        self.scale = 1.0

        self._image = Image.open(self._path+"\\"+self._image_name)

        self.title(self._image_name)
        self.resizable(True, True)
        self.minsize(250,150)
        self.geometry(f"{self._image.width+100}x{self._image.height+50}")

        self._last_width = self.winfo_width()
        self._last_height = self.winfo_height()

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1,weight=0)

        self._canvas = tk.Canvas(self, width=self._image.width, height=self._image.height)
        self._canvas.grid(row=0, column=0, sticky="nsew")

        self._image_item = self._canvas.create_image(0,0,anchor='nw')  #展示图片

        self._scrollbar_y = tk.Scrollbar(self, orient='vertical', command=self._canvas.yview)
        self._scrollbar_y.grid(row=0, column=1, sticky='ns')
        self._scrollbar_x = tk.Scrollbar(self, orient='horizontal', command=self._canvas.xview)
        self._scrollbar_x.grid(row=1, column=0, sticky='ew')
        self._canvas.configure(yscrollcommand=self._scrollbar_y.set, xscrollcommand=self._scrollbar_x.set)

        self._scrollbar_panel = tk.Frame(self, bg='white', width=self._scrollbar_y.winfo_width(), height=self._scrollbar_x.winfo_height())
        self._scrollbar_panel.grid(row=1, column=1, sticky='nsew')
        self._scrollbar_panel.grid_propagate(False)

        self.bind("<Configure>", self._on_resize)
        self.bind("<MouseWheel>", self._on_mousewheel)

        self._canvas.bind("<ButtonPress-1>", lambda event: self._canvas.scan_mark(event.x, event.y))
        self._canvas.bind("<B1-Motion>", lambda event: self._canvas.scan_dragto(event.x, event.y, gain=1))

        self._bottom_panel = tk.Frame(self, bg='white', height=50)  #下方白色镶板
        self._bottom_panel.grid(row=2, column=0, columnspan=2, sticky="ew")
        self._bottom_panel.grid_propagate(False) #防止被子控件撑大

        self._button_frame = tk.Frame(self._bottom_panel, bg='white')
        self._button_frame.place(relx=0.5, rely=0.5, anchor='center')

        self._left_button = tk.Button(self._button_frame, text="←", width=5, bg='grey', fg='white', command=self._view_prev_image)
        self._left_button.pack(side='left', padx=10)

        self._right_button = tk.Button(self._button_frame, text="→", width=5, bg='grey', fg='white', command=self._view_next_image)
        self._right_button.pack(side='left', padx=10)

        self._delete_image_button = tk.Button(self._bottom_panel, text="删除", width=5, bg='grey', fg='white', command=self._delete_image)
        self._delete_image_button.place(relx=0.97, rely=0.5, anchor='e')

        self._refresh_button = tk.Button(self._bottom_panel, text="刷新", width=5, bg='grey', fg='white', command=self._refresh)
        self._refresh_button.place(relx=0.03, rely=0.5, anchor='w')

        self.bind("<Left>", lambda event: self._view_prev_image())
        self.bind("<Right>", lambda event: self._view_next_image())
        self.bind("<Delete>", lambda event: self._delete_image())
        
        self._scale_limit_update()
        self._update_image()

    def _refresh(self):
        self._image_list_update()
        if not self._image_list:
            self.destroy()
            return

        try:
            image_index = self._image_list.index(self._image_name)
            flag = True # 当当前图片还存在时，返回True
        except:
            image_index = min(len(self._image_list)-1, self._image_index)
            flag = False # 当当前图片不存在时，返回False

        if image_index != self._image_index or self._image_list[image_index] != self._image_name:
            self.image_change(image_index)

        return flag

    def _delete_image(self): # 删除图片按钮调用
        if self._refresh():
            delete_path = self._path + "\\" + self._image_name
            delete_index = self._image_index
            delete_name = self._image_name

            try:
                os.remove(delete_path)
            except:
                notice = moretk.NoticeWindow(self, _title = "删除失败", text = "删除失败", font_l = ('微软雅黑', 15), font_b=('微软雅黑', 10), command=lambda:notice.destroy())
                notice.show()
                self._image_list_update()
                self.image_change(0)
            else:
                self._image_list.pop(delete_index)

                if self.delete_image_call:
                    self.delete_image_call(delete_name)

                if self._image_list:
                    next_index = min(delete_index, len(self._image_list) - 1)
                    self.image_change(next_index)
                else:
                    self.destroy()

    def _view_prev_image(self): # 切换至上一张图片
        self._refresh()
        if self._image_list:
            shift_index = max(0, self._image_index-1)
            shift_name = self._image_list[shift_index]
            
            if shift_index != self._image_index:
                self.image_change(shift_index)

            if self.shift_image_call:
                self.shift_image_call(shift_name)

    def _view_next_image(self): # 切换至下一张图片
        self._refresh()
        if self._image_list:
            shift_index = min(len(self._image_list)-1, self._image_index+1)
            shift_name = self._image_list[shift_index]
            
            if shift_index != self._image_index:
                self.image_change(shift_index)

            if self.shift_image_call:
                self.shift_image_call(shift_name)

    def _image_list_update(self): # 更新list
        self._image_list.clear()
        for i in os.listdir(self._path):
            if i[:5] == "hssp_":
                self._image_list.append(i)
                
    def _scale_limit_update(self): # 更新scale的极限
        self.scale_upper_limits = 4000/self._image.width
        self.scale_lower_limits = 100/self._image.width

    def _update_image(self): # 更新并绘制图片
        w = int(self._image.width * self.scale)
        h = int(self._image.height * self.scale)

        if not self._apply_high_quality:
            resized = self._image.resize((w, h), Image.NEAREST)
        else:
            resized = self._image.resize((w, h), Image.LANCZOS)
            
        self.tk_image = ImageTk.PhotoImage(resized)

        self._canvas.itemconfig(self._image_item, image = self.tk_image)
        self._canvas.config(scrollregion=self._canvas.bbox("all"))

    def image_change(self, index): # 切换显示的图片
        try:
            self._image = Image.open(self._path + "\\" + self._image_list[index])
            self._image_index = index
            self.scale = 1
            self._image_name = self._image_list[index]
            self.title(self._image_name)
            self._update_image()
            self._scale_limit_update()
        except Exception as e:
            raise e

    def _quality_shift(self): # 切换图片算法
        self._apply_high_quality = True
        self._quality_timer = None
        self._update_image()

    def _on_mousewheel(self, event):
        x = self._canvas.canvasx(event.x) # 获取缩放前的鼠标在 Canvas 内容中的绝对坐标 (画布坐标)
        y = self._canvas.canvasy(event.y)

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

        scroll_x = (new_x - event.x) / self._canvas.bbox("all")[2] # 让 new_x 减去鼠标在窗口中的偏移量 event.x，得到画布新的左上角位置,然后换算成 0.0 到 1.0 的百分比传给 moveto
        scroll_y = (new_y - event.y) / self._canvas.bbox("all")[3]

        self._canvas.xview_moveto(scroll_x)
        self._canvas.yview_moveto(scroll_y)

        if not self._apply_high_quality: # 使进行滚动缩放时采用低质量图片算法，静止200ms后恢复为高质量算法
            if self._quality_timer:
                self.after_cancel(self._quality_timer)
            self._quality_timer = self.after(200, self._quality_shift)

    def _on_resize(self, event): # 当窗口大小改变时调用
        if event.widget is not self:
            return
        
        if self._last_width == self.winfo_width() and self._last_height == self.winfo_height():
            return

        self._apply_high_quality = False

        self._last_width = self.winfo_width()
        self._last_height = self.winfo_height()

        scale_w = (event.width-self._scrollbar_y.winfo_width()) / self._image.width
        scale_h = (event.height-50-self._scrollbar_x.winfo_height()) / self._image.height
        self.scale = min(scale_w, scale_h)

        self.scale = max(self.scale_lower_limits, self.scale)
        self._update_image()

        if not self._apply_high_quality: # 使进行拉伸界面缩放时采用低质量图片算法，静止200ms后恢复为高质量算法
            if self._quality_timer:
                self.after_cancel(self._quality_timer)
            self._quality_timer = self.after(200, self._quality_shift)

    def get_image_name(self):
        return self._image_name

class ScreenshotViewer(tk.Toplevel):
    """浏览截图界面"""
    def __init__(self, master=None, path=None, config:dict=None, on_config_change_func:Callable=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        if not path or not master or not on_config_change_func or config is None:
            raise ValueError("缺少参数")

        self._picture_name_list = []
        self._picture_list = []
        self._picture_labels = []
        self._chosen_picture = None
        self._chosen_picture_list = []
        self.config = config
        self.on_config_change_func = on_config_change_func

        self._viewer_list = []

        self._batch_delete_mode = False

        self.master = master
        self._path = path
        self._is_shown = False
        self.title("截屏浏览")
        self.geometry("850x600")
        self.resizable(False, False)

        self._frame = tk.Frame(self)
        self._frame.grid(row=0, column=0, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._frame.grid_rowconfigure(0, weight=1)
        self._frame.grid_columnconfigure(0, weight=1)

        self._canvas = tk.Canvas(self._frame, bg='white')
        self._canvas.grid(row=0, column=0, sticky="nsew")

        self._image_frame = tk.Frame(self._canvas, bg='white')
        self._image_frame.bind("<Configure>", lambda event : self._canvas.configure(scrollregion=self._canvas.bbox("all"))) #更新滚动区域
        self._canvas.create_window((0, 0), window=self._image_frame, anchor='nw')

        self._scrollbar = tk.Scrollbar(self._frame, orient='vertical', bd=1, width=30, command=self._canvas.yview)
        self._scrollbar.grid(row=0, column=1, sticky='ns')

        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._canvas.bind("<Enter>", lambda e: self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)) #绑定滚轮滚动
        self._canvas.bind("<Leave>", lambda e: self._canvas.unbind_all("<MouseWheel>"))

        self._button_frame = tk.Frame(self)
        self._button_frame.grid(row=1, column=0, pady=10)

        self._delete_button = tk.Button(self._button_frame, text="删除", bg='grey', fg='white', command=self._ask_if_delete, height=1, width=16, font=('微软雅黑', 15)) #删除按钮
        self._delete_button.grid(row=1, column=1, pady=10)

        self._refresh_button = tk.Button(self._button_frame, text="刷新", bg='grey', fg='white', command=self.refresh, height=1, width=16, font=('微软雅黑', 15)) #刷新按钮
        self._refresh_button.grid(row=1, column=0, padx=10, pady=10)

        self._batch_delete_button = tk.Button(self._button_frame, text="批量删除", bg='grey', fg='white', command=self._on_batch_delete_button, height=1, width=16, font=('微软雅黑', 15)) #批量删除按钮
        self._batch_delete_button.grid(row=1, column=2, padx=10, pady=10)

        self._batch_delete_cancel_button = tk.Button(self._button_frame, text="取消", bg='grey', fg='white', command=self._on_batch_delete_cancel_button, height=1, width=16, font=('微软雅黑', 15)) #取消删除按钮

        self._none_picture_chosen_notice = moretk.NoticeWindow(self, _title="错误", text="未选择图片！", btext="确认", font_l=("微软雅黑", 14), font_b=("微软雅黑", 10), command=lambda:self._none_picture_chosen_notice.withdraw())

        if "if_ask_delete_screenshot" not in self.config:
            self.config['if_ask_delete_screenshot'] = True

        if self.config['if_ask_delete_screenshot']:
            self.confirm_window = moretk.CfmWindow(self, _title="删除确认", text="确认删除所选图片？", font_l=("微软雅黑", 13), font_b=("微软雅黑", 10), on_confirm = self._on_cfmwindow_confirm, confirm_button_text="确认", on_cancel= self._on_cfmwindow_cancel, cancel_button_text="取消", enable_check_button=True, check_button_text="不再提示")

        self._load_image()
        self._build_image_frame()
    def set_config(self):
        """设置配置"""
        self.config['if_ask_delete_screenshot'] = not self.confirm_window.get_checkbutton_value()
        self.on_config_change_func()
    
    def _on_mousewheel(self, event): #鼠标滚轮滚动事件
        self._canvas.yview_scroll(-int(event.delta/120), "units")

    def _on_cfmwindow_confirm(self): #确认删除所选图片
        self._delete_chosen_picture()
        self.set_config()
        self.confirm_window.withdraw()

    def _on_cfmwindow_cancel(self): #取消删除所选图片
        self.set_config()
        self.confirm_window.withdraw()

    def _on_batch_delete_button(self): #点击批量删除按钮
        self._batch_delete_mode = True
        self.refresh()
        self._chosen_picture_list.clear()
        self._batch_delete_button.grid_forget()
        self._batch_delete_cancel_button.grid(row=1, column=2, padx=10, pady=10)

    def _on_batch_delete_cancel_button(self): #点击取消批量删除按钮
        self._batch_delete_mode = False
        self.refresh()
        self._chosen_picture_list.clear()
        self._batch_delete_cancel_button.grid_forget()
        self._batch_delete_button.grid(row=1, column=2, padx=10, pady=10)

    def _ask_if_delete(self): #询问是否删除所选图片
        if (not self._batch_delete_mode and not self._chosen_picture) or (self._batch_delete_mode and not self._chosen_picture_list):
            self._none_picture_chosen_notice.show()
        else:
            if self.config['if_ask_delete_screenshot']:
                self.confirm_window.show()
            else:
                self._delete_chosen_picture()

    def _delete_chosen_picture(self):  #删除所选图片
        if not self._batch_delete_mode:
            if self._chosen_picture:
                try:
                    index = self._picture_labels.index(self._chosen_picture)
                    image_name = self._picture_name_list[index]
                    os.remove(self._path + "\\" + image_name)
                except Exception as e:
                    notice = moretk.NoticeWindow(self, _title="错误", text="删除"+image_name+"时出错！\n错误信息："+str(e), btext="确认", font_l=("微软雅黑", 10), font_b=("微软雅黑", 10), command=lambda: notice.destroy())
                    notice.show()
                    self._chosen_picture = None
                    self.refresh()
                else:
                    self._chosen_picture = None
                    self.refresh()
                    self._viewer_list_refresh()
                    if not self._picture_list:
                        for i in self._viewer_list:
                            i.destroy()
                    else:
                        for i in self._viewer_list:
                            if i.get_image_name() == image_name:
                                i._refresh()

            else:
                raise RuntimeError("chosen_picture为空，无法删除！")
        else:
            if self._chosen_picture_list:
                for i in self._chosen_picture_list:
                    if os.path.exists(self._path + "\\" + i):
                        try:
                            os.remove(self._path + "\\" + i)
                        except Exception as e:
                            notice = moretk.NoticeWindow(self, _title="错误", text="删除"+i+"时出错！\n错误信息："+str(e), btext="确认", font_l=("微软雅黑", 10), font_b=("微软雅黑", 10), command=lambda: notice.destroy())
                            notice.show()
                self._viewer_list_refresh()
                if not self._picture_list:
                    for i in self._viewer_list:
                        i.destroy()
                else:
                    for i in self._viewer_list:
                        if i.get_image_name() in self._chosen_picture_list:
                            i._refresh()
                self.refresh()
                self._chosen_picture_list.clear()

    def _on_label_click(self, event): #单击图片标签时执行
        if not self._batch_delete_mode:
            if self._chosen_picture and self._chosen_picture != event.widget:
                self._chosen_picture.config(bg='white')
            event.widget.config(bg='lightblue')
            self._chosen_picture = event.widget
        else:
            if event.widget.cget("bg") == 'white':
                event.widget.config(bg='lightblue')
                self._chosen_picture_list.append(self._picture_name_list[self._picture_labels.index(event.widget)])
            else:
                event.widget.config(bg='white')
                self._chosen_picture_list.remove(self._picture_name_list[self._picture_labels.index(event.widget)])

    def _on_label_double_click(self, event): #双击图片标签时执行
        if not self._batch_delete_mode:
            image_name = self._picture_name_list[self._picture_labels.index(self._chosen_picture)]

            self._viewer_list_refresh()

            for i in self._viewer_list:
                if i.image_name == image_name:
                    i.lift()
                    return

            viewer = OpenImage(self, self._path, image_name, delete_image_call=lambda d_n:(self.refresh(), self.viewer.lift()))

            self._viewer_list.append(viewer)
        
    def _viewer_list_refresh(self):
        for i in self._viewer_list:
            if i not in self.winfo_children():
                self._viewer_list.remove(i)

    def _build_image_frame(self): #构建图片显示区域
        self._picture_labels.clear()

        r=c=0
        for n in self._picture_list:
            label = tk.Label(self._image_frame, image=n, border = 10,bg='white')
            label.grid(row = r, column = c)

            label.bind("<Button-1>", self._on_label_click)
            label.bind("<Double-Button-1>", self._on_label_double_click)
            label.bind("<Enter>", lambda e: self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)) #绑定滚轮滚动
            label.bind("<Leave>", lambda e: self._canvas.unbind_all("<MouseWheel>"))

            self._picture_labels.append(label)
            c+=1
            if c == 3:
                c = 0
                r += 1

    def refresh(self):
        """刷新窗口内容"""
        for n in self._image_frame.winfo_children():
            n.destroy()

        self._chosen_picture = None
        self._chosen_picture_list.clear()

        self._load_image()
        self._build_image_frame()

    def _load_image(self):
        self._picture_list.clear()
        self._picture_name_list.clear()
        for n in os.listdir(self._path):
            image = Image.open(self._path+"\\"+n)
            image = image.resize((250, 150))
            photo = ImageTk.PhotoImage(image)
            if n[:5] == 'hssp_':
                self._picture_list.append(photo)
            self._picture_name_list.append(n)

# if __name__ == '__main__':
#     root = tk.Tk()
#     root.geometry("400x300")
#     root.title("测试moretk模块")

#     pv = PictureViewer(root, path=".\\screenshot", config={}, on_config_change_func=lambda : print("配置已更改"))
#     pv.show()

#     root.mainloop()