__author__ = 'zz'

from datetime import datetime

from flask import render_template, redirect, url_for, session, abort, make_response, request, current_app, flash
from flask_login import login_required, current_user

from caiwu.models import User, Permission, Role, Post
from caiwu import db
# from caiwu import app
from caiwu.main.forms import NameForm
from . import main
from ..auth.forms import EditProfileForm, EditProfileAdminForm, PostForm
from ..decorators import admin_required, permission_required


@main.route('/', methods=['GET', 'POST'])
def index():
    # User.generate_fake(100)
    # Post.generate_fake(100)
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data,author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    # posts = Post.query.order_by(Post.created_time.desc()).all()
    page = request.args.get('page', 1 , type=int)
    pagination = Post.query.order_by(Post.created_time.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False
    )  # error_out true 页面超出范围返回404 false则返回空列表 没有指定，默认20
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts, pagination=pagination)


@main.route('/400')
def hello_world400():
    return 'Hello World!', 400


@main.route('/caiwu', methods=['GET', 'POST'])  # 默认为get
def hello_world_index():
    # name = None
    # form = NameForm()
    # if form.validate_on_submit():
    #     name = form.name.data
    #     form.name.data = ''
    # return render_template('index2.html', form=form, current_time=datetime.utcnow(), name=name)
    # ################################POST重定向GET#########每次刷新post，每次刷新redirect################################
    # form = NameForm()
    # if form.validate_on_submit():
    #     session['name'] = form.name.data
    #     return redirect(url_for('hello_world_index'))
    # # return render_template('index2.html', form=form, current_time=datetime.utcnow(), name=name)
    # return render_template('index2.html', form=form, current_time=datetime.utcnow(), name=session.get('name'))
    # ################################名字变幻后可以在前端提示################################
    # form = NameForm()
    # if form.validate_on_submit():
    #     old_name = session.get('name')
    #     if old_name is not None and old_name != form.name.data:
    #         flash('用户名已经变化')
    #     session['name'] = form.username.data
    #     return redirect(url_for('hello_world_index'))
    # return render_template('index2.html', form=form, current_time=datetime.utcnow(), name=session.get('name'))
    form = NameForm()
    if form.validate_on_submit():
        print(User.query.all())
        user = User.query.filter_by(username=form.username.data).first()
        # user = None
        if user is not None:
            user = User(username=form.username.data, password=form.password.data)
            db.session.add(user)
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.username.data
        form.username.data = ''
        return redirect(url_for('.hello_world_index'))
    return render_template('index2.html', form=form, current_time=datetime.utcnow(), name=session.get('name'),
                           known=session.get('known', False))


@main.route('/404')
def hello_world404(user=None):
    if not user:
        abort(404)
    return 'Hello World! %s 4' % user


@main.route('/baidu')
def hello_world_baidu():
    return redirect('http://www.baidu.com')


@main.route('/response')
def hello_world_response():
    response = make_response('111111111111111111')
    response.set_cookie('answer', '12')
    return response


@main.route('/user/<username>')
def user(username):  # 方法名唯一
    # return 'Hello World! %s 4' % name  # 改动不能立即生效
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.created_time.desc()).all()
    return render_template('user.html', user=user, posts=posts)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.dep = form.dep.data
        current_user.beizhu = form.beizhu.data
        db.session.add(current_user)
        flash('个人资料已经根性')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.dep.data = current_user.dep
    form.beizhu.data = current_user.beizhu
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)  # id指定
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.dep = form.dep.data
        user.beizhu = form.beizhu.data
        db.session.add(current_user)
        flash('个人资料已经更新')
        return redirect(url_for('.user', username=user.username))
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.dep.data = user.dep
    form.beizhu.data = user.beizhu
    return render_template('edit_profile.html', form=form,user=user)



@main.route('/index')
@login_required
def index2():  # 方法名唯一
    return render_template('index.html')


@main.route('/ie')
def ie():  # 方法名唯一
    # app_ctx = app.app_context()
    # app_ctx.push()
    print(current_app.name)  # app名称
    # print(app.url_map)  # 目前的请求图
    # app_ctx.pop()
    user_agent = request.headers.get('User-Agent')
    return 'Hello World! %s 4' % user_agent  # 改动不能立即生效


@main.route('/admin')
@login_required
@admin_required
def for_admin_only():
    return '管理员'


@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return "管理他人评论"


# Permission类为所有位定义常量，为避免render_template多加参数，使用上下文处理器，全局访问
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html',posts=[post])

@main.route('/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body=form.body.data
        db.session.add(post)
        flash('已经更新')
        return redirect(url_for('.post',id=post.id))
    form.body.data=post.body
    return render_template('edit_post.html',form=form)