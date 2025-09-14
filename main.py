import tkinter as tk
import screen_print
import moretk
from datetime import datetime
from tkinter import ttk
from tkinter import filedialog
from tkinter import font as tkfont
import os
import json        #导入必要库

version = 'beta-v0.0.7'
time_gap = 0  #该变量用于记录当天的使用时间
org_time = 0
org_time_date = 0
address = R'.\screen'
max_amount = 100
qty = 1
p_gap = 30*1000
passwordkey = '1'
if_first_load = 0
now = datetime.now()
time_date = int(now.strftime('%Y%m%d'))
history = {}    

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
            history[time_date] = '0#0#0#0'
    else:
        with open('history.json', 'w', newline='') as file:
            hty_n = {}
            hty_n[time_date] = "0#0#0#0"
            json.dump(hty_n, file, indent=4)
        history = {}
        history[time_date] = '0#0#0#0'

def update_time(if_circulate):  #计算当日使用时长，并写入本地，5秒循环
    global org_time, time_gap
    now = datetime.now()
    time_date = int(now.strftime('%Y%m%d'))
    time_hour = int(now.strftime('%H'))
    time_min = int(now.strftime('%M'))
    time_second = int(now.strftime('%S'))
    now_time = time_hour * 3600 + time_min * 60 + time_second
    time_gap += now_time - org_time
    org_time = now_time
    gap_hour, gap_min, gap_second = time_calculate(time_gap)
    lab1_var.set('您今日已累计使用电脑%d小时，%d分钟，%d秒' %(gap_hour, gap_min, gap_second))
    history[time_date] = '%d#%d#%d#%d'%(gap_hour, gap_min, gap_second, time_gap)
    history_write_json()
    print(history)
    if if_circulate == 1:
        root.after(5000, lambda : update_time(1))
    else:
        pass

def time_calculate(time_gap_f): #负责将输入的time_gap计算为对应的准确时间
    gap_hour = time_gap_f//3600
    gap_min = (time_gap_f - gap_hour*3600)//60
    gap_second = time_gap_f - gap_hour*3600 - gap_min*60
    return gap_hour, gap_min, gap_second

def set_time(): #初始化org_time
    global org_time
    now = datetime.now()
    time_hour = int(now.strftime('%H'))
    time_min = int(now.strftime('%M'))
    time_second = int(now.strftime('%S'))
    org_time = time_hour * 3600 + time_min * 60 + time_second

def cfm_time(if_circulate): #确认现在是否跨天，来决定是否初始化,同时也用于重新读取本地历史
    global time_gap, time_date, org_time_date
    if org_time_date != time_date:
        set_time()
        org_time_date = time_date
        time_gap = 0
    else:
        history_read()
        set_time()
    if if_circulate == 1:
        root.after(3600*1000, lambda : cfm_time(1))
    else:
        pass

def history_write_json():  #将history以json格式写入本地
    with open('history.json', 'w', newline='') as file:
        json.dump(history, file, indent=4)

def history_read():   #将time_gap设定为当天的历史值
    global time_gap, time_date
    time_gap = get_time_gap(time_date)

def get_time_gap(keys):  #读取并返回对应天数的本地记录的历史的time_gap
    global history
    get_history = history[keys]
    positions = [i for i, letter in enumerate(get_history) if letter == '#']
    position = positions[2]
    time_gap_f = int(get_history[(position + 1):])
    return time_gap_f

def history_read_date():  #将org_time_date设置为本地记录的最后一天
    global org_time_date
    last_key = next(reversed(history))
    org_time_date = last_key

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
        if if_circulate == 1:
            root2.after(5000, lambda: htylist_refresh(1))
        else:
            pass
    
    def htylist_delete():  #删除选中的本地历史并初始化
        global history, time_date
        nonlocal hty_key
        n, *args = htylist.curselection()
        key_f = hty_key[n]
        if key_f != time_date:
            del history[key_f]
        else:
            history[key_f] = '0#0#0#0'
        history_write_json()
        load_history_json()
        cfm_time(0)
        htylist_refresh(0)
        update_time(0)

    def htylist_insert():  #将历史写入查询界面
        global history
        nonlocal hty_key
        i=0
        for key in history:
            time_gap_f = get_time_gap(key)
            gap_hour, gap_min, gap_second = time_calculate(time_gap_f)
            v = '%s:%d小时%d分钟%d秒'%(key, gap_hour, gap_min, gap_second)
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

def password(event_f):  # 用于密码确认
    global passwordkey, root
    
    def password_check():  # 确认密码是否正确，如果是则执行对应操作
        try:
            if shur1.get() == passwordkey:
                if event_f == 0:
                    root.destroy()
                    root3.destroy()
                elif event_f == 1:
                    history_check()
                    root3.destroy()
                elif event_f == 2:
                    sp_window()
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

def config_read(): #用于读取配置文件
    global config, address, max_amount, qty, p_gap
    if os.path.exists('config.txt'): #读取本地config
        try:
            with open('config.txt', 'r') as file:
                config = eval(file.read())
        except Exception as e:
            print("读取 'config.txt' 出错:", e)
    else: #本地配置文件初始化
        with open('config.txt', 'w') as file:
            file.write(R"{'address':R'.\screen', 'max_amount': 100, 'qty': 1, 'p_gap': 30*1000}")
            config = {'address':R'.\screen', 'max_amount': 100, 'qty': 1, 'p_gap': 30*1000}
    address = config['address']
    max_amount = config['max_amount']
    qty = config['qty']
    p_gap = config['p_gap']  #从config中获取并定义变量

def get_screen():  #主程序中使用截屏
    global if_first_load
    if not if_first_load:    #仅启动时读取config
        config_read()
        if_first_load = 1
    else:
        pass
    screen_print.screen_print(address, max_amount, qty)
    root.after(p_gap, get_screen)

def sp_window():
    def sp_config_write():  #用于将config中数值写入本地
        if os.path.exists('config.txt'):
            try:
                with open('config.txt', 'w') as file:
                    r1 = config['p_gap']
                    r2 = config['max_amount']
                    r3 = config['qty']
                    r4 = config['address']
                    file.write(R"{'address':R'%s', 'max_amount': %d, 'qty': %d, 'p_gap': %d}"%(r4, r2, r3, r1))
            except Exception as e:
                print("写入 'config.txt' 出错:", e)
        else:
            with open('config.txt', 'w') as file:
                file.write(R"{'address':R'.\screen', 'max_amount': 100, 'qty': 1, 'p_gap': 30*1000}")  #如果文件不存在的话就创建一个默认文件再写入一次
                sp_config_write()

    def sp_config_save():  #用于关闭时将修改后的数值写入config
        config['address'] = address_cache
        config['max_amount'] = cbb_sp_ma_list_r[cbb_sp_ma.current()]
        config['qty'] = cbb_sp_qy_list_r[cbb_sp_qy.current()]
        config['p_gap'] = cbb_sp_gap_list_r[cbb_sp_gap.current()]

    def if_save():  #确认保存界面
        if if_change:
            root6 = tk.Toplevel(root5)
            root6.title('是否保存')
            root6.geometry('400x150')
            root6.configure(bg='white')
            root6.resizable(False, False)

            lab_is = tk.Label(root6, text='是否保存', font=('微软雅黑', 20), fg="#000000", bg='white')
            lab_is.pack(side='top', pady=20)

            bto_is_y = tk.Button(root6,bd=2,height=1,width=6,font=('微软雅黑', 13),bg='grey',fg='white',text='保存',command=lambda : (sp_config_save(), sp_config_write(), config_read(), root6.destroy(), root5.destroy()))
            bto_is_n = tk.Button(root6,bd=2,height=1,width=6,font=('微软雅黑', 13),bg='grey',fg='white',text='取消',command=lambda : (root6.destroy(), root5.destroy()))
            bto_is_y.pack(side='left', padx=60)
            bto_is_n.pack(side='right', padx=60)
        else:
            root5.destroy()

    def font_width_deal(address_f):  #用于计算地址长度是否过长，若过长，则返回截短后加上省略号的地址
        nonlocal lab_sp_address
        address_c = address_f
        address_font = tkfont.Font(family='微软雅黑', size=11)
        #print(address_font.measure(address_c), lab_sp_address.winfo_width())
        if address_font.measure(address_c) <= lab_sp_address.winfo_width():
            return address_f
        else:
            address_f = ''
            for v in address_c:
                if address_font.measure(address_f + v + '...') > lab_sp_address.winfo_width() - 10:
                    break
                address_f += v
            address_f += '...'
            return address_f
        
    def bto_sp_adsc_event():  #用于询问获取保存路径，并刷新路径地址
        nonlocal address_cache, lab_sp_address_var
        save_path = filedialog.askdirectory()
        print(save_path)
        if save_path:
            address_cache = save_path
            lab_sp_address_var.set(font_width_deal(address_cache))
        else:
            pass
    
    def change():
        nonlocal if_change
        if_change = True
    
    if_change = False

    root5 = tk.Toplevel(root)
    root5.title('截屏设置')
    root5.geometry('600x300')
    root5.configure(bg='white')
    root5.resizable(False, False)

    cav_sp = tk.Canvas(root5, width=662, height=400, bg='white')
    cav_sp.pack()

    lab_sp_gap = tk.Label(root5, text='截屏间隔', font=('微软雅黑', 14), fg="#000000", bg='white')
    cav_sp.create_window(200, 50, window=lab_sp_gap)
    cbb_sp_gap_list_r = [5*1000, 30*1000, 60*1000, 5*60*1000, 15*60*1000]
    cbb_sp_gap_list = ['5秒', '30秒', '1分钟', '5分钟', '15分钟']
    cbb_sp_gap = ttk.Combobox(root5, font=('微软雅黑', 14), values=cbb_sp_gap_list, width=10)
    cbb_sp_gap.current(next(i for i, v in enumerate(cbb_sp_gap_list_r) if v == config['p_gap']))
    cav_sp.create_window(350, 50, window=cbb_sp_gap)
    
    lab_sp_ma = tk.Label(root5, text='最大保存数量', font=('微软雅黑', 14), fg="#000000", bg='white')
    cav_sp.create_window(200, 90, window=lab_sp_ma)
    cbb_sp_ma_list_r = [5, 50, 100, 1000]
    cbb_sp_ma_list = ['5张', '50张', '100张', '1000张']
    cbb_sp_ma = ttk.Combobox(root5, font=('微软雅黑', 14), values=cbb_sp_ma_list, width=10)
    cbb_sp_ma.current(next(i for i, v in enumerate(cbb_sp_ma_list_r) if v == config['max_amount']))
    cav_sp.create_window(350, 90, window=cbb_sp_ma)

    lab_sp_qy = tk.Label(root5, text='图片质量', font=('微软雅黑', 14), fg="#000000", bg='white')
    cav_sp.create_window(200, 130, window=lab_sp_qy)
    cbb_sp_qy_list_r = [1, 2, 4]
    cbb_sp_qy_list = ['1倍质量', '2倍质量', '4倍质量']
    cbb_sp_qy = ttk.Combobox(root5, font=('微软雅黑', 14), values=cbb_sp_qy_list, width=10)
    cbb_sp_qy.current(next(i for i, v in enumerate(cbb_sp_qy_list_r) if v == config['qty']))
    cav_sp.create_window(350, 130, window=cbb_sp_qy)

    lab_sp_fd = tk.Label(root5, text='保存路径', font=('微软雅黑', 14), fg="#000000", bg='white')
    cav_sp.create_window(300, 170, window=lab_sp_fd)
    lab_sp_address_var = tk.StringVar()
    lab_sp_address_var.set('None')
    lab_sp_address = tk.Label(root5, textvariable=lab_sp_address_var, font=('微软雅黑', 11), fg="#000000", bg='white', relief='solid', borderwidth=0.5, width=50, anchor='w')
    cav_sp.create_window(300, 200, window=lab_sp_address)
    address_cache = address
    lab_sp_address.bind("<Configure>", lambda event : lab_sp_address_var.set(font_width_deal(address_cache)))

    bto_sp_adsc = tk.Button(root5,bd=1,height=1,width=2,font=('微软雅黑', 9),bg='grey',fg='white',text='▼',command=lambda : (bto_sp_adsc_event(), change()))
    cav_sp.create_window(538, 200, window=bto_sp_adsc)

    tp = moretk.ToolTip(lab_sp_address, text=address_cache)

    cbb_sp_gap.bind("<Button-1>",lambda event : change())
    cbb_sp_qy.bind("<Button-1>", lambda event : change())
    cbb_sp_ma.bind("<Button-1>", lambda event : change())

    root5.protocol('WM_DELETE_WINDOW', if_save)
    
root = tk.Tk()
root.title(f'健康上网{version}')
root.geometry('662x400')
root.configure(bg='white')
root.resizable(False, False)

lab1_var = tk.StringVar()
lab1_var.set('None')

cav1 = tk.Canvas(root, width=662, height=400, bg='white')
cav1.pack()

lab1 = tk.Label(root, textvariable=lab1_var, font=('微软雅黑', 14), fg="#000000", bg='white')
cav1.create_window(331, 175, window=lab1)

bto1 = tk.Button(root,bd=2,height=1,width=10,font='微软雅黑',bg='grey',fg='white',text='历史',command=lambda : password(1))
cav1.create_window(592,30,window=bto1)
bto4 = tk.Button(root,bd=2,height=1,width=15,font='微软雅黑',bg='grey',fg='white',text='定时截屏',command=lambda : password(2))
cav1.create_window(100,30,window=bto4)

root.protocol('WM_DELETE_WINDOW', lambda : password(0))

load_history_json()
history_read_date()
cfm_time(1)
update_time(1)
get_screen()

root.mainloop()