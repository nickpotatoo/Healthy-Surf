import time
import os

result = ""

def circuit(judge):
    global result
    if os.path.exists("monitor"):
        with open("monitor", "w") as file:
            result = file.read()
        if judge:
            print(2)
        print(1)
    else:
        with open("monitor", "w") as file:
            file.write("c")
    time.sleep(5)
    circuit(1)

with open("monitor", "w") as file:
    file.write("a")

os.system('python main.py')
circuit(0)