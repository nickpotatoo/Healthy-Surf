import tkinter as tk
from lib import *
from datetime import datetime
import time
from PIL import Image
from pystray import Icon, MenuItem, Menu
import os
# 导入必要库

version = "v1.3"

SECRET_KEY = "potato_love"

default_config = {
    'ss_path':R'.\screenshot', 
    'ss_max_amount': 100, 
    'ss_quality': 1, 
    'ss_shotgap': 30*1000, 
    'if_quit_judge': -1, 
    'password_key': 'potato',
    'if_ask_delete_history': True,
    'if_ask_delete_screenshot': True
    }
config_copy = {}

default_hide = False
if_turn_off_computer = False
turn_off_computer_timer = None
admin_mode = False

screenshoter_instance = None
screenshot_viewer_instance = None

history_recorder_instance = None
history_manager_instance = None

config_manage_instance = None
config_manager_instance = None

turn_off_computer_window = None

class oIcon:  #程序托盘图标
    def __init__(self, master):
        self.master = master

        self.icon_image = Image.open(".\\icon.png")
        self.tray_icon = Icon("App", self.icon_image, menu=self.create_menu())

    def create_menu(self):
        return Menu(
           MenuItem("显示", self.show),
           MenuItem("退出", self.exit)
       )

    def show(self):
        self.master.deiconify()

    def exit(self):
        password(0)

def safe_write(filename, content):  #安全写入文件
    tmpfile = filename + ".tmp"
    with open(tmpfile, "w") as file:
        file.write(content)
    os.replace(tmpfile, filename)

def run_timer():   #计时器，用于更新monitor文件
    safe_write(".\\monitor", "b" + str(time.time()))
    root.after(10000, run_timer)

def if_quit():  #询问退出选项
    def quit_straight():  #选择直接退出
        if quit_ask_window.check_button_flag:  #选了不再提问，则储存至config
            config_manage_instance.set_config("if_quit_judge", 1)
        password(0)
        quit_ask_window.destroy()

    def window_hide():  #选择最小化
        if quit_ask_window.check_button_flag:  #选了不再提问，则储存至config
            config_manage_instance.set_config("if_quit_judge", 0)
        for widget in root.winfo_children():  #清理所有打开的界面
                if isinstance(widget, tk.Toplevel):
                    widget.destroy()
        root.withdraw()
        quit_ask_window.destroy()

    if config_manage_instance.get_config('if_quit_judge') == -1:   #如果没选过不再提问，或者后续取消不在提问，则问这个问题
        quit_ask_window = moretk.CfmWindow(root, text = "请选择退出选项", font_b='微软雅黑', font_l='微软雅黑', on_cancel=window_hide, confirm_button_text='直接退出', cancel_button_text='最小化', on_confirm=quit_straight, enable_check_button=True, check_button_text="下次不再提问")
        quit_ask_window.show()
    
    else:
        if config_manage_instance.get_config('if_quit_judge'):
            password(0)
        else:
            for widget in root.winfo_children():
                if isinstance(widget, tk.Toplevel):
                    widget.destroy()
            root.withdraw()

def password(event_f):  # 用于密码确认
    global root
    
    def password_check():  # 确认密码是否正确，如果是则执行对应操作
        global admin_mode
        try:
            if shur1.get() == config_manage_instance.get_config('password_key') or admin_mode:
                if event_f == 0:   #程序退出
                    if not(config_manage_instance.get_config('if_quit_judge') == 0):
                        icon.tray_icon.stop()
                    safe_write("monitor", "d")
                    root3.destroy()
                    icon.tray_icon.stop()
                    root.destroy()
                elif event_f == 1:  #显示历史界面
                    open_history_manager_window()
                    root3.destroy()  
                elif event_f == 2:   #显示配置界面
                    open_config_manager_window()
                    root3.destroy()
                elif event_f ==3:  #显示定时关机界面
                    cc_window()
                    root3.destroy()
                elif event_f ==4:  #显示截图浏览界面
                    open_screenshot_viewer_window()
                    root3.destroy()
            elif shur1.get() == 'admin':  #管理员模式
                admin_mode = True
                root3.destroy()
            else:
                kww.show()
                shur1.delete(0, tk.END)
        except Exception as e:
            print("错误：", e)
    
    root3 = tk.Toplevel(root)
    root3.title('输入密码')
    root3.geometry('400x100')
    root3.configure(bg='white')
    root3.resizable(False, False)

    shur1 = tk.Entry(root3, width=15, font=('微软雅黑', 16), fg='black', borderwidth=1, justify='left', bg="#E5E5E5")
    shur1.bind("<Return>", lambda event : password_check())
    shur1.pack(side='top', pady=10)

    bto3 = tk.Button(root3, bd=2, height=1, width=10, font='微软雅黑', bg='grey', fg='white',text='确认', command=password_check)
    bto3.pack(side='bottom', pady=10)

    kww = moretk.NoticeWindow(root3, _title="密码错误", text="密码错误", font_l=("微软雅黑", 15), font_b=("微软雅黑", 12), command=lambda : kww.withdraw())  # 用于生成密码错误界面，默认隐藏

    root3.lift()

    if admin_mode:  #管理员模式，跳过密码检查
        password_check()

def cc_window():  #定时关机功能 
    global turn_off_computer_window
    def cfm():
        cfmw.show()
        cch_result = cch.get_selected()
        ccm_result = ccm.get_selected()
        tv.set("是否确认%d小时%d分钟后关机？"%(cch_result, ccm_result))
        
    def on_confirm():
        global if_turn_off_computer, turn_off_computer_timer
        cch_result = cch.get_selected()
        ccm_result = ccm.get_selected()
        if_turn_off_computer = True
        turn_off_computer_timer = moretk.Timer(root, cch_result*3600+ccm_result*60-60, on_cclose)
        window_cc.destroy()

    def cancel_cc_cfm():
        ccc_cfmw = moretk.CfmWindow(window_ccc, text = "确认取消电脑定时关机？", font_b='微软雅黑', font_l='微软雅黑', on_cancel=lambda : ccc_cfmw.withdraw(), on_confirm=cancel_cc)
        ccc_cfmw.show()

    def cancel_cc():
        global if_turn_off_computer
        turn_off_computer_timer.cancel()
        if_turn_off_computer = False
        window_ccc.destroy()

    def on_cclose():
        def shutdown():
            global if_turn_off_computer
            if_turn_off_computer = False
            os.system("shutdown /s /t 1")
        turn_off_computer_reminder = tk.Toplevel(root)

        turn_off_computer_reminder.title('错误')
        turn_off_computer_reminder.geometry('400x100')
        turn_off_computer_reminder.configure(bg='white')
        turn_off_computer_reminder.resizable(False, False)

        nlabel = tk.Label(turn_off_computer_reminder, text='电脑将于一分钟后关机，请及时保存文件！',font=('微软雅黑', 14),fg="#000000", bg='white')
        nlabel.pack(pady=30)

        root.after(60000, shutdown)

    def when_window_delete():
        global turn_off_computer_window
        turn_off_computer_window.destroy()
        turn_off_computer_window = None

    if not turn_off_computer_window:
        if not if_turn_off_computer:
            window_ccc = None
            window_cc = tk.Toplevel(root)
            window_cc.title('定时关机设置')
            window_cc.geometry('300x350')
            window_cc.configure(bg='white')
            window_cc.resizable(False, False)
            window_cc.lift()
            turn_off_computer_window = window_cc

            tv = tk.StringVar()
            tv.set("None")
            cfmw = moretk.CfmWindow(window_cc, textvariable=tv, font_b='微软雅黑', font_l='微软雅黑', on_cancel=lambda : cfmw.withdraw(), on_confirm=on_confirm)

            label_cc = tk.Label(window_cc, text='选择关机时间间隔', font=('微软雅黑', 14), fg="#000000", bg='white')
            label_cc.place(x=150, y=30, anchor='center')

            list_h = [i for i in range(0,25)]
            list_m = [i for i in range(1,61)]

            timespin_cc_h = cch = moretk.TimeSpin(window_cc, list_h, amount=6, text='小时', font_l=('微软雅黑', 14), font_b=('微软雅黑', 14), bg='white', text_side='bottom')
            timespin_cc_m = ccm = moretk.TimeSpin(window_cc, list_m, amount=6, text='分钟', font_l=('微软雅黑', 14), font_b=('微软雅黑', 14), bg='white', text_side='bottom')
            cch.current(0)
            ccm.current(0)
            timespin_cc_h.place(x=80, y=160, anchor='center')
            timespin_cc_m.place(x=220, y=160, anchor='center')

            bto_cfm = tk.Button(window_cc,bd=2,height=1,width=10,font='微软雅黑',bg='grey',fg='white',text='确认', command=cfm)
            bto_cacl = tk.Button(window_cc,bd=2,height=1,width=10,font='微软雅黑',bg='grey',fg='white',text='取消', command=window_cc.destroy)
            bto_cfm.place(x=80, y=300, anchor='center')
            bto_cacl.place(x=220, y=300, anchor='center')

            window_cc.lift()
        
        else:
            window_cc = None
            window_ccc = tk.Toplevel(root)
            window_ccc.title('正在为关机计时')
            window_ccc.geometry('300x220')
            window_ccc.configure(bg='white')
            window_ccc.resizable(False, False)
            window_ccc.lift()
            turn_off_computer_window = window_ccc

            frame_cc = tk.Frame(window_ccc, bg='white')
            frame_cc.pack(side="top", pady=5)

            label_line1 = tk.Label(frame_cc, text="电脑将于", font=('微软雅黑', 14), fg="#000000", bg='white')
            label_line1.pack(pady=5)

            frame_line2 = tk.Frame(frame_cc, bg='white')
            frame_line2.pack(pady=5)

            label_line2 = tk.Label(frame_line2, textvariable=turn_off_computer_timer.timevar_f, font=('微软雅黑', 20, 'bold'), fg="#FF0000", bg='white')
            label_line2.pack(side='left')

            label_after = tk.Label(frame_line2, text="后", font=('微软雅黑', 20, 'bold'), fg="#FF0000", bg='white')
            label_after.pack(side='left')

            label_line3 = tk.Label(frame_cc, text="关机", font=('微软雅黑', 14), fg="#000000", bg='white')
            label_line3.pack(pady=5)

            bto_cancel_cc = tk.Button(window_ccc,bd=2,height=1,width=10,font='微软雅黑',bg='grey',fg='white',text='取消关机', command=cancel_cc_cfm)
            bto_cancel_cc.pack(pady=5)

            window_ccc.lift()

        turn_off_computer_window.protocol("WM_DELETE_WINDOW", when_window_delete)
        
    else:
        turn_off_computer_window.lift()

def open_screenshot_viewer_window():  #截图浏览界面
    global screenshot_viewer_instance, config_manage_instance
    def when_delete_window():
        global screenshot_viewer_instance
        screenshot_viewer_instance.destroy()
        screenshot_viewer_instance = None

        if not screenshoter_instance.if_circulate():
            screenshoter_instance.get_screen()

    if not screenshot_viewer_instance:
        screenshot_viewer_instance = screenshot_viewer.ScreenshotViewer(
            root, 
            path=config_manage_instance.get_config("ss_path"), 
            if_ask_delete_screenshot=config_manage_instance.get_config("if_ask_delete_screenshot"), 
            when_config_change_call=lambda value: config_manage_instance.set_config("if_ask_delete_screenshot", value)
            )

        screenshoter_instance.cancel_screenshot_circulate()

        screenshot_viewer_instance.protocol("WM_DELETE_WINDOW", when_delete_window)
    else:
        screenshot_viewer_instance.lift()

def open_history_manager_window():
    global history_manager_instance, history_recorder_instance, config_manage_instance
    def when_delete_window():
        global history_manager_instance
        history_manager_instance.destroy()
        history_manager_instance = None

    if not history_manager_instance:
        history_manager_instance = history_manager.HistoryManager(
            root, 
            config_manage_instance.get_config("if_ask_delete_history"), 
            history_recorder=history_recorder_instance, 
            when_config_change_call=lambda flag : config_manage_instance.set_config("if_ask_delete_history", flag)
            )

        history_manager_instance.protocol("WM_DELETE_WINDOW", when_delete_window)
    else:
        history_manager_instance.lift()

def update_config(): # 更新所有config需要更新的地方
    global config_manage_instance
    screenshoter_instance.update_config(
        config_manage_instance.get_config("ss_path"), 
        config_manage_instance.get_config("ss_max_amount"), 
        config_manage_instance.get_config("ss_quality"), 
        config_manage_instance.get_config("ss_shotgap")
        )

def open_config_manager_window():
    global config_manager_instance, config_manage_instance
    def when_destory_window():
        global config_manager_instance
        config_manager_instance = None

    def when_config_manager_change_config(): # 当在config_manager中修改了配置时，调用这个函数将修改应用到config_copy和screenshoter_instance中
        update_config()

    if config_manager_instance is None:
        config_manager_instance = config_manager.ConfigManager(root, config_manage_instance, when_config_change_call=when_config_manager_change_config, when_window_destroy_call=when_destory_window)
    else:
        config_manager_instance.lift()


root = tk.Tk()
root.title(f'健康上网{version}')
root.geometry('662x400')
root.configure(bg='white')
root.resizable(False, False)
root.iconphoto(False, tk.PhotoImage(file='icon.png'))
root.lift()

history_label = tk.Label(root, font=('微软雅黑', 14), fg="#000000", bg='white')
history_label.place(relx=0.5, rely=0.45, anchor='center')

history_button = tk.Button(root,bd=2,height=1,width=15,font='微软雅黑',bg='grey',fg='white',text='历史',command=lambda : password(1))
history_button.place(relx=0.95, rely=0.05, anchor='ne')

config_button = tk.Button(root,bd=2,height=1,width=15,font='微软雅黑',bg='grey',fg='white',text='设置',command=lambda : password(2))
config_button.place(relx=0.05, rely=0.05, anchor='nw')

computer_turn_off_button = tk.Button(root,bd=2,height=1,width=15,font='微软雅黑',bg='grey',fg='white',text='定时关机',command=lambda : password(3))
computer_turn_off_button.place(relx=0.05, rely=0.95, anchor='sw')

screenshot_button = tk.Button(root,bd=2,height=1,width=15,font='微软雅黑',bg='grey',fg='white',text='截屏预览',command=lambda : password(4))
screenshot_button.place(relx=0.95, rely=0.95, anchor='se')

icon = oIcon(root)
icon.tray_icon.run_detached()

root.protocol('WM_DELETE_WINDOW', if_quit)

config_manage_instance = config_manager.ConfigManage() # 实例化配置管理器
config_manage_instance.register(config = default_config) # 将默认配置注册到配置管理器
config_manage_instance.load_config() # 将config传入配置管理器

history_recorder_instance = history_manager.HistoryRecorder(root) # 实例化历史记录管理器，并将历史记录绑定到界面显示
history_label.configure(textvariable=history_recorder_instance.get())

screenshoter_instance = screenshoter.ScreenShoter(root, path=config_manage_instance.get_config("ss_path"), max_amount=config_manage_instance.get_config("ss_max_amount"), quality=config_manage_instance.get_config("ss_quality"), shotgap=config_manage_instance.get_config("ss_shotgap")) # 实例化截屏管理器
screenshoter_instance.start() # 启动截屏循环

if os.path.exists(".\\monitor"):
    with open(".\\monitor", "r") as file:
        text = file.read().strip()
        if text and text[0] == 'a':
            default_hide = True

run_timer()

if default_hide:
    root.withdraw()

root.mainloop()