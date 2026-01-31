import tkinter as tk
from tkinter import font as tkfont
from tkinter import filedialog
from tkinter import ttk
from typing import Literal
import os
from PIL import Image, ImageTk 

class ToolTip:  #提示框
    def __init__(self, widget, font="TkDefaultFont", textvariable:tk.StringVar=None, text='',judge=True, wraplength=500):
        self.if_tv = False
        self.widget = widget
        self.font = font
        self.text = text
        self.judge = judge
        self.tip_window = None
        self.widget.bind("<Enter>", self.enter_tip)
        self.widget.bind("<Leave>", self.hide_tip)
        self.textvariable = textvariable
        self.wraplength = wraplength

        if text and textvariable:  #若两种文本同时输入，报错且以text输入值为准
            textvariable = None
            raise ValueError('冲突！输入了多种文本！')
        elif textvariable:  #若textvariable类型错误，则使用text的默认值，即''
            if not isinstance(self.textvariable, tk.StringVar):
                raise TypeError("textvariable 必须是 tk.StringVar 类型")
            self.if_tv = True
            
    
    def show_tip(self):
        while self.if_enter:
            if not self.judge or self.tip_window or (not self.text and not self.textvariable):
                return
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 1
            self.tip_window = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)  # 去掉窗口边框
            tw.wm_geometry(f"+{x}+{y}")
            if self.if_tv:
                label = tk.Label(tw, textvariable=self.textvariable, justify='left', background="#ffffff", relief='solid', borderwidth=1, font=self.font, wraplength=self.wraplength)
            else:
                label = tk.Label(tw, text=self.text, justify='left', background="#ffffff", relief='solid', borderwidth=1, font=self.font, wraplength=self.wraplength)
            label.pack(ipadx=5, ipady=2)

    def enter_tip(self, event):
        self.if_enter = True
        self.show_tip()

    def hide_tip(self, event):
        self.if_enter = False
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class PathInputBox(tk.Frame):  #地址输入框
    def __init__(self, master=None, text='Saving Path', font_r="TkDefaultFont", font_a="TkDefaultFont", default_path='', button_size=1, width_a=50, bg='white', if_omit=True, *args, **kwargs):
        super().__init__(master, bg=bg, *args, **kwargs)

        self.text = text
        self.master = master
        self.font_r = font_r
        self.font_a = font_a
        self.button_size = button_size
        self.default_path = default_path
        self.width_a = width_a
        self.bg = bg
        self.if_omit = if_omit
        self.__PathChange_bind = None

        self.path = self.default_path
        self.path_v = tk.StringVar()
        self.path_v.set(self.path)
        self.path_show = tk.StringVar()

        self.label_r = tk.Label(self, text=self.text, font=self.font_r, bg=self.bg)
        self.label_r.pack(side='left')

        self.label_a = tk.Label(self, textvariable=self.path_show, font=self.font_a, fg="#000000", bg=self.bg, relief='solid', borderwidth=0.5, width=self.width_a, anchor='w')
        self.label_a.pack(side='left')

        self.label_a.bind("<Configure>", lambda event : self.__path_set(path_get=None))  

        self.button = tk.Button(self,bd=1,height=1,width=2,font=('微软雅黑', 7*self.button_size),bg='grey',fg='white',text='▼',command=self.__bto_pathca_deal)
        self.button.pack(side='right')

    @staticmethod
    def font_width_deal(path_f, label):  #用于计算地址长度是否过长，若过长，则返回截短后加上省略号的地址，其中label需要为要处理的tkinter.label实例
        try:
            width = label.winfo_width()
            font = tkfont.Font(font=label.cget("font"))
            path_c = path_f
            if font.measure(path_c) <= width:
                return path_f
            else:
                path_f = ''
                for v in path_c:
                    if font.measure(path_f + v + '...') > width - 10:
                        break
                    path_f += v
                path_f += '...'
                return path_f 
        except:
            print('sth wrong')   

    def bind(self, action:str=..., func=None):  #重写bind方法
        if action == "<Enter>":
            self.label_a.bind("<Enter>", func)
        elif action == "<Leave>":
            self.label_a.bind("<Leave>", func)
        elif action == "<PathChange>":
            self.__PathChange_bind = func

    def winfo_rootx(self):   #重写winfo_rootx方法，返回label_a的x坐标
        return self.label_a.winfo_rootx()
    
    def path_get(self):  #获取地址（仅当下）
        return self.path
    
    def path_var_get(self):  #获取为tk.Stringvar()实例的地址
        return self.path_v
    
    def set(self, text=""):
        self.path = text
        self.path_v.set(text)
        if self.if_omit:
            self.path_show.set(self.font_width_deal(text, self.label_a))
        else:
            self.path_show.set(text)

    def __bto_pathca_deal(self):  #仅用于获取地址界面
        if self.__PathChange_bind:
            self.__PathChange_bind("this is event awa")
        path_get =  None
        save_path = filedialog.askdirectory()
        if save_path:
            path_get = save_path
            self.__path_set(path_get=path_get)
        else:
            pass 

    def __path_set(self, path_get):  #用于为各个地址属性赋值最终self.path与self.path_v即为地址，path_get=None时用于初始化
        if not path_get:
            if self.if_omit:
                self.path_show.set(self.font_width_deal(self.path, self.label_a))
            else:
                self.path_show.set(self.path)
        else:
            self.path_v.set(path_get)
            self.path = path_get
            if self.if_omit:
                self.path_show.set(self.font_width_deal(path_get, self.label_a))
            else:
                self.path_show.set(path_get)
                
class TextComboBox(tk.Frame):   #带有文字的combobox
    def __init__(self, master=None, text='', values=[], default_index=0, width=10, font_l="TkDefaultFont", font_c="TkDefaultFont", bg="white", *args, **kwargs):
        super().__init__(master, bg=bg, *args, **kwargs)

        self.master = master
        self.text = text
        self.values = values
        self.default_index = default_index
        self.font_l = font_l
        self.font_c = font_c
        self.width = width
        self.bg = bg

        self.label = tk.Label(self, text=self.text, font=self.font_l, bg=self.bg)
        self.label.pack(side='left')

        self.combobox = ttk.Combobox(self, values=self.values, font=self.font_c, width=self.width)
        self.combobox.pack(side='right')
        if self.values:    #如果有给值的话，默认为default_index
            self.combobox.current(self.default_index)

    def current(self, newindex=0):   #写一个current方法，使得可以从combobox丝滑过渡到我写的这个类
        if newindex:
            self.combobox.current(newindex=newindex)
        return self.combobox.current()
    
    def bind(self, *args, **kwargs):  #同上
        self.combobox.bind(*args, **kwargs)

class TimeSpin(tk.Frame):
    def __init__(self, master, values, amount=1, width=80, text='', font_l="TkDefaultFont", font_b="TkDefaultFont", bg='white', text_side:Literal['right', 'left', 'top', 'bottom']='right', default_index:int=None, *args, **kwargs):
        super().__init__(master, bg=bg, *args, **kwargs)

        self.values = values
        self.width = width 
        self.item_height = 30  # 每一项的高度
        self.height = amount * self.item_height
        self.offset = 0        # 偏移量（用于滚动）
        self.offset_org = 0
        self.total_height = self.item_height * len(self.values)
        self.mid = self.height // 2
        self.text = text
        self.font_l = font_l
        self.font_b = font_b
        self.mouse_y_org = 0
        self.bg = bg
        self.text_side = text_side
        self.default_index = default_index

        if amount > len(self.values):
            raise ValueError("The amount is too large.")

        self.canvas = tk.Canvas(self, width=self.width, bg=self.bg, height=self.height)
        
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)# 绑定滚轮
        self.canvas.bind("<B1-Motion>", self.on_mousedrag)# 绑定鼠标拖拽
        self.canvas.bind("<Button-1>", self.on_mouse1click)# 绑定鼠标点击
        self.draw()# 绘制内容

        self.canvas.create_line(0, self.mid, width, self.height//2, fill="red", dash=(2, 2))# 中心线（选中区域）

        self.label = tk.Label(self, bg=self.bg, text=self.text, font=self.font_l)
        if self.text_side == 'bottom':
            self.canvas.pack(side='top')
        elif self.text_side == 'top':
            self.canvas.pack(side='bottom')
        elif self.text_side == 'left':
            self.canvas.pack(side='right')
        else:
            self.canvas.pack(side='left')
        self.label.pack(side=self.text_side)

        if self.default_index:
            self.current(self.default_index)

    def draw(self):
        """绘制滚轮上的值"""
        if self.offset >= self.total_height:
            self.offset -= self.total_height
        elif self.offset <= -self.total_height:  #又对self.offset处理，使其不过大并循环滚动
            self.offset += self.total_height
        self.canvas.delete("text")
        if_red = False  #用于防止两个数字被同时标红
        for i, v in enumerate(self.values):
            y = i * self.item_height + self.offset
            color = "black"
            if abs(y - self.mid) <= self.item_height//2 and not if_red:
                color = "red"  # 选中的项标红
                self.idx = i
                if_red = True
            self.canvas.create_text(self.width//2, y, text=v, tags="text", fill=color, font=self.font_b)
            if i == len(self.values) - 1:
                if y <= self.height - self.item_height:   #多画一点，防止穿帮
                    n = len(self.values)
                    for t in range(0,n):
                        color = "black"
                        y += self.item_height
                        v = self.values[t]
                        if abs(y - self.mid) <= self.item_height//2 and not if_red:
                            color = "red"
                            self.idx = t
                            if_red = True
                        self.canvas.create_text(self.width//2, y, text=v, tags="text", fill=color, font=self.font_b)
            if i == 0:
                if -self.item_height <= y:
                    n = len(self.values)
                    for t in range(0,n):    #多画一点，防止穿帮
                        color = "black"
                        y -= self.item_height
                        v = self.values[len(self.values)-1-t]
                        if abs(y - self.mid) <= self.item_height//2 and not if_red:
                            color = "red"
                            self.idx = len(self.values)-1-t
                            if_red = True
                        self.canvas.create_text(self.width//2, y, text=v, tags="text", fill=color, font=self.font_b)
                    

    def on_mousewheel(self, event):
        """滚动"""
        self.offset += (event.delta // 120) * self.item_height  # 鼠标滚轮调节

        self.draw()

    def on_mousedrag(self, event):
        def move_value_deal(move_value):  #递归函数，防止move_value过大
            if move_value >= self.total_height:
                move_value -= self.total_height
                return move_value_deal(move_value)
            elif move_value <= -self.total_height:
                move_value += self.total_height
                return move_value_deal(move_value)
            else:
                return move_value

        move_value = ((event.y - self.mouse_y_org) // 30)*30
        move_value = move_value_deal(move_value)
        
        self.offset = self.offset_org + move_value

        self.draw()

    def on_mouse1click(self, event):
        self.mouse_y_org = event.y
        self.offset_org = self.offset
        return self.mouse_y_org

    def get_selected(self):
        """返回当前选中的值"""
        return self.values[self.idx]
    
    def current(self, index:int=None):
        """改变当下绘制元素"""
        if index != None:
            self.offset += (self.idx - index) * self.item_height
            self.draw()
        return self.idx
    
class CfmWindow(tk.Toplevel):
    """确认界面"""
    def __init__(self, master=None, text:str="", textvariable:tk.StringVar=None, font_l="TkDefaultFont", font_b="TkDefaultFont", _title="确认窗口", on_confirm=None, confirm_button_text = "确认", on_cancel=None, cancel_button_text = "取消", enable_check_button = False, check_button_text = "default", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self._title = _title
        self.text = text
        self.textvariable = textvariable
        self.font_l = font_l
        self.font_b = font_b
        self.on_confirm = on_confirm  # 外部传入的函数（确认）
        self.confirm_button_text = confirm_button_text
        self.on_cancel = on_cancel    # 外部传入的函数（取消）
        self.cancel_button_text = cancel_button_text
        self.if_cfm = False
        self.enable_check_button = enable_check_button
        if self.enable_check_button:  #是否需要复选框
            self.check_button_flag = tk.BooleanVar()
            self.check_button_flag.set(False)
            self.check_button_text = check_button_text
            self.check_button = tk.Checkbutton(self, text=check_button_text, font=("微软雅黑", 10), variable=self.check_button_flag)

        if text and textvariable:  #若两种文本同时输入，报错且以text输入值为准
            textvariable = None
            raise ValueError('冲突！输入了多种文本！')
        elif textvariable:  #若textvariable类型错误，则使用text的默认值，即''
            if not isinstance(self.textvariable, tk.StringVar):
                raise TypeError("textvariable 必须是 tk.StringVar 类型")

        self.title(self._title)
        if self.enable_check_button:
            self.geometry('300x140')
        else:
            self.geometry('300x100')
        self.resizable(False, False)
        self.withdraw()

        self.protocol('WM_DELETE_WINDOW', self.withdraw)

        if self.textvariable:
            self.label = tk.Label(self, font=self.font_l, textvariable=self.textvariable)
        else:
            self.label = tk.Label(self, font=self.font_l, text=self.text)
        self.label.pack(pady=10)

        if self.enable_check_button:
            self.check_button.pack(pady=5)

        self.btn_frame = tk.Frame(self)
        self.btn_frame.pack(pady=5)

        self.btn_ok = tk.Button(self.btn_frame, text=self.confirm_button_text, width=10, command=self._do_confirm, bg='grey', fg='white', bd=2, font=self.font_b)
        self.btn_ok.pack(side="left", padx=10)

        self.btn_cancel = tk.Button(self.btn_frame, text=self.cancel_button_text, width=10, command=self._do_cancel, bg='grey', fg='white', bd=2, font=self.font_b)
        self.btn_cancel.pack(side="left", padx=10)

    def _do_confirm(self):  #确认时执行的任务
        """点击确认执行"""
        self.if_cfm = True
        if callable(self.on_confirm):
            self.on_confirm()        
        return True

    def _do_cancel(self):  #取消时执行的任务
        """点击取消执行"""
        self.if_cfm = False
        if callable(self.on_cancel):
            self.on_cancel()
        return False

    def show(self):
        """显示确认界面"""
        if self.state() != 'withdrawn':
            self.withdraw()
            self.deiconify()
        else:
            self.deiconify()
        self.lift()

    def get_checkbutton_value(self):
        """获取复选框的值，若没有复选框则报错"""
        if self.enable_check_button:
            return self.check_button_flag.get()
        else:
            raise AttributeError("该确认窗口没有复选框！")
        
    def check_button_flag_set(self, value:bool):
        """设置复选框的值，若没有复选框则报错"""
        if self.enable_check_button:
            self.check_button_flag.set(value)
        else:
            raise AttributeError("该确认窗口没有复选框！")

class Timer:
    """基于tkinter窗口的计时器"""
    def __init__(self, master=None, time:int=0, func=None, judge=True):
        self.master = master
        self.time = time
        self.func = func
        self.judge = judge
        self._if_timer_start = False
        self._tkafter = None
        self.timevar = tk.StringVar()
        self.timevar_f = tk.StringVar()

        self.timevar_f.set("0小时0分钟")
        self.timevar.set(0)
        
        if self.time % 10 != 0:
            raise ValueError("time属性需要是大于零的十的倍数！")
        
        self.timer()

    def timer(self):  #以十秒钟为单位计时
        if self.judge and self.time > 0:
            if self._if_timer_start:
                self.time -= 10
                self.timevar.set(self.time)
                self.timevar_f.set(("%d小时%d分钟")%(self.time//3600, self.time%3600//60))  #格式化的tk.Stringvar类型的时间
                self._tkafter = self.master.after(10000, self.timer)
            else:
                self.timevar.set(self.time)
                self.timevar_f.set(("%d小时%d分钟")%(self.time//3600, self.time%3600//60))  #格式化的tk.Stringvar类型的时间
                self._if_timer_start = True
                self._tkafter = self.master.after(10000, self.timer)
        if self.judge and self.time == 0:
            self.conduct()

    def conduct(self):  #直接执行函数
        if self.func:
            self.func()
        self._if_timer_start = False

    def cancel(self):  #取消执行
        if self._tkafter:
            self.master.after_cancel(self._tkafter)
            self._tkafter = None

class NoticeWindow(tk.Toplevel):
    """提醒界面"""
    def __init__(self, master = None, _title = None, text="", btext="确认", textvariable:tk.StringVar=None, font_l="TkDefaultFont", font_b="TkDefaultFont", command=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.master = master
        self._title = _title
        self.text = text
        self.btext = btext
        self.textvariable = textvariable
        self.font_l = font_l
        self.font_b = font_b
        self.command = command

        if text and textvariable:  #若两种文本同时输入，报错且以text输入值为准
            textvariable = None
            raise ValueError('冲突！输入了多种文本！')
        elif textvariable:  #若textvariable类型错误，则使用text的默认值，即''
            if not isinstance(self.textvariable, tk.StringVar):
                raise TypeError("textvariable 必须是 tk.StringVar 类型")

        self.title(self._title)
        self.geometry('300x100')
        self.resizable(False, False)
        self.withdraw()

        if self.textvariable:
            self.label = tk.Label(self, textvariable=self.textvariable, font=self.font_l,fg="#000000")
        else:
            self.label = tk.Label(self, text=self.text, font=self.font_l,fg="#000000")

        self.bto = tk.Button(self, text=self.btext, width=10, bg='grey', fg='white', bd=2, font=self.font_b, command=self.command)
        self.bind("<Return>", lambda event : self.command())

        self.label.pack(pady=5)
        self.bto.pack(pady=5)

    def show(self):
        if self.state() != 'withdrawn':
            self.withdraw()
            self.deiconify()
        else:
            self.deiconify()
        self.lift()

class ScreenShotWindow(tk.Toplevel):
    """浏览截图界面"""
    def __init__(self, master=None, path=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.master = master
        self.path = path
        self.is_shown = False
        self.title("截屏浏览")
        self.geometry("830x500")
        self.resizable(False, False)

        self.canvas = tk.Canvas(self, bg='white', width=800, height=500)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.image_frame = tk.Frame(self.canvas, bg='white')
        self.image_frame.bind("<Configure>", lambda event : self.canvas.configure(scrollregion=self.canvas.bbox("all"))) #更新滚动区域
        self.canvas.create_window((0, 0), window=self.image_frame, anchor='nw')

        self.withdraw() #初始化时隐藏窗口

        self.scrollbar = tk.Scrollbar(self, orient='vertical', bd=2, width=30, command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=3, sticky='ns')

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)) #绑定滚轮滚动
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-int(event.delta/120), "units")

    def show(self):
        if self.state() != 'withdrawn':
            self.withdraw() 
            self.deiconify()
        else:
            self.deiconify()
        self.lift()
        self.is_shown = True
        self._load_image()

        for n in self.image_frame.winfo_children():
            n.destroy()

        r=c=0
        for n in self.picture_list:
            label = tk.Label(self.image_frame, image=n, bg='white')
            label.grid(row = r, column = c, padx=5, pady=5)
            label.bind("<Button-1>", lambda event : print("clicked"))
            c+=1
            if c == 3:
                c = 0
                r += 1

    def refresh(self):
        if self.is_shown:
            self._load_image()

            for n in self.image_frame.winfo_children():
                n.destroy()

            r=c=0
            for n in self.picture_list:
                label = tk.Label(self.image_frame, image=n)
                label.grid(row = r, column = c, padx=5, pady=5)
                c+=1
                if c == 3:
                    c = 0
                    r += 1

    def _load_image(self):
        self.picture_list = []
        for n in os.listdir(self.path):
            image = Image.open(self.path+"\\"+n)
            image = image.resize((250, 150))
            photo = ImageTk.PhotoImage(image)
            if n[:5] == 'hssp_':
                self.picture_list.append(photo)

    def withdraw(self):
        super().withdraw()
        self.is_shown = False

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("400x300")
    root.title("测试moretk模块")
    
    ssw = ScreenShotWindow(root, path="C:/Users/Datudo/Desktop/py/healthy_surf/screenshot")

    btn = tk.Button(root, text="打开窗口", command=ssw.show)
    btn.pack(pady=20)

    root.mainloop()