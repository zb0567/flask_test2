__author__ = 'zz'

from flask import Blueprint
main = Blueprint('main', __name__)
from . import views, errors  # 在末尾导入，避免循环导入依赖 在相应的文件还导入main
