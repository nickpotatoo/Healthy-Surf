import os
import math
import datetime
from PIL import ImageGrab

class Screenshoter:
    def __init__(self, path:str, max_amount:int, quality:int):
        self.picture_list = []
        self.picture_cache = None
        self.path = path
        self.max_amount = max_amount
        self.quality = quality

        if not os.path.exists(self.path):  # 初始化，创建文件夹
            os.mkdir(self.path)

    def screenshot(self):  # 截屏
        now = datetime.datetime.now()
        time = now.strftime('%Y%m%d%H%M%S')
        try:
            self.image = ImageGrab.grab()
            self.image = self.image.resize(self._picture_quality_deal())
            self.image.save('%s\\hssp_%s.png' % (self.path, time))
            self.picture_cache = '%s.png' % time
            return True
        except Exception as e:
            print('截图失败:', e)
            return False

    def _picture_quality_deal(self):  # 用于计算图像处理质量
        def is_prime(n):  # 判断数字是否为质数，返回布尔值
            if n <= 1:
                return False
            sqrt_n = math.isqrt(n)
            for i in range(2, sqrt_n + 1):
                if n % i == 0:
                    return False
            return True

        a, b = self.image.size  # 获取照片尺寸
        while a % 2 == 0 and b % 2 == 0:  # 将两个尺寸化简到出现奇数
            a = int(a / 2)
            b = int(b / 2)
        while not (is_prime(a) or is_prime(b)):  # 再将两个尺寸化简直到其中出现两个数字为互质数
            if a >= b:  # 获取最大的数
                m = a
            else:
                m = b
            sqrt_n2 = math.isqrt(m)  # 将最大的数开方
            t = 2
            n = 0
            for i in range(2, sqrt_n2 + 1):  # 与判断是否为质数逻辑相似，获取较大的数所有可能的因数，并依次判断是否同时为a与b的因数
                if a % i == 0 and b % i == 0:
                    a = int(a / i)
                    b = int(b / i)
                    break  # 若找到，则化简ab并进行下一次化简
                t += 1  # 用于计算尝试次数，若已尝试所有可能，说明ab互质，将n设为一，跳出化简，返回处理后的ab
                if t == int(sqrt_n2 + 1):
                    n = 1
                    break
            if n == 1:  # 若n为1则跳出循环
                break
        a = int(a * 20 * self.quality)
        b = int(b * 20 * self.quality)
        return a, b

    def picture_clean(self):  # 计算并删除多余图片
        i = 0
        self.picture_list = []
        for n in os.listdir(self.path):
            if n[:5] == 'hssp_':
                self.picture_list.append(n)
        self.picture_list.sort()
        i = len(self.picture_list)
        while i >= self.max_amount + 1:
            os.remove('%s\\%s' % (self.path, self.picture_list[0]))
            self.picture_list.remove(self.picture_list[0])
            i -= 1
        return i
    
if __name__ == "__main__":

    import time

    def test_screenshoter():
        # 指定保存路径（当前目录下的 screenshot 文件夹）
        save_path = "screenshot"
        max_pics = 3     # 最多保留 3 张
        quality = 1     # 图像缩放质量倍数

        # 创建对象
        shooter = Screenshoter(save_path, max_pics, quality)

        # 连续截图 5 次，每次间隔 1 秒
        for i in range(5):
            print(f"\n开始第 {i+1} 次截图...")
            success = shooter.screenshot()
            shooter.picture_clean()
            if success:
                print("截图成功:", shooter.picture_cache)
            else:
                print("截图失败")
            shooter.picture_clean()
            print("当前保留的截图数量:", len(shooter.picture_list))
            time.sleep(1)
            
    test_screenshoter()