from PIL import ImageGrab
import math
import datetime
import os

picture_list = []

def sp_init(address_f): #初始化，创建文件夹
    if os.path.exists(address_f):
        pass
    else:
        os.mkdir(address_f)

def screen_print_main(address_f, qty_f):  #截屏主程序
    global pic_cache
    now = datetime.datetime.now()
    t = now.strftime('%Y%m%d%H%M%S')
    try:
        im = ImageGrab.grab()
        im = im.resize(pic_quantity(im, qty_f))
        im.save('%s\\hssp_%s.png'%(address_f, t))
        pic_cache = '%s.png'%t
        return True
    except Exception as e:
        print('截图失败:',e)
        return False

def pic_quantity(im_f, q):  #用于计算图像处理质量
    def is_prime(n): #判断数字是否为质数，返回布尔值
        if n <= 1:
            return False
        sqrt_n = math.isqrt(n)
        for i in range(2, sqrt_n + 1):
            if n % i == 0:
                return False
        return True
    a, b = im_f.size #获取输入照片尺寸
    while a%2 == 0 and b%2 == 0: #将两个尺寸化简到出现奇数
        a = int(a/2)
        b = int(b/2)
    while not(is_prime(a) or is_prime(b)): #再将两个尺寸化简直到其中出现两个数字为互质数
        if a>=b:  #获取最大的数
            m = a
        else:
            m = b
        sqrt_n2 = math.isqrt(m)  #将最大的数开方
        t = 2
        n = 0
        for i in range(2, sqrt_n2 + 1):  #与判断是否为质数逻辑相似，获取较大的数所有可能的因数，并依次判断是否同时为a与b的因数
            if a % i == 0 and b % i == 0:
                a = int(a/i)
                b = int(b/i)
                break  #若找到，则化简ab并进行下一次化简
            t += 1  #用于计算尝试次数，若已尝试所有可能，说明ab互质，将n设为一，跳出化简，返回处理后的ab
            if t == int(sqrt_n2 + 1):
                n = 1
                break
        if n == 1:  #若n为1则跳出循环
            break
    a = int(a*20*q)
    b = int(b*20*q)
    return a, b

def picture_count(address_f, max_amount_f):  #计算并删除多余图片
    global picture_list
    i=0
    picture_list = []
    for n in os.listdir(address_f):
        if n[:5] == 'hssp_':
            picture_list.append(n)
    for p in picture_list:
        i += 1
    while i >= max_amount_f + 1:
        os.remove('%s\\%s'%(address_f, picture_list[0]))
        picture_list.remove(picture_list[0])
        i -= 1
    return i

def screen_print(address_f, max_amount_f, qty_f):
    sp_init(address_f)
    screen_print_main(address_f, qty_f)
    picture_count(address_f, max_amount_f)

if __name__ == "__main__":
    max_amount = 10
    address = '.\\screen'
    qty = 1

    sp_init(address)
    screen_print_main(address, qty)
    picture_count(address, max_amount)