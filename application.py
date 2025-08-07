import tkinter as tk
import threading
from register.register import RegisterManager

class Application:
    def __init__(self,title,height,width):
        """
        初始化应用
        :param title: 窗口标题
        :param height: 窗口高度
        :param width: 窗口宽度
        """
        self.label = None
        self.window = tk.Tk()
        self.title = title
        self.width = width
        self.height = height
        self.init_window()
        self.setup_ui()

    def init_window(self):
        """
        初始化窗口

        设置窗口标题、宽度、高度以及窗口位置
        """
        print("初始化窗口中...")
        self.window.title(self.title)
        # 获取屏幕大小
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        # 计算屏幕中间坐标
        cen_x = (sw - self.width) / 2
        cen_y = (sh - self.height) / 2
        # 设置窗口大小并且剧中
        self.window.geometry('%dx%d+%d+%d' % (self.width, self.height, cen_x, cen_y))
        # 设置窗口不可随便改动大小
        self.window.resizable(False, False)
        self.window.attributes('-topmost', True)
        print("窗口UI初始化成功")

    def setup_ui(self):
        """
        初始化窗口组件UI
        """
        print("初始化窗口UI中...")
        # 注册数量
        frame1 = tk.Frame(self.window)
        frame1.pack(pady=5, fill='x', padx=10)
        tk.Label(frame1, text="注册数量：", width=12, anchor='w').pack(side=tk.LEFT)
        self.count_entry = tk.Entry(frame1, width=30)
        self.count_entry.pack(side=tk.LEFT, fill='x', expand=True)

        # 复选框：随机账号 和 随机密码
        frame2 = tk.Frame(self.window)
        frame2.pack(pady=5, fill='x', padx=10)
        self.random_user_var = tk.BooleanVar()
        self.random_pwd_var = tk.BooleanVar()
        tk.Checkbutton(frame2, text="随机账号", variable=self.random_user_var).pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(frame2, text="随机密码", variable=self.random_pwd_var).pack(side=tk.LEFT, padx=10)

        # 按钮
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=15)
        start_btn = tk.Button(button_frame, text="开始自动注册", width=12, command=self.start_registration)
        start_btn.pack(side=tk.LEFT, padx=10)

        # 日志窗口
        self.log_text = tk.Text(self.window, height=20)
        self.log_text.pack(pady=10)
        self.log_text.config(state=tk.DISABLED)
        self.log_text.bind("<Button-1>", lambda e: "break")  # 禁止鼠标左键点击
        print("初始化窗口UI成功")

    # 开始注册
    def start_registration(self):
        # 获取输入参数
        count_str = self.count_entry.get().strip()
        random_user = self.random_user_var.get()
        random_pwd = self.random_pwd_var.get()

        # 参数验证
        try:
            count = int(count_str)
            if count <= 0:
                self.print_log("注册数量必须大于0", "red")
                return
        except ValueError:
            self.print_log("注册数量必须是有效的整数", "red")
            return

        # 创建并启动注册线程
        self.print_log(f"开始注册 {count} 个账号...", "blue")
        threading.Thread(target=self._run_registration, args=(
            count,  random_user, random_pwd,
        )).start()

    # 在单独的线程中运行注册过程
    def _run_registration(self, count,  random_user, random_pwd,):
        # 创建注册管理器实例
        register_manager = RegisterManager(log_callback=self.print_log)
        # 执行注册过程
        register_manager.register_accounts(
            count,  random_user, random_pwd,
        )

    # 启动
    def run(self):
        self.window.mainloop()

    def print_log(self, msg, color):
        """
        在日志框中打印日志信息
        :param msg: 日志消息
        :param color: 颜色
        """
        # 使用主线程更新UI
        self.window.after(0, self._update_log, msg, color)

    def _update_log(self, msg, color):
        self.log_text.config(state=tk.NORMAL)
        # 插入前获取插入点
        start_index = self.log_text.index(tk.END + "-1c linestart")  # 当前插入行开始
        self.log_text.insert(tk.END, msg + "\n")  # 插入文本
        end_index = self.log_text.index(tk.END + "-1c")  # 插入后行结束位置（不包括新行）
        # 配置颜色 tag
        if color not in self.log_text.tag_names():
            self.log_text.tag_configure(color, foreground=color)
        # 应用 tag 到该行
        self.log_text.tag_add(color, start_index, end_index)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
