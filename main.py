import tkinter as tk
import screenshot
import moretk
from datetime import datetime
import time
from PIL import Image
from pystray import Icon, MenuItem, Menu
import os
import json        #导入必要库

version = "beta-v0.0.9"
if_first_run = True
if_quit_judge = -1
time_date = "0"
total_time = 0
ss_address = R".\screenshot"
ss_max_amount = 100
ss_quality = 1
ss_shotgap = 30*1000
default_password = "1"
default_config = {'ss_address':R'.\screenshot', 'ss_max_amount': 100, 'ss_quality': 1, 'ss_shotgap': 30*1000, 'if_quit_judge': -1}
default_hide = False
now = datetime.now()
time_date = int(now.strftime('%Y%m%d'))
history = {}
if_cc_conduct = False
cc_timer = None

class oIcon:
    def __init__(self, master):
        self.master = master

        self.icon_image = Image.open("icon.png")
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

def run_timer():
    with open("monitor", "w") as file:
        file.write("b"+str(time.time()))
    root.after(10000,run_timer)

def load_history_json():   #读取或创建本地历史文件，将结果保存为字典history
    global history, time_date
    if os.path.exists('history.json'):
        try:
            with open('history.json', 'r') as file:
                history_c = json.load(file)
                for k, v in history_c.items():
                    history[int(k)] = v
        except Exception as e:
            print("读取 history.json 出错:", e)
            history[time_date] = "0"
    else:
        with open('history.json', 'w', newline='') as file:
            hty_n = {}
            hty_n[time_date] = "0"
            json.dump(hty_n, file, indent=4)
        history = {}
        history[time_date] = "0"

def history_write_json():  #将history以json格式写入本地
    with open('history.json', 'w', newline='') as file:
        json.dump(history, file, indent=4)

def check_history():
    global time_date
    if not time_date in history:
        history[time_date] = "0"

def time_update_init():
    global total_time, time_date
    load_history_json()
    check_history()
    total_time = int(history[time_date])

def time_update():
    global total_time, time_date
    if not if_first_run:
        total_time += 5
    history[time_date] = str(total_time)
    history_write_json()
    gap_hour = total_time // 3600
    gap_min = total_time % 3600 // 60
    gap_sec = total_time % 60
    lab1_var.set('您今日已累计使用电脑%d小时，%d分钟，%d秒' %(gap_hour, gap_min, gap_sec))
    root.after(5000, time_update)

def history_check():   #用于图形界面查询历史
    global history, time_date
    
    root2 = tk.Toplevel()
    root2.title('使用历史')
    root2.geometry('662x400')
    root2.configure(bg='white')
    root2.resizable(False, False)
    hty_key = {}

    def htylist_refresh(if_circulate):  #对查询界面5秒一刷新
        nonlocal hty_key
        htylist.delete(0,tk.END)
        hty_key = {}
        htylist_insert()
        if if_circulate:
            root2.after(5000, lambda: htylist_refresh(True))
        else:
            pass
    
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
        history_write_json()
        htylist_refresh(0)

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
    
    bto2 = tk.Button(root2,bd=2,height=1,width=10,font='微软雅黑',bg='grey',fg='white',text='删除',command=htylist_delete)
    bto2.pack(side='bottom', pady= 50)

    htylist = tk.Listbox(root2, yscrollcommand=sb.set, width= 662, height= 10, font=('微软雅黑', 14))    
    
    htylist_refresh(1)
    
    htylist.pack()

def if_quit():  #询问推出选项
    def quit_straight():  #选择直接退出
        global if_quit_judge
        if qiw_cb_var.get():  #选了不再提问，则储存至config
            if_quit_judge = 1
            config['if_quit_judge'] = 1
            config_write_json()
        password(0)
        n.destroy()

    def window_hide():  #选择最小化
        global if_quit_judge
        if qiw_cb_var.get():  #选了不再提问，则储存至config
            if_quit_judge = 0
            config['if_quit_judge'] = 0
            config_write_json()
        for widget in root.winfo_children():  #清理所有打开的界面
                if isinstance(widget, tk.Toplevel):
                    widget.destroy()
        root.withdraw()
        n.destroy()

    if if_quit_judge == -1:   #如果没选过不再提问，或者后续取消不在提问，则问这个问题
        quit_inquire_window = n = tk.Toplevel(root)
        n.title('退出选项')
        n.geometry('300x170')
        n.configure(bg='white')
        n.resizable(False, False)

        qiw_cb_var = tk.BooleanVar()
        qiw_cb = tk.Checkbutton(n, text="下次不再提问", font=("微软雅黑", 10), bg="white", variable=qiw_cb_var)
        qiw_cb.deselect()
        qiw_cb.pack(pady=5)

        qiw_bto_1 = tk.Button(n,bd=2,height=1,width=10,font='微软雅黑',bg='grey',fg='white',text='直接退出',command=quit_straight)
        qiw_bto_2 = tk.Button(n,bd=2,height=1,width=10,font='微软雅黑',bg='grey',fg='white',text='最小化',command=window_hide)
        qiw_bto_1.pack(pady=5)
        qiw_bto_2.pack(pady=5)
    
    else:
        if if_quit_judge:
            password(0)
        else:
            for widget in root.winfo_children():
                if isinstance(widget, tk.Toplevel):
                    widget.destroy()
            root.withdraw()

def password(event_f):  # 用于密码确认
    global default_password, root
    
    def password_check():  # 确认密码是否正确，如果是则执行对应操作
        try:
            if shur1.get() == default_password:
                if event_f == 0:
                    if not(if_quit_judge):
                        icon.tray_icon.stop()
                    with open("monitor") as file:
                        file.write("d")
                    root3.destroy()
                    icon.tray_icon.stop()
                    root.destroy()
                elif event_f == 1:
                    history_check()
                    root3.destroy()
                elif event_f == 2:
                    ss_window()
                    root3.destroy()
                elif event_f ==3:
                    cc_window()
                    root3.destroy()
            elif shur1.get() == 'admin':
                print('admin')
            else:
                kww.show()
        except Exception as e:
            print("错误：", e)

    kww = moretk.KeyWrong()  # 用于生成密码错误界面，默认隐藏
    
    root3 = tk.Toplevel(root)
    root3.title('输入密码')
    root3.geometry('400x100')
    root3.configure(bg='white')
    root3.resizable(False, False)

    shur1 = tk.Entry(root3, width=15, font=('微软雅黑', 16), fg='black', borderwidth=1, justify='left')
    shur1.bind("<Return>", lambda event : password_check())
    shur1.pack(side='top', pady=10)

    bto3 = tk.Button(root3, bd=2, height=1, width=10, font='微软雅黑', bg='grey', fg='white',text='确认', command=password_check)
    bto3.pack(side='bottom', pady=10)

def config_read_json(): #用于读取配置文件
    global config, ss_address, ss_max_amount, ss_quality, ss_shotgap, if_quit_judge
    if os.path.exists('config.json'): #读取本地config
        try:
            with open('config.json', 'r') as file:
                config = json.load(file)
        except Exception as e:
            print("读取 'config.json' 出错:", e)
            config = default_config
    else: #本地配置文件初始化
        with open('config.json', 'w', newline='') as file:
            config = default_config
            json.dump(config, file, indent=4)
    try:
        ss_address = config['ss_address']
        ss_max_amount = config['ss_max_amount']
        ss_quality = config['ss_quality']
        ss_shotgap = config['ss_shotgap']  
        if_quit_judge = config['if_quit_judge'] #从config中获取并定义变量
    except:
        config = default_config

def get_screen_init():
    global screenshoter
    config_read_json()  #仅启动时读取config
    screenshoter = screenshot.Screenshoter(ss_address, ss_max_amount, ss_quality)

def get_screen():  #主程序中使用截屏
    screenshoter.screenshot()
    screenshoter.picture_clean()
    root.after(ss_shotgap, get_screen)

def config_write_json():  #用于将config中数值以json格式写入本地
        if os.path.exists('config.json'):
            try:
                with open('config.json', 'w', newline='') as file:
                    json.dump(config, file, indent=4)

            except Exception as e:
                print("写入 'config.json' 出错:", e)
        else:
            with open('config.json', 'w', newline='') as file:
                config_n = default_config
                json.dump(config_n, file, indent=4)  #如果文件不存在的话就创建一个默认文件再写入一次
                config_write_json()


def ss_window():  #显示截屏配置界面
    def config_save():  #用于关闭时将修改后的数值写入config
        config['ss_address'] = ss_ads_pic.address_get()
        config['ss_max_amount'] = ss_cbb_ma_list_r[ss_cbb_ma.current()]
        config['ss_quality'] = ss_cbb_qty_list_r[ss_cbb_qty.current()]
        config['ss_shotgap'] = ss_cbb_gap_list_r[ss_cbb_gap.current()]
        if ss_quitway_cb_1_var.get():
            config['if_quit_judge'] = 1
        elif ss_quitway_cb_2_var.get():
            config['if_quit_judge'] = 0
        else:
            config['if_quit_judge'] = -1

    def if_save():  #确认保存界面
        if if_change:
            root6 = tk.Toplevel(root5)
            root6.title('是否保存')
            root6.geometry('400x150')
            root6.configure(bg='white')
            root6.resizable(False, False)

            lab_is = tk.Label(root6, text='是否保存', font=('微软雅黑', 20), fg="#000000", bg='white')
            lab_is.pack(side='top', pady=20)

            bto_is_y = tk.Button(root6,bd=2,height=1,width=6,font=('微软雅黑', 13),bg='grey',fg='white',text='保存',command=lambda : (config_save(), config_write_json(), config_read_json(), root6.destroy(), root5.destroy()))
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

    ss_cbb_qty_list_r = [1, 2, 4]
    ss_cbb_qty_list = ['1倍质量', '2倍质量', '4倍质量']
    ss_cbb_qty = moretk.TextComboBox(root5, text="图片质量", font_l=('微软雅黑', 14), font_c=('微软雅黑', 12), bg="white", values=ss_cbb_qty_list)
    ss_cbb_qty.current(next(i for i, v in enumerate(ss_cbb_qty_list_r) if v == config["ss_quality"]))
    ss_cbb_qty.pack(pady=10)

    ss_ads_pic = moretk.AddressInputBox(root5, text="截屏保存路径", font_a=('微软雅黑', 10), font_r=('微软雅黑', 14), default_address=ss_address, bg="white")
    ss_ads_pic.pack(pady=10)

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
    ss_bto_y = tk.Button(ss_bto_frame,bd=2,height=1,width=10,font='微软雅黑',bg='grey',fg='white',text='保存',command=lambda : (config_save(), config_write_json(), config_read_json(), root5.destroy()))
    ss_bto_n = tk.Button(ss_bto_frame,bd=2,height=1,width=10,font='微软雅黑',bg='grey',fg='white',text='取消',command=root5.destroy)
    ss_bto_y.pack(side="left", padx=5)
    ss_bto_n.pack(side="right", padx=5)
    ss_bto_frame.pack(pady=10)

    tp = moretk.ToolTip(ss_ads_pic, text=ss_address)

    ss_cbb_gap.bind("<Button-1>",lambda event : change())  #用于确认是否发生修改
    ss_cbb_ma.bind("<Button-1>", lambda event : change())
    ss_cbb_qty.bind("<Button-1>", lambda event : change())
    ss_ads_pic.bind("<AddressChange>", lambda event : change())
    ss_quitway_cb_1.bind("<Button-1>",lambda event : change())
    ss_quitway_cb_2.bind("<Button-1>",lambda event : change())

    root5.protocol('WM_DELETE_WINDOW', if_save)  #关闭时显示是否保存界面（若发生修改）

def cc_window():
    def cfm():
        cfmw.show()
        cch_result = cch.get_selected()
        ccm_result = ccm.get_selected()
        tv.set("是否确认%d小时%d分钟后关机？"%(cch_result, ccm_result))
        
    def on_confirm():
        global if_cc_conduct, cc_timer
        cch_result = cch.get_selected()
        ccm_result = ccm.get_selected()
        if_cc_conduct = True
        cc_timer = moretk.Timer(root, cch_result*3600+ccm_result*60, on_cclose)
        window_cc.destroy()

    def cancel_cc_cfm():
        ccc_cfmw = moretk.CfmWindow(window_ccc, text = "确认取消电脑定时关机？", font_b='微软雅黑', font_l='微软雅黑', on_cancel=lambda : ccc_cfmw.withdraw(), on_confirm=cancel_cc)
        ccc_cfmw.show()

    def cancel_cc():
        global if_cc_conduct
        cc_timer.cancel()
        if_cc_conduct = False
        window_ccc.destroy()

    def on_cclose():
        def shutdown():
            global if_cc_conduct
            if_cc_conduct = False
            os.system("shutdown /s /t 1")
        shutdownreminder = n =tk.Toplevel(root)

        n.title('错误')
        n.geometry('400x100')
        n.configure(bg='white')
        n.resizable(False, False)

        nlabel = tk.Label(n, text='电脑将于一分钟后关机，请及时保存文件！',font=('微软雅黑', 14),fg="#000000", bg='white')
        nlabel.pack(pady=30)

        root.after(60000, shutdown)

    if not if_cc_conduct:
        window_ccc = None
        window_cc = tk.Toplevel(root)
        window_cc.title('定时关机设置')
        window_cc.geometry('300x350')
        window_cc.configure(bg='white')
        window_cc.resizable(False, False)

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
    
    else:
        window_cc = None
        window_ccc = tk.Toplevel(root)
        window_ccc.title('正在为关机计时')
        window_ccc.geometry('300x220')
        window_ccc.configure(bg='white')
        window_ccc.resizable(False, False)

        frame_cc = tk.Frame(window_ccc, bg='white')
        frame_cc.pack(side="top", pady=5)

        label_line1 = tk.Label(frame_cc, text="电脑将于", font=('微软雅黑', 14), fg="#000000", bg='white')
        label_line1.pack(pady=5)

        frame_line2 = tk.Frame(frame_cc, bg='white')
        frame_line2.pack(pady=5)

        label_line2 = tk.Label(frame_line2, textvariable=cc_timer.timevar_f, font=('微软雅黑', 20, 'bold'), fg="#FF0000", bg='white')
        label_line2.pack(side='left')

        label_after = tk.Label(frame_line2, text="后", font=('微软雅黑', 20, 'bold'), fg="#FF0000", bg='white')
        label_after.pack(side='left')

        label_line3 = tk.Label(frame_cc, text="关机", font=('微软雅黑', 14), fg="#000000", bg='white')
        label_line3.pack(pady=5)

        bto_cancel_cc = tk.Button(window_ccc,bd=2,height=1,width=10,font='微软雅黑',bg='grey',fg='white',text='取消关机', command=cancel_cc_cfm)
        bto_cancel_cc.pack(pady=5)

root = tk.Tk()
root.title(f'健康上网{version}')
root.geometry('662x400')
root.configure(bg='white')
root.resizable(False, False)

lab1_var = tk.StringVar()
lab1_var.set('None')

lab1 = tk.Label(root, textvariable=lab1_var, font=('微软雅黑', 14), fg="#000000", bg='white')
lab1.place(x=331, y=175, anchor='center')

bto1 = tk.Button(root,bd=2,height=1,width=15,font='微软雅黑',bg='grey',fg='white',text='历史',command=lambda : password(1))
bto1.place(x=562, y=30, anchor='center')
bto4 = tk.Button(root,bd=2,height=1,width=15,font='微软雅黑',bg='grey',fg='white',text='设置',command=lambda : password(2))
bto4.place(x=100, y=30, anchor='center')
bto_cc = tk.Button(root,bd=2,height=1,width=15,font='微软雅黑',bg='grey',fg='white',text='定时关机',command=lambda : password(3))
bto_cc.place(x=100, y=370, anchor='center')

icon = oIcon(root)
icon.tray_icon.run_detached()

root.protocol('WM_DELETE_WINDOW', if_quit)

time_update_init()
time_update()
get_screen_init()
get_screen()
run_timer()

if_first_run = False

if default_hide:
    root.withdraw()

root.mainloop()