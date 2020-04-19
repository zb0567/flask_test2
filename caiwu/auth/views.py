__author__ = 'zz'

from flask import render_template, redirect, request, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user

from . import auth

# @auth.route('/login')    # 先搜索程序配置模板，后续在搜素蓝版存放位置
# def login():
#     return render_template('auth/login.html')
from .forms import LoginForm, RegistrationForm
from .. import db
from ..models import User, Role


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)  # 用户浏览器写入长效cookie
            # Role.insert_roles()  # 0 7 15 255 权限分级
            # login_user(user, remember=False, force=False, fresh=True)
            return redirect(request.args.get('next') or url_for('main.index'))
        # else:
        #     user = User(username=form.username.data)
        #     user.password=form.password.data
        #     db.session.add(user)
        flash('非法的用户名或者密码')
        return redirect(url_for('auth.login'))
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()  # 删除并重设用户会话
    # flash('您已经退出')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        token = user.generate_confirmation_token()
        # send_email(user.email,'发送邮件','auth/email/confirm',user=user,token=token)
        flash('你已经可以登录')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('认证成功')
    else:
        flash('非法认证或者认证信息已经过期')
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.lasttime()
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    token = current_user.generate_confirmation_token()
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html', token=token)


@auth.route('/confirm_resend')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    # send_email(current_user.email,'确认账户','auth/email/confirm',user=current_user,token=token)
    flash('新的邮件已经发送')
    return redirect(url_for('main.index'))

# @app.route('/secret')
# @login_required
# def secret():
#     return '只有认证过才能通过'
