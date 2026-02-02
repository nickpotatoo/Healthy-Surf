import tkinter as tk
import screenshot
import moretk
import picture_viewer
import encryption
from datetime import datetime
import time
from PIL import Image
from pystray import Icon, MenuItem, Menu
import os
import json        #导入必要库

version = "v0.1.1"
SECRET_KEY = "potato_love"
if_first_run = True
time_date = "0"
total_time = 0
default_config = {'ss_path':R'.\screenshot', 
                  'ss_max_amount': 100, 
                  'ss_quality': 1, 
                  'ss_shotgap': 30*1000, 
                  'if_quit_judge': -1, 
                  'password_key': 'potato',
                  'if_ask_delete_history': True,
                  'if_ask_delete_screenshot': True}
config = default_config
default_hide = False
time_date = int(datetime.now().strftime('%Y%m%d'))
default_history = {time_date: "0"}
history = default_history
if_turn_off_computer = False
turn_off_computer_timer = None
admin_mode = False
screenshoter = None

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

def load_history_json_encryption():   #读取或创建加密的本地历史文件，将结果保存为字典history
    global history, time_date
    try:
        history_c = encryption.decrypt_file("history.json", SECRET_KEY)
        if str(time_date) not in history_c:
            history_c[str(time_date)] = history[time_date] 
        history.clear()
        for k, v in history_c.items():
            history[int(k)] = v
    except Exception as e:
            print("读取 history.json 出错:", e)
            history.clear()
            history[time_date] = "0"

def history_write_json_encryption():  #将history以加密的json格式写入本地
    global history
    encryption.encrypt_file(history, "history.json", SECRET_KEY)

    if admin_mode:
        with open('.\\history_decrypt.json', 'w', newline='') as file:
            json.dump(history, file, indent=4)

def check_history():
    global time_date
    if not time_date in history:
        history[time_date] = "0"

def time_update_init():
    global total_time, time_date
    if os.path.exists('history.json'):
        load_history_json_encryption()
    else:
        history_write_json_encryption()
    check_history()
    total_time = int(history[time_date])

def time_update():
    global total_time, time_date
    if not if_first_run:
        total_time += 5
    history[time_date] = str(total_time)
    history_write_json_encryption()
    gap_hour = total_time // 3600
    gap_min = total_time % 3600 // 60
    gap_sec = total_time % 60
    lab1_var.set('您今日已累计使用电脑%d小时，%d分钟，%d秒' %(gap_hour, gap_min, gap_sec))
    root.after(5000, time_update)

def history_journal():   #用于图形界面查询历史
    global history, time_date
    
    root2 = tk.Toplevel()
    root2.title('使用历史')
    root2.geometry('662x400')
    root2.configure(bg='white')
    root2.resizable(False, False)
    hty_key = {}

    root2.lift()

    def htylist_refresh(if_circulate):  #对查询界面5秒一刷新
        nonlocal hty_key
        htylist.delete(0,tk.END)
        hty_key = {}
        htylist_insert()
        if if_circulate:
            root2.after(60000, lambda: htylist_refresh(True))

    def ask_window_on_confirm():
        nonlocal ask_window
        htylist_delete()
        if ask_window.get_checkbutton_value():
            config['if_ask_delete_history'] = False
            config_write_json_encryption()
        ask_window.withdraw()

    def ask_window_on_cancel():
        nonlocal ask_window
        if ask_window.get_checkbutton_value():
            config['if_ask_delete_history'] = False
            config_write_json_encryption()
        ask_window.withdraw()

    def htylist_delete_ask_window():  #删除历史询问窗口
        if config['if_ask_delete_history']:
            ask_window.show()
        else:
            htylist_delete()
    
    def htylist_delete():  #删除选中的本地历史并初始化
        global total_time, time_date
        nonlocal hty_key
        n, *args = htylist.curselection()
        key_f = hty_key[n]
        if key_f != time_date:
            del history[key_f]
        else:
            history[key_f] = '0'
            total_time = 0
        lab1_var.set('您今日已累计使用电脑0小时，0分钟，0秒')    
        history_write_json_encryption()
        htylist_refresh(False)

    def htylist_insert():  #将历史写入查询界面
        nonlocal hty_key
        i=0
        for key in history:
            time_f = int(history[key])
            gap_hour = time_f // 3600
            gap_min = time_f % 3600 // 60
            gap_sec = time_f % 60
            v = '%s:%d小时%d分钟%d秒'%(key, gap_hour, gap_min, gap_sec)
            htylist.insert(i,v)
            hty_key[i] = key
            i += 1
    
    sb = tk.Scrollbar(root2, bd=2, width=30)
    sb.pack(side = 'right', fill= 'y' )

    button_frame = tk.Frame(root2)
    
    delete_button = tk.Button(button_frame, bd=2, height=1, width=10, font='微软雅黑', bg='grey', fg='white', text='删除', command=htylist_delete_ask_window)
    delete_button.pack(side='left', padx= 5)

    refresh_button = tk.Button(button_frame, bd=2, height=1, width=10, font='微软雅黑', bg='grey', fg='white', text='刷新', command=lambda:htylist_refresh(False))
    refresh_button.pack(side='right', padx= 5)

    button_frame.pack(side='bottom', pady=10)

    htylist = tk.Listbox(root2, yscrollcommand=sb.set, width= 662, height= 15, font=('微软雅黑', 14))    

    if config['if_ask_delete_history']:
        ask_window = moretk.CfmWindow(root2, text = "确认删除选中的历史记录？", font_b='微软雅黑', font_l='微软雅黑', on_cancel=ask_window_on_cancel, on_confirm=ask_window_on_confirm, enable_check_button=True, check_button_text="不再提示")
    
    htylist_refresh(True)
    
    htylist.pack()

def if_quit():  #询问推出选项
    def quit_straight():  #选择直接退出
        if quit_ask_window.check_button_flag:  #选了不再提问，则储存至config
            config['if_quit_judge'] = 1
            config_write_json_encryption()
        password(0)
        quit_ask_window.destroy()

    def window_hide():  #选择最小化
        if quit_ask_window.check_button_flag:  #选了不再提问，则储存至config
            config['if_quit_judge'] = 0
            config_write_json_encryption()
        for widget in root.winfo_children():  #清理所有打开的界面
                if isinstance(widget, tk.Toplevel):
                    widget.destroy()
        root.withdraw()
        quit_ask_window.destroy()

    if config['if_quit_judge'] == -1:   #如果没选过不再提问，或者后续取消不在提问，则问这个问题
        quit_ask_window = moretk.CfmWindow(root, text = "请选择退出选项", font_b='微软雅黑', font_l='微软雅黑', on_cancel=window_hide, confirm_button_text='直接退出', cancel_button_text='最小化', on_confirm=quit_straight, enable_check_button=True, check_button_text="下次不再提问")
        quit_ask_window.show()
    
    else:
        if config['if_quit_judge']:
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
            if shur1.get() == config['password_key'] or admin_mode:
                if event_f == 0:   #程序退出
                    if not(config['if_quit_judge']):
                        icon.tray_icon.stop()
                    safe_write("monitor", "d")
                    root3.destroy()
                    icon.tray_icon.stop()
                    root.destroy()
                elif event_f == 1:  #显示历史界面
                    history_journal()
                    root3.destroy()  
                elif event_f == 2:   #显示配置界面
                    config_window()
                    root3.destroy()
                elif event_f ==3:  #显示定时关机界面
                    cc_window()
                    root3.destroy()
                elif event_f ==4:  #显示截图浏览界面
                    open_screenshot_viewing_window()
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

def config_read_json_encryption(): #用于读取加密的配置文件
    global config
    
    try:
        config = encryption.decrypt_file("config.json", SECRET_KEY)
    except:
        config = default_config

def screenshoter_init():
    global screenshoter
    screenshoter = screenshot.Screenshoter(path=config['ss_path'], max_amount=config['ss_max_amount'], quality=config['ss_quality'])

def screenshoter_config_update():
    screenshoter.path = config['ss_path']
    screenshoter.max_amount = config['ss_max_amount']
    screenshoter.quality = config['ss_quality']

def get_screen():  #主程序中使用截屏
    screenshoter.screenshot()
    screenshoter.picture_clean()
    root.after(config['ss_shotgap'], get_screen)

def config_write_json_encryption():   #用于将config中数值以加密的json格式写入本地
    global config
    encryption.encrypt_file(config, "config.json", SECRET_KEY)

    if admin_mode:
        with open('.\\config_decrypt.json', 'w', newline='') as file:
            json.dump(config, file, indent=4)

def config_window():  #显示配置界面
    class PasswordCange:  #用于修改密码
        def __init__(self, password_key:str = config['password_key']):
            self.password_key = password_key

            self.root = tk.Toplevel(root5)
            self.root.title('修改密码')
            self.root.geometry('500x350')
            self.root.configure(bg='white')
            self.root.resizable(False, False)
            self.root.lift()

            self.root_lab1 = tk.Label(self.root,  text='请输入原密码', font=('微软雅黑', 18), fg="#000000", bg='white')
            self.root_ety1 = tk.Entry(self.root, width=15, font=('微软雅黑', 16), fg='black', borderwidth=1, justify='left', bg="#E5E5E5")
            self.root_ety1.bind("<Return>", lambda event : self.confirm())

            self.root_lab2 = tk.Label(self.root,  text='请输入新密码', font=('微软雅黑', 18), fg="#000000", bg='white')
            self.root_ety2 = tk.Entry(self.root, width=15, font=('微软雅黑', 16), fg='black', borderwidth=1, justify='left', bg="#E5E5E5")
            self.root_ety2.bind("<Return>", lambda event : self.confirm())

            self.root_lab3 = tk.Label(self.root,  text='请重复输入新密码', font=('微软雅黑', 18), fg="#000000", bg='white')
            self.root_ety3 = tk.Entry(self.root, width=15, font=('微软雅黑', 16), fg='black', borderwidth=1, justify='left', bg="#E5E5E5")
            self.root_ety3.bind("<Return>", lambda event : self.confirm())

            self.root_bto = tk.Button(self.root, bd=2, height=1, width=10, font='微软雅黑', bg='grey', fg='white',text='确认', command=self.confirm)
            self.root_bto.bind("<Return>", lambda event : self.confirm())

            self.notice_text_v = tk.StringVar()
            self.notice_text_v.set("None")
            self.notice = moretk.NoticeWindow(self.root, _title = "错误！", textvariable = self.notice_text_v, font_l=('微软雅黑', 14), font_b=('微软雅黑', 10), command=lambda : self.notice.withdraw())

            self.root_lab1.pack(pady=5)
            self.root_ety1.pack(pady=5)
            self.root_lab2.pack(pady=5)
            self.root_ety2.pack(pady=5)
            self.root_lab3.pack(pady=5)
            self.root_ety3.pack(pady=5)
            self.root_bto.pack(pady=10)

        def root_show(self):
            if self.root.state() != 'withdrawn':
                self.root.withdraw()
                self.root.deiconify()
            else:
                self.root.deiconify()
            self.root.lift()

        def confirm(self):
            nonlocal changed_password

            if not admin_mode:
                if not(self.root_ety1.get()):
                    self.notice_text_v.set("请输入原密码！")
                    self.notice.show()
                elif self.root_ety1.get() != self.password_key:
                    self.notice_text_v.set("请输入正确的原密码！")
                    self.notice.show()
                    self.root_ety1.delete(0, tk.END)
                elif not(self.root_ety2.get()):
                    self.notice_text_v.set("请输入新密码！")
                    self.notice.show()
                elif not(self.root_ety3.get()):
                    self.notice_text_v.set("请重复输入新密码！")
                    self.notice.show()
                elif self.root_ety3.get() != self.root_ety2.get():
                    self.notice_text_v.set("两次输入的新密码不一致！")
                    self.notice.show()
                    self.root_ety2.delete(0, tk.END)
                    self.root_ety3.delete(0, tk.END)
                else:
                    changed_password = str(self.root_ety3.get())
                    self.password_key = changed_password
                    self.notice_text_v.set("密码修改成功！")
                    self.notice.show()
                    self.root_ety1.delete(0, tk.END)
                    self.root_ety2.delete(0, tk.END)
                    self.root_ety3.delete(0, tk.END)
                    self.root.withdraw()

            else:
                changed_password = str(self.root_ety3.get())
                self.password_key = changed_password
                self.notice_text_v.set("密码修改成功！")
                self.notice.show()
                self.root_ety1.delete(0, tk.END)
                self.root_ety2.delete(0, tk.END)
                self.root_ety3.delete(0, tk.END)
                self.root.withdraw()
            
    def config_update():  #用于关闭时将修改后的数值写入config
        config['ss_path'] = ss_path_inputbox.path_get()
        config['ss_max_amount'] = ss_cbb_ma_list_r[ss_cbb_ma.current()]
        config['ss_quality'] = ss_cbb_qty_list_r[ss_cbb_qty.current()]
        config['ss_shotgap'] = ss_cbb_gap_list_r[ss_cbb_gap.current()]
        if changed_password:    
            config['password_key'] = changed_password
        if ss_quitway_cb_1_var.get():
            config['if_quit_judge'] = 1
        elif ss_quitway_cb_2_var.get():
            config['if_quit_judge'] = 0
        else:
            config['if_quit_judge'] = -1

        screenshoter_config_update()

    def if_save():  #确认保存界面
        if if_change:
            root6 = tk.Toplevel(root5)
            root6.title('是否保存')
            root6.geometry('400x150')
            root6.configure(bg='white')
            root6.resizable(False, False)

            lab_is = tk.Label(root6, text='是否保存', font=('微软雅黑', 20), fg="#000000", bg='white')
            lab_is.pack(side='top', pady=20)

            bto_is_y = tk.Button(root6,bd=2,height=1,width=6,font=('微软雅黑', 13),bg='grey',fg='white',text='保存',command=lambda : (config_update(), config_write_json_encryption(), root6.destroy(), root5.destroy()))
            bto_is_n = tk.Button(root6,bd=2,height=1,width=6,font=('微软雅黑', 13),bg='grey',fg='white',text='取消',command=lambda : (root6.destroy(), root5.destroy()))
            bto_is_y.pack(side='left', padx=60)
            bto_is_n.pack(side='right', padx=60)
        else:
            root5.destroy()
    
    def change():  #用于确认是否发生修改
        nonlocal if_change
        if_change = True

    def quitway_choose_1():
        if ss_quitway_cb_1_var.get():
            ss_quitway_cb_2.deselect()

    def quitway_choose_2():
        if ss_quitway_cb_2_var.get():
            ss_quitway_cb_1.deselect()
    
    if_change = False

    root5 = tk.Toplevel(root)
    root5.title('设置界面')
    root5.geometry('600x400')
    root5.configure(bg='white')
    root5.resizable(False, False)

    ss_cbb_gap_list_r = [5*1000, 30*1000, 60*1000, 5*60*1000, 15*60*1000]
    ss_cbb_gap_list = ['5秒', '30秒', '1分钟', '5分钟', '15分钟']
    ss_cbb_gap = moretk.TextComboBox(root5, text="截屏间隔", font_l=('微软雅黑', 14),font_c=('微软雅黑', 12), values=ss_cbb_gap_list, bg="white")
    ss_cbb_gap.current(next(i for i, v in enumerate(ss_cbb_gap_list_r) if v == config["ss_shotgap"]))
    ss_cbb_gap.pack(pady=10)

    ss_cbb_ma_list_r = [5, 50, 100, 1000]
    ss_cbb_ma_list = ['5张', '50张', '100张', '1000张']
    ss_cbb_ma = moretk.TextComboBox(root5, text="最大保存数量", font_l=('微软雅黑', 14), font_c=('微软雅黑', 12), bg="white", values=ss_cbb_ma_list)
    ss_cbb_ma.current(next(i for i, v in enumerate(ss_cbb_ma_list_r) if v == config["ss_max_amount"]))
    ss_cbb_ma.pack(pady=10)

    ss_cbb_qty_list_r = [1, 2, 4, 8]
    ss_cbb_qty_list = ['1倍质量', '2倍质量', '4倍质量', '8倍质量']
    ss_cbb_qty = moretk.TextComboBox(root5, text="图片质量", font_l=('微软雅黑', 14), font_c=('微软雅黑', 12), bg="white", values=ss_cbb_qty_list)
    ss_cbb_qty.current(next(i for i, v in enumerate(ss_cbb_qty_list_r) if v == config["ss_quality"]))
    ss_cbb_qty.pack(pady=10)

    ss_path_inputbox = moretk.PathInputBox(root5, text="截屏保存路径", font_a=('微软雅黑', 10), font_r=('微软雅黑', 14), default_path=config['ss_path'], bg="white")
    ss_path_inputbox.pack(pady=10)

    pwdk_c_root = PasswordCange()
    pwdk_c_bto = tk.Button(root5, bd=2, height=1, width=10, font=('微软雅黑',10), bg='grey', fg='white', text='修改密码', command=pwdk_c_root.root_show)
    pwdk_c_bto.pack(pady=10)
    pwdk_c_root.root.withdraw()
    changed_password = None

    ss_quitway_frame = tk.Frame(root5, bg="white")
    ss_quitway_lab = tk.Label(root5, text='  当退出时，软件将：',font=('微软雅黑', 14),fg="#000000", bg='white')
    ss_quitway_lab.pack(pady=5,anchor='center')
    ss_quitway_cb_1_var = tk.BooleanVar()
    ss_quitway_cb_2_var = tk.BooleanVar()
    ss_quitway_cb_1 = tk.Checkbutton(ss_quitway_frame,font=('微软雅黑', 11),bg='white',text='直接退出',variable=ss_quitway_cb_1_var,command=quitway_choose_1)
    ss_quitway_cb_2 = tk.Checkbutton(ss_quitway_frame,font=('微软雅黑', 11),bg='white',text='最小化',variable=ss_quitway_cb_2_var,command=quitway_choose_2)
    ss_quitway_cb_1.deselect()
    ss_quitway_cb_2.deselect()
    if config['if_quit_judge'] == 1:
        ss_quitway_cb_1.select()
    elif config['if_quit_judge'] == 0:
        ss_quitway_cb_2.select()
    ss_quitway_cb_1.pack(side='left', padx=5)
    ss_quitway_cb_2.pack(side='right', padx=5)
    ss_quitway_frame.pack(pady=5)

    ss_bto_frame = tk.Frame(root5, bg="white")
    ss_bto_y = tk.Button(ss_bto_frame,bd=2,height=1,width=10,font='微软雅黑',bg='grey',fg='white',text='保存',command=lambda : (config_update(), config_write_json_encryption(), root5.destroy()))
    ss_bto_n = tk.Button(ss_bto_frame,bd=2,height=1,width=10,font='微软雅黑',bg='grey',fg='white',text='取消',command=root5.destroy)
    ss_bto_y.pack(side="left", padx=5)
    ss_bto_n.pack(side="right", padx=5)
    ss_bto_frame.pack(pady=10)

    tp = moretk.ToolTip(ss_path_inputbox, text=config['ss_path'])

    ss_cbb_gap.bind("<Button-1>",lambda event : change())  #用于确认是否发生修改
    ss_cbb_ma.bind("<Button-1>", lambda event : change())
    ss_cbb_qty.bind("<Button-1>", lambda event : change())
    ss_path_inputbox.bind("<AddressChange>", lambda event : change())
    ss_quitway_cb_1.bind("<Button-1>",lambda event : change())
    ss_quitway_cb_2.bind("<Button-1>",lambda event : change())
    pwdk_c_bto.bind("<Button-1>",lambda event : change())

    root5.protocol('WM_DELETE_WINDOW', if_save)  #关闭时显示是否保存界面（若发生修改）

def cc_window():  #定时关机功能 
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

    if not if_turn_off_computer:
        window_ccc = None
        window_cc = tk.Toplevel(root)
        window_cc.title('定时关机设置')
        window_cc.geometry('300x350')
        window_cc.configure(bg='white')
        window_cc.resizable(False, False)
        window_cc.lift()

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

def open_screenshot_viewing_window():  #截图浏览界面
    def refresh_circulate():
        screenshot_viewing_window.refresh()
        screenshot_viewing_window.after(int(config["ss_shotgap"]), lambda: refresh_circulate())
    
    screenshot_viewing_window = picture_viewer.PictureViewer(root, config["ss_path"], config, config_write_json_encryption)
    screenshot_viewing_window.show()

    refresh_circulate()

root = tk.Tk()
root.title(f'健康上网{version}')
root.geometry('662x400')
root.configure(bg='white')
root.resizable(False, False)
root.iconphoto(False, tk.PhotoImage(file='icon.png'))
root.lift()

lab1_var = tk.StringVar()
lab1_var.set('None')

lab1 = tk.Label(root, textvariable=lab1_var, font=('微软雅黑', 14), fg="#000000", bg='white')
lab1.place(x=331, y=175, anchor='center')

bto1 = tk.Button(root,bd=2,height=1,width=15,font='微软雅黑',bg='grey',fg='white',text='历史',command=lambda : password(1))
bto1.place(x=557, y=35, anchor='center')
bto4 = tk.Button(root,bd=2,height=1,width=15,font='微软雅黑',bg='grey',fg='white',text='设置',command=lambda : password(2))
bto4.place(x=105, y=35, anchor='center')
bto_cc = tk.Button(root,bd=2,height=1,width=15,font='微软雅黑',bg='grey',fg='white',text='定时关机',command=lambda : password(3))
bto_cc.place(x=105, y=365, anchor='center')
bto_ssw = tk.Button(root,bd=2,height=1,width=15,font='微软雅黑',bg='grey',fg='white',text='截屏预览',command=lambda : password(4))
bto_ssw.place(x=557, y=365, anchor='center')

icon = oIcon(root)
icon.tray_icon.run_detached()

root.protocol('WM_DELETE_WINDOW', if_quit)

if os.path.exists("config.json"):
    config_read_json_encryption()  #仅启动时读取config
else:
    config_write_json_encryption()

for key in default_config:  #校验config完整性与正确性
    if key not in config:
        config[key] = default_config[key]
        config_write_json_encryption()
    elif type(config[key]) != type(default_config[key]):
        config[key] = default_config[key]
        config_write_json_encryption()


time_update_init()
time_update()
screenshoter_init()
get_screen()

if os.path.exists(".\\monitor"):
    with open(".\\monitor", "r") as file:
        text = file.read().strip()
        if text and text[0] == 'a':
            default_hide = True

run_timer()

if_first_run = False

if default_hide:
    root.withdraw()

root.mainloop()