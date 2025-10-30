import time
import os
import threading
import subprocess

class Circuit:
    def __init__(self):
        self.result = 0
        self.main_process = None
        with open(".\\monitor", "w") as file:
            file.write("a")
        self.start_process()
    
    def check(self):
        while True:
            time.sleep(5)
            if os.path.exists(".\\monitor"):
                with open(".\\monitor", "r") as file:
                    text = file.read().strip()
                    if text and text[0] == 'a':
                        continue
                    elif text and text[0] == 'b':
                        self.result = float(text[1:])
                        print(self.result)
                    elif text and text[0] == 'd':
                        break
                    else:
                        self.result = 0

                if time.time() - self.result > 60:   # 检查上次更新时间是否超过 60 秒
                    self.restart_process()
            else:
                pass

    def start_process(self):
        self.main_process = subprocess.Popen(  # 启动新的子进程，并允许其使用标准输入输出
            ["python", "main.py"],
            stdin=None,
            stdout=None,
            stderr=None
        )

    def restart_process(self):
        if self.main_process and self.main_process.poll() is None:     # 如果之前有子进程在运行，先结束它
            try:
                self.main_process.terminate()
                self.main_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.main_process.kill()

        with open(".\\monitor", "w") as file:
            file.write("a")

        self.start_process()

circuit = Circuit()
thread_monitor = threading.Thread(target=circuit.check, daemon=True)
thread_monitor.start()
thread_monitor.join()