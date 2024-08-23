import tkinter as tk
from tkinter import colorchooser, messagebox
from datetime import datetime
from task_manager import TaskManager


class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List")

        self.task_manager = TaskManager()

        # GUI компоненты
        self.frame = tk.Frame(root)
        self.frame.pack()

        self.button_frame = tk.Frame(root)
        self.button_frame.pack()

        self.listbox = tk.Listbox(self.frame, width=50, height=15)
        self.listbox.pack(side=tk.LEFT)

        self.scrollbar = tk.Scrollbar(self.frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)

        self.add_button = tk.Button(self.button_frame, text="Добавить", command=self.add_task)
        self.add_button.pack(side=tk.LEFT)

        self.edit_button = tk.Button(self.button_frame, text="Редактировать", command=self.edit_task)
        self.edit_button.pack(side=tk.LEFT)

        self.delete_button = tk.Button(self.button_frame, text="Удалить", command=self.delete_task)
        self.delete_button.pack(side=tk.LEFT)

        self.deadline_button = tk.Button(self.button_frame, text="Установить дедлайн", command=self.set_deadline)
        self.deadline_button.pack(side=tk.LEFT)

        self.color_button = tk.Button(self.button_frame, text="Установить цвет", command=self.set_color)
        self.color_button.pack(side=tk.LEFT)

        self.load_tasks()

    def load_tasks(self):
        """Загрузить задачи и цвета из базы данных"""
        tasks = self.task_manager.load_tasks()
        for task in tasks:
            self.update_listbox(task)

    def add_task(self):
        new_task = tk.simpledialog.askstring("Добавить задачу", "Введите описание задачи:")
        if new_task:
            task_id = self.task_manager.add_task(new_task)
            self.update_listbox(self.task_manager.get_task(task_id))

    def edit_task(self):
        selected_task_index = self.listbox.curselection()
        if selected_task_index:
            selected_task_id = self.listbox.get(selected_task_index[0])[0]
            new_task = tk.simpledialog.askstring("Редактировать задачу", "Измените описание задачи:",
                                                 initialvalue=self.task_manager.get_task(selected_task_id)["task"])
            if new_task:
                self.task_manager.edit_task(selected_task_id, new_task)
                self.update_listbox(self.task_manager.get_task(selected_task_id))

    def delete_task(self):
        selected_task_index = self.listbox.curselection()
        if selected_task_index:
            selected_task_id = self.listbox.get(selected_task_index[0])[0]
            self.task_manager.delete_task(selected_task_id)
            self.listbox.delete(selected_task_index[0])

    def set_deadline(self):
        selected_task_index = self.listbox.curselection()
        if selected_task_index:
            selected_task_id = self.listbox.get(selected_task_index[0])[0]
            deadline_str = tk.simpledialog.askstring("Установить дедлайн", "Введите дедлайн (гггг-мм-дд):")
            if deadline_str:
                try:
                    deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
                    self.task_manager.set_deadline(selected_task_id, deadline)
                    self.update_listbox(self.task_manager.get_task(selected_task_id))
                except ValueError:
                    messagebox.showerror("Ошибка", "Неверный формат даты. Используйте формат гггг-мм-дд.")

    def set_color(self):
        selected_task_index = self.listbox.curselection()
        if selected_task_index:
            selected_task_id = self.listbox.get(selected_task_index[0])[0]
            color_code = colorchooser.askcolor()[1]
            if color_code:
                color_name = tk.simpledialog.askstring("Название цвета", "Введите название для этого цвета:")
                if color_name:
                    self.task_manager.set_color(selected_task_id, color_code, color_name)
                    self.update_listbox(self.task_manager.get_task(selected_task_id))

    def update_listbox(self, task):
        """Обновляет listbox с учетом изменения задачи."""
        if task:
            display_text = f'{task["id"]}: {task["task"]}'
            if task["deadline"]:
                days_left = (task["deadline"] - datetime.now()).days
                display_text += f" (дедлайн через {days_left} дн.)"
            self.listbox.insert(tk.END, display_text)
            if task["color"]:
                self.listbox.itemconfig(tk.END, {'bg': task["color"]})
