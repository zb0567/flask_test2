from flask import Flask

app = Flask(__name__)  # 程序初始化


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/user/<name>')
def hello_world2(name):   # 方法名唯一
    return 'Hello World! %s 4' % name  # 改动不能立即生效


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)  # 改动不生效 只要在运行环境里面点击debug才生效
