__author__ = 'zz'

from flask import Flask
from flask_login import LoginManager
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_pagedown import PageDown  # 富文本
from flask_bootstrap import Bootstrap

from config import config

moment = Moment()
db = SQLAlchemy()  # 初始化db
pagedown = PageDown()
bootstrap = Bootstrap()
login_manager = LoginManager()
login_manager.session_protection = 'strong'  # ip和代理信息会被记录，
login_manager.login_view = 'auth.login'  # 用于处理登录认证

login_manager.login_message_category = "info"  # error
login_manager.login_message = u"请登录！"


# 定义一个函数用来创建app核心对象
def create_app(config_name):  # create_app是应用程序工厂方法。
    app = Flask(__name__)  # type:Flask
    # app.config.from_object('config')
    # app.config.from_object('app.secure')
    # app.config.from_object('app.setting')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    # # 调用注册蓝图
    # register_blueprint(app)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)  # 蓝本路由本身休眠，注册到app上之后激活路由
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    # 初始化数据库
    # db.app = app
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    # db.create_all()
    # db.drop_all()
    with app.app_context():
        # 调用生成mysql表的函数
        db.create_all()
    return app


# #  创建注册蓝图的方法
# def register_blueprint(app):
#     # 导入蓝图对象
#     from app.web.blueprint import web
#     app.register_blueprint(web)

# @login_manager.unauthorized_handler
# def unauthorized():
#     # do stuff
#     return render_template("some template")