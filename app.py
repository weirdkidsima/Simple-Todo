from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)


class Task(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    text: str = db.Column(db.String(200))
    completed: bool = db.Column(db.Boolean, default=False)


with app.app_context():
    db.create_all()


@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)


@app.route('/add', methods=['POST'])
def add_task():
    text = request.form.get('text')
    if text:
        new_task = Task(text=text)
        db.session.add(new_task)
        db.session.commit()
    return redirect(url_for('index'))


@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return redirect(url_for('index'))

    if request.method == 'POST':
        new_text = request.form.get('text')
        if new_text:
            task.text = new_text
            db.session.commit()
            return redirect(url_for('index'))

    return render_template('edit.html', task=task)


@app.route('/check/<int:task_id>')
def check_task(task_id):
    task = Task.query.get(task_id)
    if task:
        task.completed = not task.completed
        db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
