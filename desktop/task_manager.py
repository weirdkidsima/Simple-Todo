import sqlite3
from datetime import datetime

class TaskManager:
    def __init__(self):
        self.conn = sqlite3.connect('todo_list.db')
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task TEXT NOT NULL,
                    deadline DATE,
                    color TEXT,
                    color_name TEXT
                )
            ''')

    def add_task(self, task_description):
        with self.conn:
            cursor = self.conn.execute('''
                INSERT INTO tasks (task) VALUES (?)
            ''', (task_description,))
            return cursor.lastrowid

    def edit_task(self, task_id, new_task_description):
        with self.conn:
            self.conn.execute('''
                UPDATE tasks SET task = ? WHERE id = ?
            ''', (new_task_description, task_id))

    def delete_task(self, task_id):
        with self.conn:
            self.conn.execute('''
                DELETE FROM tasks WHERE id = ?
            ''', (task_id,))

    def set_deadline(self, task_id, deadline):
        with self.conn:
            self.conn.execute('''
                UPDATE tasks SET deadline = ? WHERE id = ?
            ''', (deadline, task_id))

    def set_color(self, task_id, color, color_name):
        with self.conn:
            self.conn.execute('''
                UPDATE tasks SET color = ?, color_name = ? WHERE id = ?
            ''', (color, color_name, task_id))

    def load_tasks(self):
        with self.conn:
            cursor = self.conn.execute('SELECT * FROM tasks')
            tasks = cursor.fetchall()
            return [self._task_from_row(row) for row in tasks]

    def get_task(self, task_id):
        with self.conn:
            cursor = self.conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
            row = cursor.fetchone()
            return self._task_from_row(row)

    def _task_from_row(self, row):
        return {
            "id": row[0],
            "task": row[1],
            "deadline": datetime.strptime(row[2], "%Y-%m-%d") if row[2] else None,
            "color": row[3],
            "color_name": row[4]
        }
