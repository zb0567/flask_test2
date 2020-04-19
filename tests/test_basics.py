__author__ = 'zz'

import unittest
from flask import  current_app
from caiwu import create_app,db
from manage import manager


class BasicsTestCase(unittest.TestCase):
    def SetUp(self):  # 测试前 创建测试环境
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):  # 测试后
        db.session.remove()
        db.drop_all()
        self.app.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

    @manager.command
    def test(self):
        import unittest
        tests = unittest.TestLoader().discover('tests')
        unittest.TextTestRunner(verbosity=2).run(tests)
