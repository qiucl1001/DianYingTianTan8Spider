# coding: utf-8
# author: QCL
# software: PyCharm Professional Edition 2018.2.8

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


app = Flask(__name__)


class Config(object):
    """app配置相关信息类"""

    # SQLAlchemy相关配置选项
    # 设置连接数据库的URL
    # 注意：district_code数据库要事先手动创建
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:qcl123@127.0.0.1:3306/dytt8_movie'

    # 动态跟踪配置
    SQLALCHEMY_TRACK_MODIFICATIONS = True


app.config.from_object(Config)

# 创建一个SQLAlchemy数据库连接对象
db = SQLAlchemy(app)

# 创建flask脚本管理工具对象
manager = Manager(app)

# 创建数据库迁移工具对象
Migrate(app, db)

# 向manager对象中添加数据库操作命令
manager.add_command("db", MigrateCommand)


class Movie(db.Model):
    """定义一个存储电影的表格模型类"""
    __tblname__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), unique=False, index=True)
    cover = db.Column(db.String(255))
    year = db.Column(db.String(32))
    country = db.Column(db.String(64))
    category = db.Column(db.String(64))
    douban_score = db.Column(db.String(32))
    duration = db.Column(db.String(64))
    director = db.Column(db.String(128))
    actors = db.Column(db.TEXT)
    profile = db.Column(db.TEXT)
    prize = db.Column(db.TEXT)
    download_url = db.Column(db.TEXT)

    def __str__(self):
        return 'Movie:%s' % self.title


if __name__ == '__main__':
    # # 清空district_code数据库中的所有表
    # db.drop_all()
    # # 创建所有模型类对应的表格
    # db.create_all()

    manager.run()




