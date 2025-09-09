import tkinter as tk

class ToolTip:  #提示框
    def __init__(self, widget, font="TkDefaultFont", text='',condition=True):
        self.widget = widget
        self.font = font
        self.text = text
        self.condition = condition
        self.tip_window = None
        self.widget.bind("<Enter>", self.enter_tip)
        self.widget.bind("<Leave>", self.hide_tip)
    
    def show_tip(self):
        while self.if_enter:
            if not self.condition or self.tip_window or not self.text:
                return
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 1
            self.tip_window = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)  # 去掉窗口边框
            tw.wm_geometry(f"+{x}+{y}")
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
    def __init__(self, master=None, text='Saving Address', font_r="TkDefaultFont", font_a="TkDefaultFont", default_address='', button_size=1, width_a=50, bg='white', **kwargs):
        self.text = text
        self.master = master
        self.font_r = font_r
        self.font_a = font_a
        self.button_size = button_size
        self.default_address = default_address
        self.width_a = width_a
        self.bg = bg

        super().__init__(master, **kwargs)

        self.address = tk.StringVar()
        self.address.set(self.default_address)  #最终self.address即为地址

        self.label_r = tk.Label(self, text=self.text, font=self.font_r)
        self.label_r.pack(side='left')

        self.label_a = tk.Label(self, textvariable=self.address, font=self.font_a, fg="#000000", bg=self.bg, relief='solid', borderwidth=0.5, width=self.width_a, anchor='w')
        self.label_a.pack(side='left')

        self.button = tk.Button(self,bd=1,height=1,width=2,font=('微软雅黑', 9*self.button_size),bg='grey',fg='white',text='▼')
        self.button.pack(side='right')

    def bind(self, action="<Enter>", func=None):
        if action == "<Enter>":
            self.label_a.bind("<Enter>", func)
        elif action == "<Leave>":
            self.label_a.bind("<Leave>", func)

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("800x500")

    full_text = "这是一个非常非常长的路径示例，用于显示ooltip和省略号效果11111111111111111111111111111111111111111111"

    #lab = tk.Label(root, text=full_text, fg="#000000", bg='white', anchor='w')
    #lab.pack(fill='x', padx=10, pady=20)
    lab2 = tk.Label(root, text=full_text, fg="#FF0000", bg='white', anchor='w')
    lab2.pack(fill='x', padx=10, pady=20)

    condition1 = False
    #tooltip = ToolTip(lab, text=full_text)
    for char in full_text:
        if char == 'T':
            condition1 = True
    remindtip = ToolTip(lab2, text=full_text, font=("微软雅黑",10))

    test = AddressInputBox(root, button_size=1, default_address=r'C:\Program Files (x86)\Microsoft')
    test.pack()

    testtip = ToolTip(test, text=test.address)

    root.mainloop()