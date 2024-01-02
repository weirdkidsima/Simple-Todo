from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fGHk7r#HNzit9Jpx3zjqKbKNpXnST?E|'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True)


    def is_valid_username(self, username):
        return any(c.isalnum() for c in username)


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
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not User().is_valid_username(username):
            flash('Имя пользователя должно содержать хотя-бы одну букву любого алфавита или цифру')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Пользователь c таким именем уже существует. Пожалуйста выберите другое имя пользователя')
            return redirect(url_for('register'))

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Регистрация успешна. Теперь вы можете войти.', 'success')
        return redirect('/login')

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if 'login' in request.path:
            if user and user.password == password:
                login_user(user)
                flash('Вход успешен.', 'success')
                return redirect(url_for('tasks'))
            else:
                flash('Неправильное имя пользователя или пароль.', 'danger')

    return render_template('login.html')



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


if __name__ == '__main__':

    with app.app_context():
        if db.session.query(User).count() == 0:
            empty_user = User(username='unkown', password='tghhjgchvhjbjnkhvgvhbn')
            db.session.add(empty_user)
            db.session.commit()

    with app.test_request_context():
        logout_user()

    app.run(debug=True)
