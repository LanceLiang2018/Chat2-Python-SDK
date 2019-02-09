from tkinter import *
from tkinter import scrolledtext
from chat2_sdk import *
import webbrowser
import threading
import sys


class MyUI:
    def __init__(self):
        # self.buf = ""
        pass

    def write(self, x):
        # self.buf = self.buf + x
        text_logs.insert(END, x)
        text_logs.see(END)
        text_logs.update()
        __screen__.write(x)

    def flush(self):
        pass


def printer_loop(username, password):
    latina.mainloop(username=username, password=password)


def start_service():
    global running
    if running is True:
        return
    username = text_username.get()
    password = text_password.get()
    with open('paper.txt', 'w') as f:
        f.write(text_paper.get())
    running = True
    sys.stdout = MyUI()
    t = threading.Thread(target=printer_loop, args=(username, password, ))
    t.start()


running = False
__screen__ = sys.stdout

root = Tk()
root.title("方寸之间 - 设备端程序")

frame1 = Frame(root)
Label(frame1, text="方寸之间 - 设备端程序").grid(row=0, column=0)
Button(frame1, text="获取帮助", command=lambda: webbrowser.open("https://lance-chatroom2.herokuapp.com/device_help"))\
    .grid(row=0, column=1)
frame1.pack()

frame2 = Frame(root)
Label(frame2, text="账号").grid(row=0, column=0)
text_username = Entry(frame2)
text_username.grid(row=0, column=1)
frame2.pack()

frame3 = Frame(root)
Label(frame3, text="密码",).grid(row=0, column=0)
text_password = Entry(frame3, show="*")
text_password.grid(row=0, column=1)
frame3.pack()

frame4 = Frame(root)
Label(frame4, text="纸张").grid(row=1, column=0)
try:
    with open('paper.txt', 'r') as f:
        paper_type = f.read()
except FileNotFoundError as e:
    paper_type = '58'
    with open('paper.txt', 'w') as f:
        f.write(paper_type)
val = StringVar()
text_paper = Entry(frame4, textvariable=val)
text_paper.grid(row=1, column=1)
val.set(paper_type)
frame4.pack()

frame5 = Frame(root)
Button(frame5, text="开启服务", command=start_service).pack(fill=X, expand=1)
frame5.pack(fill=X, expand=1)

frame6 = Frame(root)
text_logs = scrolledtext.ScrolledText(frame6, width=30, height=10)
text_logs.pack(fill=BOTH, expand=1)
frame6.pack(fill=BOTH, expand=1)


def on_closing():
    global latina
    print("#### 等待服务关闭 ####")
    print("#### 未响应请结束进程 ####")
    latina.sdk_running = False
    if running is True:
        ti = 1.0
        while latina.quit_confirm is False:
            ti = ti + 0.1
            time.sleep(0.1)
            if ti > 5.0:
                os.system("taskkill /pid %s /f > nul" % os.getpid())
    root.destroy()
    os.system("taskkill /pid %s /f > nul" % os.getpid())

latina = LatinaPrinter()
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
