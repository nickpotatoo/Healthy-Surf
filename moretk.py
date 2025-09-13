import tkinter as tk
from tkinter import font as tkfont
from tkinter import filedialog

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
    def __init__(self, widget, font="TkDefaultFont", textvariable=None, text='',condition=True):
        self.if_tv = False
        self.widget = widget
        self.font = font
        self.text = text
        self.condition = condition
        self.tip_window = None
        self.widget.bind("<Enter>", self.enter_tip)
        self.widget.bind("<Leave>", self.hide_tip)
        self.textvariable = textvariable

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
                label = tk.Label(tw, textvariable=self.textvariable, justify='left', background="#ffffff", relief='solid', borderwidth=1, font=self.font)
            else:
                label = tk.Label(tw, text=self.text, justify='left', background="#ffffff", relief='solid', borderwidth=1, font=self.font)
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
    def __init__(self, master=None, text='Saving Address', font_r="TkDefaultFont", font_a="TkDefaultFont", default_address='', button_size=1, width_a=50, bg='white', if_omit=True, **kwargs):
        self.text = text
        self.master = master
        self.font_r = font_r
        self.font_a = font_a
        self.button_size = button_size
        self.default_address = default_address
        self.width_a = width_a
        self.bg = bg

        super().__init__(master, **kwargs)

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
            self.address_s.set(font_width_deal(self.address, self.label_a))
        else:
            address_t = font_width_deal(ads_get, self.label_a)
            self.address_v.set(ads_get)
            self.address = ads_get
            self.address_s.set(address_t)

if __name__ == '__main__':
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

    font_width_deal('123', lab2)

    root.mainloop()