__author__ = 'zz'

from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, ValidationError

from caiwu.models import User, Role


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('提交')


class RegistrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, '用户名只能含有字母、数字、句号、下划线')])
    password = PasswordField('password', validators=[DataRequired(), EqualTo('password2', message='密码要一致')])
    password2 = PasswordField('Confirm password',validators=[DataRequired()])
    submit = SubmitField('提交')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经在用')



class EditProfileForm(FlaskForm):
    name = StringField('名字',validators=[Length(0,64)])
    dep = StringField('部门', validators=[Length(0,64)])
    beizhu = TextAreaField('备注')
    submit = SubmitField('提交')


class EditProfileAdminForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, '用户名只能含有字母、数字、句号、下划线')])
    confirmed = BooleanField('是否确认')
    role = SelectField('Role',coerce=int)  # coerce转换字段为整数
    name = StringField('名字',validators=[Length(0,64)])
    dep = StringField('部门', validators=[Length(0,64)])
    beizhu = TextAreaField('备注')
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        self.role.choices=[(role.id,role.name) for role in Role.query.order_by(Role.name).all()]
        self.user=user

    def validate_username(self, field):
        if field.data !=self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经在用')


class PostForm(FlaskForm):
    # body = TextAreaField('你的想法是',validators=[DataRequired()])
    body = PageDownField('你的想法是',validators=[DataRequired()])
    submit = SubmitField('提交')