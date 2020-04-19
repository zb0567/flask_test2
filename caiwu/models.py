__author__ = 'zz'

from datetime import datetime

import bleach
from flask import Flask, current_app
from flask_login import UserMixin, AnonymousUserMixin
from markdown import markdown
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from caiwu import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # 以unicode的形式返回用户标识符


# 登录日志
class UserLog(db.Model):
    __tablename__ = 'userlogs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ip = db.Column(db.String(30))
    created_time = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return '<UserLog %r>' % self.id


# 操作日志
class Oplog(db.Model):
    __tablename__ = 'oplogs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ip = db.Column(db.String(30))
    reason = db.Column(db.String(600))  # 操作原因
    created_time = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return '<oplog %r>' % self.id


# 管理员登录日志
class Adminlog(db.Model):
    __tablename__ = 'adminlogs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ip = db.Column(db.String(30))
    created_time = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return '<Admin %r>' % self.name


# 权限及角色数据模型
class Auth(db.Model):
    __tablename__ = 'auths'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)  # 权限名称
    url = db.Column(db.String(255), unique=True)
    created_time = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return '<auth %r>' % self.name


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


# 角色模型
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    moren = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    auths = db.Column(db.String(600))
    # lazy禁止自动执行查询 AttributeError: 'InstrumentedList' object has no attribute 'order_by'
    users = db.relationship('User', backref='role', lazy='dynamic')

    # users = db.relationship('User', backref='role')  # lazy禁止自动执行查询
    @staticmethod
    def insert_roles():
        roles={
            'User':(Permission.FOLLOW|Permission.COMMENT|Permission.WRITE_ARTICLES, True),
            'Moderator':(Permission.FOLLOW|Permission.COMMENT|Permission.WRITE_ARTICLES|Permission.MODERATE_COMMENTS, False),
            'Administrator':(0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.moren = roles[r][1]
            db.session.add(role)

    def __repr__(self):
        return '<Role %r>' % self.name


class Post(db.Model):
    __tablename__="posts"
    id = db.Column(db.Integer, primary_key=True)
    body=db.Column(db.Text)
    body_html = db.Column(db.Text)
    created_time = db.Column(db.DateTime, index=True, default=datetime.now)
    author_id=db.Column(db.Integer,db.ForeignKey('users.id'))

    @staticmethod
    def on_changed_body(target,value,oldvalue,initiator):
        allowed_tags = ['a','abbr','acronym','b','blockquote','code',
                        'em','i','li','ol','strong','ul',
                        'h1','h2','h3','p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value,output_format='html'),
            tags=allowed_tags, strip=True
        ))

    @staticmethod
    def generate_fake(count=100):
        from random import seed,randint
        import forgery_py

        seed()
        user_count=User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0,user_count-1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1,3)),
                     created_time=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)


db.event.listen(Post.body,'set',Post.on_changed_body)


class User(UserMixin, db.Model):
    __tablename__ = 'users'  # 不写会默认
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    # password = db.Column(db.String(64), nullable=False)
    is_super = db.Column(db.Boolean, default=False)  # 是否为超级管理员
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    created_time = db.Column(db.DateTime, index=True, default=datetime.now)
    last_time = db.Column(db.DateTime, index=True, default=datetime.now)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    beizhu = db.Column(db.TEXT())
    dep = db.Column(db.String(64))
    name = db.Column(db.String(64))

    userlogs = db.relationship('UserLog', backref='user',lazy='dynamic')
    posts = db.relationship('Post',backref='author',lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('密码非读属性')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):  # 一个小时
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def lasttime(self):
        self.last_time=datetime.now()
        db.session.add(self)

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def can(self, permisssons):
        return self.role is not None and \
               (self.role.permissions & permisssons) == permisssons  # 请求和赋予之间进行位予操作 包含所有权限位 返回true

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     dep=forgery_py.address.city(),
                     beizhu=forgery_py.lorem_ipsum.sentence(),
                     created_time=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.is_super is True:  # 原文是判定是不是特殊邮箱
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:  # 判定没有role
                self.role = Role.query.filter_by(moren=True).first()

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):  # 不用检查登录，直接使用can和is两个方法

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


# if __name__ == '__main__':
#     db.create_all()
# db.drop_all()

# admin_role = Role(name='admin')
# mod_role = Role(name='Moderator')
# user_role = Role(name='User')
# user_john = User(username='john', password='111', role=admin_role)
# user_susan = User(username='susan', password='222', role=mod_role)
# user_david = User(username='david', password=generate_password_hash('333'), role=user_role)

# print(admin_role.id)  # 未提交
# db.session.add(admin_role)
# print(admin_role.id)  # 未提交
# db.session.add(user_john)
# db.session.add_all([mod_role, user_susan, user_role, user_david])
# print(admin_role.id)  # 未提交
# db.session.rollback()
# admin_role.name = 'Admin'
# db.session.add(admin_role)
# db.delete(mod_role)
# db.session.commit()
# print(admin_role.id)  #提交


# print(User.query.all())
# print(Role.query.all())
# # print(str(User.query.filter_by(role=user_role).all()))
# print(Role.query.filter_by(name='User').first())  # print(users_temp[0].role)等同
# users_temp1 = user_role.users
# for user in users_temp1:
#     print(user.username)
# print('##############################3')
# print(users_temp1)
# print(users_temp1[0].role)
# # print(users_temp1.order_by(User.username).all())
# print(users_temp1.all())
# print(users_temp1.count())
# users_temp = Role.query.filter_by(name='User')[0].users
# for user in users_temp:
#     print(user.username)
# print('##############################3')
# print(users_temp)
# print(users_temp[0].role)
# print(users_temp.order_by(User.username).all())
# print(users_temp.all())
# print(users_temp.count())
