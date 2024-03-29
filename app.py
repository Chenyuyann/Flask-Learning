import os
import sys
import click
from flask import Flask, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape

WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)

class User(db.Model):  # 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(20))  # 名字

class Music(db.Model):  # 表名将会是 music
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(60))  # 歌曲标题
    year = db.Column(db.String(4))  # 歌曲年份

@app.cli.command()  # 注册为命令，可以传入 name 参数来自定义命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息

@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()

    # 全局的两个变量移动到这个函数内
    name = 'Chen'
    musiclists = [
        {'title': 'Latata', 'year': '2018'},
        {'title': 'TOMBOY', 'year': '2022'},
        {'title': 'Villain dies', 'year': '2022'},
        {'title': 'ESCAPE', 'year': '2022'},
        {'title': 'Nxde', 'year': '2022'},
        {'title': 'Queencard', 'year': '2023'},
        {'title': 'Paradise', 'year': '2023'},
        {'title': 'Fate', 'year': '2024'},
    ]

    user = User(name=name)
    db.session.add(user)
    for m in musiclists:
        music = Music(title=m['title'], year=m['year'])
        db.session.add(music)

    db.session.commit()
    click.echo('Done.')

@app.route('/')
def index():
    user = User.query.first()  # 读取用户记录
    musiclists = Music.query.all()  # 读取所有歌曲记录
    return render_template('index.html', user=user, musiclists=musiclists)

@app.route('/user/<name>')
def user_page(name):
    return f'Hello! {escape(name)}'

@app.route('/test')
def test_url_for():
    # 下面是一些调用示例（请访问 http://localhost:5000/test 后在命令行窗口查看输出的 URL）：
    print(url_for('hello'))  # 生成 hello 视图函数对应的 URL，将会输出：/
    # 注意下面两个调用是如何生成包含 URL 变量的 URL 的
    print(url_for('user_page', name='cyy'))  # 输出：/user/greyli
    print(url_for('user_page', name='sakura'))  # 输出：/user/peter
    print(url_for('test_url_for'))  # 输出：/test
    # 下面这个调用传入了多余的关键字参数，它们会被作为查询字符串附加到 URL 后面。
    print(url_for('test_url_for', num=3))  # 输出：/test?num=2
    return 'Test page'