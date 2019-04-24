from flask import Flask, render_template
from flask import url_for
from flask import request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_login import login_user,current_user
from flask_login import login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import click
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path,'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'devo'
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(20))
#     username = db.Column(db.String(20))
#     password_hash = db.Column(db.String(128))
#
#     def set_password(self, password): #用来设置密码的方法，接受密码作为参数
#         self.password_hash = generate_password_hash(password) #将生存的密码保存到对应字段。
#
#     def validate_password(self, password): #用来验证密码的方法，接受密码作为参数
#         return check_password_hash(self.password_hash, password)

#创建shell命令函数
@app.cli.command()
@click.option('--drop', is_flag = True, help='Create after drop.') #设置选项
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')

#创建数据库的表函数
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))

#模板上下文处理函数
@app.context_processor
def inject_user():#函数名可以随意修改
    user = User.query.first()
    return dict(user=user) #需要返回字典，等同于return {'user': user}

#视图函数处理请求
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':    #判断请求类型
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        title = request.form.get('title') #传入表单对应的输入字段的name值
        year = request.form.get('year')

        #验证数据
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.') #显示错误提示
            return redirect(url_for('index')) #重定向回主页

        #保存表单数据到数据库
        movie = Movie(title=title, year=year) #创建记录
        db.session.add(movie)  #添加到数据库会话
        db.session.commit()  #提交任务
        flash('Item created')  #显示成功创建的提示
        return redirect(url_for('index'))

    user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html', user=user, movies=movies)

#初始化flask-login
@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id)) #用ID作为User模型的主键查询对应的用户
    return user #返回用户对象

#用户登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))
        
        user = User.query.first()
        #验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('index'))
        
        flash('Invalid username or password.')#如果验证失败，显示错误消息
        return redirect(url_for('login'))
    
    return render_template('login.html')

#设置用户自己的名字
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']
        if not name or len(name) >20:
            flash('Invalid input.')
            return redirect(url_for('settings'))
        
        current_user.name = name
        db.session.commit()
        flash('Setting updated.')
        return redirect(url_for('index'))
    
    return render_template('settings.html')

#404处理函数
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/user/<name>')
def user_page(name):
    return 'User: %s' % name

@app.route('/test')
def test_url_for():
    print(url_for("hello_world"))
    print(url_for('user_page', name='ykf'))
    print(url_for('user_page', name='jayce'))
    print(url_for('test_url_for',num=2))
    return 'Test page'

#编辑电影条目
@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST': #处理编辑表单的提交请求
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year)>4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))

        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item updated')
        return redirect(url_for('index')) #重定向回主页

    return render_template('edit.html', movie=movie)

#登出
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('index'))

#删除电影条目
@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required #登录保护
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id) #获取电影记录
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))




name = 'Grey Li'
movies = [
    {'title': 'My Neighbor Totoro', 'year': '1988'},
    {'title': 'Dead Poets Society', 'year': '1989'},
    {'title': 'A Perfect World', 'year': '1993'},
    {'title': 'Leon', 'year': '1994'},
    {'title': 'Mahjong', 'year': '1996'},
    {'title': 'Swallowtail Butterfly', 'year': '1996'},
    {'title': 'King of Comedy', 'year': '1999'},
    {'title': 'Devils on the Doorstep', 'year': '1999'},
    {'title': 'WALL-E', 'year': '2008'},
    {'title': 'The Pork of Music', 'year': '2012'},
]



if __name__ == '__main__':
    app.run()
