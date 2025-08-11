import tkinter as tk
import threading
from register.register import RegisterManager
import tkinter.filedialog as filedialog
from util.string_util import *
from util.import_util import UserDataImporter
from tkinter import ttk, messagebox

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
        self.user_importer = UserDataImporter()  # 用户数据导入器
        self.registration_mode = tk.StringVar(value="random")  # 注册模式：random或import
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
        # 临时置顶，确保窗口显示在前台
        self.window.attributes('-topmost', True)
        print("窗口UI初始化成功")


    def setup_ui(self):
        """
        初始化窗口组件UI
        """
        print("初始化窗口UI中...")
        
        # 创建主框架
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 创建左右两列布局
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill='both', expand=True, padx=(0, 5))
        
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill='both', expand=True, padx=(5, 0))
        
        # 左列：注册模式选择
        mode_frame = tk.LabelFrame(left_frame, text="注册模式", font=('Arial', 10, 'bold'))
        mode_frame.pack(fill='x', pady=(0, 10))
        
        mode_inner = tk.Frame(mode_frame)
        mode_inner.pack(fill='x', padx=10, pady=5)
        
        tk.Radiobutton(mode_inner, text="随机生成模式", variable=self.registration_mode, 
                      value="random", command=self.on_mode_change).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(mode_inner, text="导入数据模式", variable=self.registration_mode, 
                      value="import", command=self.on_mode_change).pack(side=tk.LEFT, padx=10)
        
        # 左列：基础配置框架
        basic_frame = tk.LabelFrame(left_frame, text="基础配置", font=('Arial', 10, 'bold'))
        basic_frame.pack(fill='x', pady=(0, 10))
        

        # 注册数量
        count_frame = tk.Frame(basic_frame)
        count_frame.pack(fill='x', padx=10, pady=3)
        tk.Label(count_frame, text="注册数量：", width=12, anchor='w').pack(side=tk.LEFT)
        self.count_entry = tk.Entry(count_frame, width=30)
        self.count_entry.pack(side=tk.LEFT, fill='x', expand=True)
        self.count_entry.insert(0, "1")  # 默认值
        
        # 线程数配置
        thread_frame = tk.Frame(basic_frame)
        thread_frame.pack(fill='x', padx=10, pady=3)
        tk.Label(thread_frame, text="线程数：", width=12, anchor='w').pack(side=tk.LEFT)
        self.thread_count_entry = tk.Entry(thread_frame, width=30)
        self.thread_count_entry.pack(side=tk.LEFT, fill='x', expand=True)
        self.thread_count_entry.insert(0, "5")  # 默认5个线程
        
        # 导出路径
        export_frame = tk.Frame(basic_frame)
        export_frame.pack(fill='x', padx=10, pady=3)
        tk.Label(export_frame, text="导出路径：", width=12, anchor='w').pack(side=tk.LEFT)
        self.export_path_entry = tk.Entry(export_frame, width=20)
        self.export_path_entry.pack(side=tk.LEFT, fill='x', expand=True)
        browse_btn = tk.Button(export_frame, text="浏览", command=self.browse_export_path)
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        # 左列：随机生成模式配置框架
        self.random_frame = tk.LabelFrame(left_frame, text="随机生成配置", font=('Arial', 10, 'bold'))
        self.random_frame.pack(fill='x', pady=(0, 10))
        
        # 名字
        name_frame = tk.Frame(self.random_frame)
        name_frame.pack(fill='x', padx=10, pady=3)
        tk.Label(name_frame, text="名字（空=随机）：", width=15, anchor='w').pack(side=tk.LEFT)
        self.name_entry = tk.Entry(name_frame, width=30)
        self.name_entry.pack(side=tk.LEFT, fill='x', expand=True)
        
        # 生日
        birthday_frame = tk.Frame(self.random_frame)
        birthday_frame.pack(fill='x', padx=10, pady=3)
        tk.Label(birthday_frame, text="生日（YYYY-MM-DD）：", width=15, anchor='w').pack(side=tk.LEFT)
        self.birthday_entry = tk.Entry(birthday_frame, width=30)
        self.birthday_entry.pack(side=tk.LEFT, fill='x', expand=True)
        self.birthday_entry.insert(0, "2000-01-01")
        
        # 国家
        country_frame = tk.Frame(self.random_frame)
        country_frame.pack(fill='x', padx=10, pady=3)
        tk.Label(country_frame, text="国家（空=China）：", width=15, anchor='w').pack(side=tk.LEFT)
        self.country_entry = tk.Entry(country_frame, width=30)
        self.country_entry.pack(side=tk.LEFT, fill='x', expand=True)
        
        # 性别
        gender_frame = tk.Frame(self.random_frame)
        gender_frame.pack(fill='x', padx=10, pady=3)
        tk.Label(gender_frame, text="性别（空=男）：", width=15, anchor='w').pack(side=tk.LEFT)
        self.gender_entry = tk.Entry(gender_frame, width=30)
        self.gender_entry.pack(side=tk.LEFT, fill='x', expand=True)
        
        # 左列：导入数据模式配置框架
        self.import_frame = tk.LabelFrame(left_frame, text="导入数据配置", font=('Arial', 10, 'bold'))
        self.import_frame.pack(fill='x', pady=(0, 10))
        
        # 导入文件选择
        import_file_frame = tk.Frame(self.import_frame)
        import_file_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(import_file_frame, text="Excel文件：", width=12, anchor='w').pack(side=tk.LEFT)
        self.import_file_entry = tk.Entry(import_file_frame, width=20)
        self.import_file_entry.pack(side=tk.LEFT, fill='x', expand=True)
        import_btn = tk.Button(import_file_frame, text="选择文件", command=self.browse_import_file)
        import_btn.pack(side=tk.LEFT, padx=5)
        
        # 导入状态显示
        import_status_frame = tk.Frame(self.import_frame)
        import_status_frame.pack(fill='x', padx=10, pady=3)
        self.import_status_label = tk.Label(import_status_frame, text="未导入数据", fg="gray")
        self.import_status_label.pack(side=tk.LEFT)
        
        # 左列：按钮框架
        button_frame = tk.Frame(left_frame)
        button_frame.pack(pady=10)
        start_btn = tk.Button(button_frame, text="开始注册", width=15, height=2, 
                             command=self.start_registration, bg="#4CAF50", fg="black",
                             font=('Arial', 10, 'bold'))
        start_btn.pack(side=tk.LEFT, padx=10)
        
        clear_btn = tk.Button(button_frame, text="清空日志", width=15, height=2, 
                             command=self.clear_log, bg="#FF9800", fg="black",
                             font=('Arial', 10, 'bold'))
        clear_btn.pack(side=tk.LEFT, padx=10)
        
        # 左列：日志框架
        log_frame = tk.LabelFrame(left_frame, text="运行日志", font=('Arial', 10, 'bold'))
        log_frame.pack(fill='both', expand=True, pady=(0, 5))
        
        # 日志文本框和滚动条
        log_container = tk.Frame(log_frame)
        log_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.log_text = tk.Text(log_container, height=15, wrap=tk.WORD)
        scrollbar = tk.Scrollbar(log_container, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        
        self.log_text.config(state=tk.DISABLED)
        
        # 右列：邮箱配置
        email_config_frame = tk.LabelFrame(right_frame, text="邮箱配置", font=('Arial', 10, 'bold'))
        email_config_frame.pack(fill='x', pady=(0, 10))
        
        # 邮箱域名
        domain_frame = tk.Frame(email_config_frame)
        domain_frame.pack(fill='x', padx=10, pady=3)
        tk.Label(domain_frame, text="邮箱域名：", width=12, anchor='w').pack(side=tk.LEFT)
        self.email_domain_entry = tk.Entry(domain_frame, width=30)
        self.email_domain_entry.pack(side=tk.LEFT, fill='x', expand=True)
        # self.email_domain_entry.insert(0, "eatfan.")  # 默认值

        # 邮箱服务器API URL
        api_url_frame = tk.Frame(email_config_frame)
        api_url_frame.pack(fill='x', padx=10, pady=3)
        tk.Label(api_url_frame, text="API URL：", width=12, anchor='w').pack(side=tk.LEFT)
        self.api_url_entry = tk.Entry(api_url_frame, width=30)
        self.api_url_entry.pack(side=tk.LEFT, fill='x', expand=True)
        # self.api_url_entry.insert(0, "http://127.0.0.1/api/v1")  # 默认值
        
        # API 密钥
        api_key_frame = tk.Frame(email_config_frame)
        api_key_frame.pack(fill='x', padx=10, pady=3)
        tk.Label(api_key_frame, text="API 密钥：", width=12, anchor='w').pack(side=tk.LEFT)
        self.api_key_entry = tk.Entry(api_key_frame, width=30, show="*")
        self.api_key_entry.pack(side=tk.LEFT, fill='x', expand=True)
        # self.api_key_entry.insert(0, "442317-C79337-D145B7-96DFC8-D2BF50")  # 默认值
        

        # 右列：账号注册情况表格
        table_frame = tk.LabelFrame(right_frame, text="账号注册情况", font=('Arial', 10, 'bold'))
        table_frame.pack(fill='both', expand=True, pady=(0, 5))
        
        # 创建表格
        table_container = tk.Frame(table_frame)
        table_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 定义表格列
        columns = ('邮箱', '密码', '姓名', '生日', '当前注册状态', '类型', '状态')
        self.account_tree = ttk.Treeview(table_container, columns=columns, show='headings', height=15)
        
        # 设置列标题和宽度
        for col in columns:
            self.account_tree.heading(col, text=col)
            if col == '邮箱':
                self.account_tree.column(col, width=150)
            elif col == '密码':
                self.account_tree.column(col, width=100)
            elif col == '姓名':
                self.account_tree.column(col, width=80)
            elif col == '生日':
                self.account_tree.column(col, width=80)
            elif col == '当前注册状态':
                self.account_tree.column(col, width=100)
            elif col == '类型':
                self.account_tree.column(col, width=60)
            else:
                self.account_tree.column(col, width=60)
        
        # 添加表格滚动条
        table_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.account_tree.yview)
        self.account_tree.configure(yscrollcommand=table_scrollbar.set)
        
        self.account_tree.pack(side=tk.LEFT, fill='both', expand=True)
        table_scrollbar.pack(side=tk.RIGHT, fill='y')
        
        # 初始化界面状态
        self.on_mode_change()
        # 取消置顶状态
        self.window.attributes('-topmost', False)
        print("初始化窗口UI成功")


    def on_mode_change(self):
        """
        注册模式切换事件处理
        """
        mode = self.registration_mode.get()
        if mode == "random":
            # 显示随机生成配置，隐藏导入配置
            self.random_frame.pack(fill='x', pady=(0, 10))
            self.import_frame.pack_forget()
        else:
            # 显示导入配置，隐藏随机生成配置
            self.import_frame.pack(fill='x', pady=(0, 10))
            self.random_frame.pack_forget()
    
    def browse_export_path(self):
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
    
    def browse_import_file(self):
        """
        选择要导入的Excel文件
        """
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel 文件", "*.xlsx"), ("Excel 文件", "*.xls")],
            title="选择要导入的Excel文件"
        )
        if file_path:
            self.import_file_entry.delete(0, 'end')
            self.import_file_entry.insert(0, file_path)
            # 尝试导入数据
            self.import_user_data(file_path)
    
    def import_user_data(self, file_path):
        """
        导入用户数据
        """
        try:
            if self.user_importer.import_from_excel(file_path):
                count = self.user_importer.get_user_count()
                self.import_status_label.config(text=f"已导入 {count} 条用户数据", fg="green")
                # 自动设置注册数量
                self.count_entry.delete(0, 'end')
                self.count_entry.insert(0, str(count))
                self.print_log(f"成功导入 {count} 条用户数据", "green")
            else:
                self.import_status_label.config(text="导入失败", fg="red")
                messagebox.showerror("导入失败", "无法导入Excel文件，请检查文件格式")
        except Exception as e:
            self.import_status_label.config(text="导入失败", fg="red")
            messagebox.showerror("导入失败", f"导入过程中出现错误：{str(e)}")
    
    def clear_log(self):
        """
        清空日志和表格
        """
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # 清空账号表格
        self.clear_account_table()
        
        print("日志和表格已清空")


    def start_registration(self):
        """
        开始注册
        """
        # 获取基础参数
        domain = self.email_domain_entry.get().strip()
        count_str = self.count_entry.get().strip()
        thread_count_str = self.thread_count_entry.get().strip()
        export_path = self.export_path_entry.get().strip()
        mode = self.registration_mode.get()

        # 基础参数验证
        try:
            count = int(count_str)
            if count <= 0:
                self.print_log("注册数量必须大于0", "red")
                return
        except ValueError:
            self.print_log("注册数量必须是有效的整数", "red")
            return
        try:
            thread_count = int(thread_count_str)
            if thread_count <= 0:
                self.print_log("线程数必须大于0", "red")
                return
            if thread_count > 20:
                self.print_log("线程数不建议超过20，以免对服务器造成过大压力", "red")
                return
        except ValueError:
            self.print_log("线程数必须是有效的整数", "red")
            return
        if not export_path:
            self.print_log("导出保存路径未设置！", "red")
            return

        # 根据模式进行不同的处理
        if mode == "random":
            # 随机生成模式
            name = self.name_entry.get().strip()
            birthday = self.birthday_entry.get().strip()
            country = self.country_entry.get().strip()
            gender = self.gender_entry.get().strip()
            
            # 设置默认值
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
            
            self.print_log(f"开始随机生成模式注册 {count} 个账号，使用 {thread_count} 个线程...", "blue")
            threading.Thread(target=self._run_random_registration, args=(
               domain, count, name, birthday, country, gender, export_path, thread_count
            )).start()
            
        else:
            # 导入数据模式
            if self.user_importer.get_user_count() == 0:
                self.print_log("请先导入用户数据！", "red")
                return
            
            imported_count = self.user_importer.get_user_count()
            if count > imported_count:
                self.print_log(f"注册数量({count})超过导入的用户数据数量({imported_count})！", "red")
                return
            
            self.print_log(f"开始导入数据模式注册 {count} 个账号，使用 {thread_count} 个线程...", "blue")
            threading.Thread(target=self._run_import_registration, args=(
               domain, count, export_path, thread_count
            )).start()

    def _run_random_registration(self, domain, count, name, birthday, country, gender, export_path, thread_count):
        """
        在单独的线程中运行随机生成模式的注册过程
        :param domain: 邮箱域名
        :param count: 注册数量
        :param name: 名字
        :param birthday: 生日
        :param country: 国家
        :param gender: 性别
        :param export_path: 导出文件路径
        :param thread_count: 线程数
        """
        # 创建注册管理器实例
        register_manager = RegisterManager(log_callback=self.print_log, app_instance=self)
        # 执行随机生成注册过程
        register_manager.register_accounts_random(
            domain, count, name, birthday, country, gender, export_path, thread_count
        )
    
    def _run_import_registration(self, domain, count, export_path, thread_count):
        """
        在单独的线程中运行导入数据模式的注册过程
        :param domain: 邮箱域名
        :param count: 注册数量
        :param export_path: 导出文件路径
        :param thread_count: 线程数
        """
        # 创建注册管理器实例
        register_manager = RegisterManager(log_callback=self.print_log, app_instance=self)
        # 获取导入的用户数据
        user_data = self.user_importer.get_user_data()[:count]
        # 执行导入数据注册过程
        register_manager.register_accounts_import(
            domain, user_data, export_path, thread_count
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
        
        # 颜色映射：将不清晰的颜色映射为更清晰的颜色
        color_mapping = {
            'yellow': '#FF8C00',  # 深橙色，比黄色更清晰
            'cyan': '#00CED1',    # 深青色
            'magenta': '#FF1493'  # 深粉色
        }
        
        # 使用映射后的颜色
        display_color = color_mapping.get(color, color)
        
        # 配置颜色 tag
        if color not in self.log_text.tag_names():
            self.log_text.tag_configure(color, foreground=display_color)
        # 应用 tag 到该行
        self.log_text.tag_add(color, start_index, end_index)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def add_account_to_table(self, email, password, name, birthday, status, account_type="随机"):
        """
        添加账号到表格中
        """
        def _add():
            # 确定状态显示
            status_text = "成功" if status else "失败"
            status_color = "green" if status else "red"
            
            # 插入数据到表格
            item = self.account_tree.insert('', 'end', values=(
                email, password, name, birthday, status_text, account_type, "已注册"
            ))
            
            # 设置行颜色
            if status:
                self.account_tree.set(item, '当前注册状态', '成功')
            else:
                self.account_tree.set(item, '当前注册状态', '失败')
            
            # 滚动到最新添加的项目
            self.account_tree.see(item)
        
        # 在主线程中执行
        self.window.after(0, _add)
    
    def clear_account_table(self):
        """
        清空账号表格
        """
        for item in self.account_tree.get_children():
            self.account_tree.delete(item)
        print("账号表格已清空")
    

    
    def get_email_api_config(self):
        """
        获取邮箱API配置
        """
        return {
            'email_domain': self.email_domain_entry.get().strip(),
            'api_url': self.api_url_entry.get().strip(),
            'api_key': self.api_key_entry.get().strip()
        }


