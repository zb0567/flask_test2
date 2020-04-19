__author__ = 'zz'

# -*- coding:utf-8 -*-
# 定义项目机密信息配置文件,开发环境和生产环境不同，不能上传git
import os

# flask连接数据库
# SQLALCHEMY_DATABASE_URI = 'mysql+cymysql://server:server@localhost:3306/server'
# SQLALCHEMY_TRACK_MODIFICATIONS = True


# app.config['SECRET_KEY'] = 'you are out now'
# app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir, 'data.sqlite')
# app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://comejack:123456@localhost:3306/flask'


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # 密码
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you are out now'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    FLASKY_POSTS_PER_PAGE = 10

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///'+os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-caiwu.sqlite')


class ProductConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development':DevelopmentConfig,
    'testing':TestingConfig,
    'production':ProductConfig,
    'default':ProductConfig,
}


