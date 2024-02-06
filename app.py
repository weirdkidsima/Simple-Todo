import os

from dotenv import load_dotenv
from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


def is_valid_username(username):
    has_letter = False
    has_number = False

    for c in username:
        if c.isalpha():
            has_letter = True
        elif c.isdigit():
            has_number = True
    if has_letter and has_number:
        return True
    return False
#TEST!!!!

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = None
    message_color = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not is_valid_username(username):
            message = 'В логине должна быть как минимум 1 буква и 1 цифра'
            message_color = 'error'
        else:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                message = 'Пользователь уже существует'
                message_color = 'error'
            else:
                new_user = User(username=username)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()

                login_user(new_user) # логиним юзера из реги
                return redirect(url_for('tasks'))

    return render_template('register.html', message=message, message_color=message_color)


async def create_Window():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    message_color = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if 'login' in request.path:
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for('tasks'))
            elif username == "":
                message = 'Заполните поля'
                message_color = "error"
            else:
                message = 'Неправильное имя пользователя или пароль'
                message_color = "error"

    return render_template('login.html', message=message, message_color=message_color)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/tasks')
@login_required
def tasks():
    tasks = Task.query.filter_by(user=current_user).all()
    return render_template('tasks.html', tasks=tasks)

@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    content = request.form['content']
    new_task = Task(content=content, user=current_user)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('tasks'))

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get(task_id)

    if request.method == 'POST':
        task.content = request.form['content']
        db.session.commit()
        return redirect(url_for('tasks'))

    return render_template('edit_task.html', task=task)

@app.route('/delete_task/<int:task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('tasks'))

@app.route('/complete_task/<int:task_id>')
@login_required
def complete_task(task_id):
    task = Task.query.get(task_id)
    task.completed = True
    db.session.commit()
    return redirect(url_for('tasks'))

@app.route('/return_task/<int:task_id>')
@login_required
def return_task(task_id):
    task = Task.query.get(task_id)
    task.completed = False
    db.session.commit()
    return redirect(url_for('tasks'))

if __name__ == '__main__':
    with app.app_context():
        if db.session.query(User).count() == 0:
            empty_user = User(username='unknown')
            empty_user.set_password('tghhjgchvhjbjnkhvgvhbn')
            db.session.add(empty_user)
            db.session.commit()

    app.run(debug=True)