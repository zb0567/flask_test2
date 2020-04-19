__author__ = 'zz'

#!/usr/bin/env python
import os

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell

from caiwu import create_app, db
from caiwu.models import User, Role

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)  # 初始化migrate


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


manager.add_command("shell",Shell(make_context=make_shell_context()))
manager.add_command('db', MigrateCommand)  # 把migratecommand添加到db里面

if __name__ == '__main__':
    manager.run()
