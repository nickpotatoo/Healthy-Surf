import tkinter as tk
from tkinter import font as tkfont
from tkinter import filedialog
from tkinter import ttk
from typing import Literal

def font_width_deal(address_f, label):  #用于计算地址长度是否过长，若过长，则返回截短后加上省略号的地址，其中label需要为要处理的tkinter.label实例
        try:
            width = label.winfo_width()
            font = tkfont.Font(font=label.cget("font"))
            address_c = address_f
            if font.measure(address_c) <= width:
                return address_f
            else:
                address_f = ''
                for v in address_c:
                    if font.measure(address_f + v + '...') > width - 10:
                        break
                    address_f += v
                address_f += '...'
                return address_f 
        except:
            print('sth wrong')        

class ToolTip:  #提示框
    def __init__(self, widget, font="TkDefaultFont", textvariable=None, text='',condition=True, wraplength=500):
        self.if_tv = False
        self.widget = widget
        self.font = font
        self.text = text
        self.condition = condition
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
            if not self.condition or self.tip_window or (not self.text and not self.textvariable):
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

class AddressInputBox(tk.Frame):  #地址输入框
    def __init__(self, master=None, text='Saving Address', font_r="TkDefaultFont", font_a="TkDefaultFont", default_address='', button_size=1, width_a=50, bg='white', if_omit=True, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.text = text
        self.master = master
        self.font_r = font_r
        self.font_a = font_a
        self.button_size = button_size
        self.default_address = default_address
        self.width_a = width_a
        self.bg = bg
        self.if_omit = if_omit

        self.address = self.default_address
        self.address_v = tk.StringVar()
        self.address_v.set(self.address)
        self.address_s = tk.StringVar()

        self.label_r = tk.Label(self, text=self.text, font=self.font_r)
        self.label_r.pack(side='left')

        self.label_a = tk.Label(self, textvariable=self.address_s, font=self.font_a, fg="#000000", bg=self.bg, relief='solid', borderwidth=0.5, width=self.width_a, anchor='w')
        self.label_a.pack(side='left')

        self.label_a.bind("<Configure>", lambda event : self.__ads_set(ads_get=None))  

        self.button = tk.Button(self,bd=1,height=1,width=2,font=('微软雅黑', 7*self.button_size),bg='grey',fg='white',text='▼',command=self.__bto_adsca_deal)
        self.button.pack(side='right')

    def bind(self, action="<Enter>", func=None):  #重写bind方法
        if action == "<Enter>":
            self.label_a.bind("<Enter>", func)
        elif action == "<Leave>":
            self.label_a.bind("<Leave>", func)

    def winfo_rootx(self):   #重写winfo_rootx方法，返回label_a的x坐标
        return self.label_a.winfo_rootx()
    
    def address_get(self):  #获取地址（仅当下）
        return self.address
    
    def address_var_get(self):  #获取为tk.Stringvar()实例的地址
        return self.address_v
    
    def __bto_adsca_deal(self):  #仅用于获取地址界面
        ads_get =  None
        save_path = filedialog.askdirectory()
        if save_path:
            ads_get = save_path
            self.__ads_set(ads_get=ads_get)
        else:
            pass 

    def __ads_set(self, ads_get):  #用于为各个地址属性赋值最终self.address与self.address_v即为地址，ads_get=None时用于初始化
        if not ads_get:
            if self.if_omit:
                self.address_s.set(font_width_deal(self.address, self.label_a))
            else:
                self.address_s.set(self.address)
        else:
            if self.if_omit:
                address_t = font_width_deal(ads_get, self.label_a)
            else:
                self.address_t = self.address
                self.address_v.set(ads_get)
                self.address = ads_get
            self.address_s.set(address_t)

class TextComboBox(tk.Frame):   #带有文字的combobox
    def __init__(self, master=None, text='', values=[], default_index=0, font_l="TkDefaultFont", font_c="TkDefaultFont", *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.master = master
        self.text = text
        self.values = values
        self.default_index = default_index
        self.font_l = font_l
        self.font_c = font_c

        self.label = tk.Label(self, text=self.text, font=self.font_l)
        self.label.pack(side='left')

        self.combobox = ttk.Combobox(self, values=self.values, font=self.font_c)
        self.combobox.pack(side='right')
        if self.values:    #如果有给值的话，默认为default_index
            self.combobox.current(self.default_index)

    def current(self, newindex=0):   #写一个current方法，使得可以从combobox丝滑过渡到我写的这个类
        if newindex:
            self.combobox.current(newindex=newindex)
        return self.combobox.current()
    
    def bind(self, *args, **kwargs):  #同上
        self.combobox.bind(*args, **kwargs)

class KeyWrong(tk.Toplevel):
    """密码错误界面，默认隐藏，.show()方法显示"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title('错误')
        self.geometry('400x100')
        self.configure(bg='white')
        self.resizable(False, False)

        self.label = tk.Label(self, text='密码错误',font=('微软雅黑', 14),fg="#000000", bg='white')
        self.label.pack(pady=30)

        self.withdraw()

    def show(self):
        if self.state() != 'withdrawn':
            self.withdraw()
            self.deiconify()
        else:
            self.deiconify()

class TimeSpin(tk.Frame):
    def __init__(self, master, values, amount=1, width=80, text='', font_l="TkDefaultFont", font_b="TkDefaultFont" ,*args, **kwargs):
        super().__init__(master, *args, **kwargs)

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

        if amount > len(self.values):
            raise ValueError("The amount is too large.")

        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bg="white")
        self.canvas.pack(side="left")

        self.canvas.bind("<MouseWheel>", self.on_mousewheel)# 绑定滚轮
        self.canvas.bind("<B1-Motion>", self.on_mousedrag)# 绑定鼠标拖拽
        self.canvas.bind("<Button-1>", self.on_mouse1click)# 绑定鼠标点击
        self.draw()# 绘制内容

        self.canvas.create_line(0, self.mid, width, self.height//2, fill="red", dash=(2, 2))# 中心线（选中区域）

        self.label = tk.Label(self, text=self.text, font=self.font_l)
        self.label.pack(side='right')

    def draw(self):
        """绘制滚轮上的值"""
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
                if -self.item_height <= y < self.height:   #多画一点，防止穿帮
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
                if -self.item_height < y <= self.mid + self.item_height:
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

        if self.offset >= self.total_height:  # 让它循环滚动
            self.offset -= self.total_height
        elif self.offset <= -self.total_height:
            self.offset += self.total_height

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

        if self.offset >= self.total_height:
            self.offset -= self.total_height
        elif self.offset <= -self.total_height:  #又对self.offset处理，使其不过大并循环滚动
            self.offset += self.total_height

        self.draw()

    def on_mouse1click(self, event):
        self.mouse_y_org = event.y
        self.offset_org = self.offset
        return self.mouse_y_org

    def get_selected(self):
        """返回当前选中的值"""
        return self.values[self.idx]

if __name__ == '__main__':
    def a(event):
        global textbox
        print(textbox.current())

    root = tk.Tk()
    root.geometry("500x500")

    full_text = "这是一个非常非常长的路径示例，用于显示ooltip和省略号效果11111111111111111111111111111111111111111111"

    #lab = tk.Label(root, text=full_text, fg="#000000", bg='white', anchor='w')
    #lab.pack(fill='x', padx=10, pady=20)
    lab2 = tk.Label(root, text=full_text, fg="#FF0000", bg='white', anchor='w', font=("微软雅黑",10), width=50)
    lab2.pack(fill='x', padx=10, pady=20)

    condition1 = False
    #tooltip = ToolTip(lab, text=full_text)
    for char in full_text:
        if char == 'T':
            condition1 = True
    remindtip = ToolTip(lab2, text=full_text, font=("微软雅黑",10))

    test = AddressInputBox(root, button_size=1, default_address=r'这是一个非常非常长的路径示例，用于显示ooltip和省略号效果11111111111111111111111111111111111111111111')
    test.pack()

    testtip = ToolTip(test, textvariable=test.address_var_get())

    textbox = TextComboBox(root, text='test', values=['a','b','c'], font_l=('微软雅黑', 13), font_c=('微软雅黑', 13))
    textbox.pack()

    textbox.bind("<Button-1>", a)

    wrong = KeyWrong(root)
    wrong.show()
    wrong.withdraw()

    bto = tk.Button(root, text='Yes', command=wrong.show)
    bto2 = tk.Button(root, text='No', command=wrong.withdraw)
    bto.pack()
    bto2.pack()

    font_width_deal('123', lab2)

    abcdefg = ['0', "1", "2", "3"]
    timespin = TimeSpin(root, values=abcdefg, amount=4)
    timespin.pack()

    root.mainloop()