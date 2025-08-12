from application import Application

def main():
    app = Application("注册机", 750, 1200)  # 增加宽度以适应双列布局
    app.run()

if __name__ == '__main__':
    main()