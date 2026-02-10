import os
import math
import datetime
from PIL import ImageGrab

class Screenshot:
    """截屏类，负责截屏，提供接口供ScreenShoter调用，并管理图片质量处理和图片清理"""
    def __init__(self, path:str, max_amount:int, quality:int):
        self.picture_list = []
        self.picture_cache = None
        self.path = path
        self.max_amount = max_amount
        self.quality = quality

        if not os.path.exists(self.path):  # 初始化，创建文件夹
            os.mkdir(self.path)

    def shot(self):  # 截屏
        now = datetime.datetime.now()
        time = now.strftime('%Y%m%d%H%M%S')
        try:
            self.image = ImageGrab.grab()
            self.image = self.image.resize(self._picture_quality_deal())
            self.image.save('%s\\hssp_%s.jpg' % (self.path, time))
            self.picture_cache = '%s.jpg' % time
            return True
        except Exception as e:
            print('截图失败:', e)
            return False

    def _picture_quality_deal(self):
        a, b = self.image.size

        # 不断用最大公约数约分，直到互质
        g = math.gcd(a, b)
        while g > 1:
            a //= g
            b //= g
            g = math.gcd(a, b)

        # 按原逻辑放大
        a = int(a * 20 * self.quality)
        b = int(b * 20 * self.quality)

        return a, b

    def clean(self):  # 计算并删除多余图片
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
    
class ScreenShoter:
    """截屏器类，单例化，负责管理截屏器对象，提供接口供主程序调用，并管理配置更新和截屏循环"""
    _instance = None

    def __new__(cls, *args, **kwargs):
        """单例化"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, master, path:str, max_amount:int, quality:int, shotgap:int):
        """初始化"""
        self._master = master
        self.path = path
        self.max_amount = max_amount
        self.quality = quality
        self.shotgap = shotgap
        self._screenshot_timer = None

        self._screenshot = Screenshot(path=self.path, max_amount=self.max_amount, quality=self.quality)

    def start(self):
        """开始截屏循环"""
        if self.if_circulate():
            self.cancel_screenshot_circulate()

        if self.shotgap > 0:
            self.get_screen()
            self._screenshot_timer = self._master.after(self.shotgap, self._circulate)

    def _circulate(self):
        """截屏循环"""
        self.get_screen()
        self._screenshot_timer = self._master.after(self.shotgap, self._circulate)
            
    def cancel_screenshot_circulate(self):
        """取消截图循环"""
        if not self._screenshot_timer is None:
            self._master.after_cancel(self._screenshot_timer)
            self._screenshot_timer = None

    def update_config(self, path:str = None, max_amount:int = None, quality:int = None, shotgap:int = None):
        """更新配置"""
        if path is not None:
            self.path = path
        if max_amount is not None:
            self.max_amount = max_amount
        if quality is not None:
            self.quality = quality
        if shotgap is not None:
            self.shotgap = shotgap

        self._screenshot.path = self.path
        self._screenshot.max_amount = self.max_amount
        self._screenshot.quality = self.quality

        self.cancel_screenshot_circulate()
        self.start()

    def get_screen(self, if_circulate:bool = True):
        """截屏并清理"""
        self._screenshot.shot()
        self._screenshot.clean()

    def if_circulate(self):
        """是否在循环"""
        return not self._screenshot_timer is None
if __name__ == "__main__":

    import time

    def test_screenshoter():
        # 指定保存路径（当前目录下的 screenshot 文件夹）
        save_path = "screenshot"
        max_pics = 3     # 最多保留 3 张
        quality = 1     # 图像缩放质量倍数

        # 创建对象
        shooter = Screenshot(save_path, max_pics, quality)

        # 连续截图 5 次，每次间隔 1 秒
        for i in range(5):
            print(f"\n开始第 {i+1} 次截图...")
            success = shooter.shot()
            shooter.clean()
            if success:
                print("截图成功:", shooter.picture_cache)
            else:
                print("截图失败")
            shooter.clean()
            print("当前保留的截图数量:", len(shooter.picture_list))
            time.sleep(1)
            
    test_screenshoter()