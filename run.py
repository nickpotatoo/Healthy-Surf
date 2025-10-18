import time
import os

t = None
last_t = None

def init():
    global t, last_t
    if not os.path.exists("monitor"):
        t = time.time()
        last_t = t
        with open("monitor", "w") as file:
            file.write("b" + str(t))

while True:
    init()
    with open("monitor", "r") as file:
        content = file.read().strip()
        
    if not content:
        t = time.time()
        last_t = t
        with open("monitor", "w") as file:
            file.write("b" + str(t))
    elif content[0] == "a":
        t = time.time()
        last_t = t
        with open("monitor", "w") as file:
            file.write("b" + str(t))
    elif content[0] == "b":
        time.sleep(10)
    else:
        t = time.time()
        last_t = t
        with open("monitor", "w") as file:
            file.write("b" + str(t))