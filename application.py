import tkinter as tk
import threading
from register.register import RegisterManager
import tkinter.filedialog as filedialog
from util.string_util import *

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
        # 邮箱域名
        frame7 = tk.Frame(self.window)
        frame7.pack(pady=5, fill='x',padx=10)
        tk.Label(frame7,text="邮箱域名：",width=12,anchor='w').pack(side=tk.LEFT)
        self.domain_entry = tk.Entry(frame7,width=30)
        self.domain_entry.pack(side=tk.LEFT,fill='x',expand=True)

        # 注册数量
        frame1 = tk.Frame(self.window)
        frame1.pack(pady=5, fill='x', padx=10)
        tk.Label(frame1, text="注册数量：", width=12, anchor='w').pack(side=tk.LEFT)
        self.count_entry = tk.Entry(frame1, width=30)
        self.count_entry.pack(side=tk.LEFT, fill='x', expand=True)

        # 名字
        frame2 = tk.Frame(self.window)
        frame2.pack(pady=5, fill='x', padx=10)
        tk.Label(frame2, text="名字（默认随机)：",width=12, anchor='w').pack(side=tk.LEFT)
        self.name_entry = tk.Entry(frame2, width=30)
        self.name_entry.pack(side=tk.LEFT, fill='x', expand=True)

        # 生日
        frame3 = tk.Frame(self.window)
        frame3.pack(pady=5, fill='x', padx=10)
        tk.Label(frame3,text="生日: 2000-01-01",width=12, anchor='w').pack(side=tk.LEFT)
        self.birthday_entry = tk.Entry(frame3, width=30)
        self.birthday_entry.pack(side=tk.LEFT, fill='x', expand=True)

        # 国家区域
        frame4 = tk.Frame(self.window)
        frame4.pack(pady=5, fill='x', padx=10)
        tk.Label(frame4,text="国家（默认China）：",width=12, anchor='w').pack(side=tk.LEFT)
        self.country_entry = tk.Entry(frame4, width=30)
        self.country_entry.pack(side=tk.LEFT, fill='x', expand=True)

        # 性别
        frame5 = tk.Frame(self.window)
        frame5.pack(pady=5, fill='x', padx=10)
        tk.Label(frame5,text="性别（默认男）:",width=12, anchor='w').pack(side=tk.LEFT)
        self.gender_entry = tk.Entry(frame5, width=30)
        self.gender_entry.pack(side=tk.LEFT, fill='x', expand=True)

        # 导出路径
        frame6 = tk.Frame(self.window)
        frame6.pack(pady=5, fill='x', padx=10)
        tk.Label(frame6, text="导出保存路径：", width=12, anchor='w').pack(side=tk.LEFT)
        self.export_path_entry = tk.Entry(frame6, width=20)
        self.export_path_entry.pack(side=tk.LEFT, fill='x', expand=True)
        browse_btn = tk.Button(frame6, text="浏览", command=self.browse_path)
        browse_btn.pack(side=tk.LEFT, padx=5)

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


    def browse_path(self):
        """
        弹出文件保存对话框，选择保存的 Excel 文件路径
        """
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel 文件", "*.xlsx")],
            title="选择保存路径"
        )
        if file_path:
            self.export_path_entry.delete(0, 'end')
            self.export_path_entry.insert(0, file_path)


    def start_registration(self):
        """
        开始注册
        """
        # 获取输入参数
        domain = self.domain_entry.get().strip()
        count_str = self.count_entry.get().strip()
        name = self.name_entry.get().strip()
        birthday = self.birthday_entry.get().strip()
        country = self.country_entry.get().strip()
        gender = self.gender_entry.get().strip()
        export_path = self.export_path_entry.get().strip()

        # 参数验证
        if not domain:
            self.print_log("邮箱域名不能为空！","red")
            return
        try:
            count = int(count_str)
            if count <= 0:
                self.print_log("注册数量必须大于0", "red")
                return
        except ValueError:
            self.print_log("注册数量必须是有效的整数", "red")
            return
        if not birthday:
            birthday = "2000-01-01"
        else:
            if not validate_birthday(birthday):
                self.print_log("生日格式错误！必须是 YYYY-MM-DD 格式！","red")
                return
        if not country:
            country = "China"
        if not gender:
            gender = "男"
        if not export_path:
            self.print_log("导出保存路径未设置！", "red")
            return

        # 创建并启动注册线程
        self.print_log(f"开始注册 {count} 个账号...", "blue")
        threading.Thread(target=self._run_registration, args=(
           domain, count,  name, birthday, country,gender,export_path
        )).start()

    def _run_registration(self,domain ,count,name,birthday,country, gender,export_path):
        """
        在单独的线程中运行注册过程
        :param domain: 邮箱域名
        :param count: 注册数量
        :param name: 名字
        :param birthday: 生日
        :param country: 国家
        :param gender: 性别
        :param export_path: 导出文件路径
        """
        # 创建注册管理器实例
        register_manager = RegisterManager(log_callback=self.print_log)
        # 执行注册过程
        register_manager.register_accounts(
            domain,count,name,birthday,country,gender,export_path
        )

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
        """
        更新日志消息
        :param msg: 日志消息
        :param color: 字体颜色
        """
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


