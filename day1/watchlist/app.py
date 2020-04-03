import os
import sys

from flask import Flask,render_template,flash,redirect,request,url_for
import click
from flask_sqlalchemy import SQLAlchemy   #导入扩展类

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app = Flask(__name__)


#windows
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path,'data.db')
app.config['SQLALCHY_TRACK_MODIFICATIONS'] = False  #关闭了对模型修改的监控
app.config['SECRET_KEY'] = 'watchlist_dev'

db = SQLAlchemy(app)   #初始化扩展，传入程序实例app

#models
class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(20))
class Movie(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))


#m模板上下文处理函数
@app.context_processor
def common_user():
    user = User.query.first()
    return dict(user=user)


#views
@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        # request在请求触发的时候才会包含数据
        title = request.form.get('title')
        year = request.form.get('year')
        # 验证数据
        if not title or not year or len(year)>4 or len(title)>60:
            flash('不能为空或超过最大长度')
            return redirect(url_for('index'))
        # 保存表单数据
        movie = Movie(title=title,year=year)
        db.session.add(movie)
        db.session.commit()
        flash('添加成功')
        return redirect(url_for('index'))

    movies = Movie.query.all()
    return render_template('index.html',movies=movies)


@app.route('/movie/edit/<int:movie_id>',methods=['GET','POST'])
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']
        # 验证数据
        if not title or not year or len(year)>4 or len(title)>60:
            flash('不能为空或超过最大长度')
            return redirect(url_for('index'))
        movie.title = title
        movie.year = year
        db.session.commit()
        flash('更新完成')
        return redirect(url_for('index'))

    return render_template('edit.html',movie=movie)


@app.route('/movie/delete/<int:movie_id>',methods=['GET','POST'])
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if request.method == 'POST':

        db.session.delete(movie)
        db.session.commit()
        flash('删除完成')
        return redirect(url_for('index'))

    return render_template('delete.html',movie=movie)


#自定义命令
#新建data.db的数据库初始化功能
@app.cli.command()  #装饰器，注册命令
@click.option('--drop',is_flag=True,help='删除后在创建')
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo("初始化数据库完成")


# 向data.db中写入数据的命令
@app.cli.command()
def forge():
    name = 'L'
    moviews = [
        {"title":"大赢家","year":"2020"},
        {"title":"速度与激情","year":"2020"},
    ]
    user = User(name=name)
    db.session.add(user)
    for m in moviews:
        movie = Movie(title=m['title'],year=m['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo('插入数据完成')

#错误处理函数
@app.errorhandler(404)
def page_not_found(e):
    #返回模板和状态码
    return render_template('404.html'),404





