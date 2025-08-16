import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path

from . import test_strings
from .dep_finding.python_dep_finder import PythonDepFinder
from .graph_building.graph_creator import GraphCreator
from .logging_setup import setup_logger
from .utils import visualize_graph

logger = setup_logger()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dependency Graph Builder")
        self.geometry("600x400")

        self.project_path = None
        self.save_path = None

        # Кнопка выбора директории проекта
        self.select_dir_btn = tk.Button(self, text="Выбрать проект", command=self.select_project_dir)
        self.select_dir_btn.pack(pady=10)

        # Кнопка выбора места сохранения графа
        self.select_save_btn = tk.Button(self, text="Выбрать файл для графа", command=self.select_save_file)
        self.select_save_btn.pack(pady=10)

        # Кнопка запуска анализа
        self.run_btn = tk.Button(self, text="Запустить анализ", command=self.run_analysis)
        self.run_btn.pack(pady=10)

        # Окно для логов
        self.log_text = scrolledtext.ScrolledText(self, height=10)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)

    def select_project_dir(self):
        self.project_path = Path(filedialog.askdirectory(title="Выберите директорию проекта"))
        if self.project_path:
            self.log(f"Выбрана директория проекта: {self.project_path}")

    def select_save_file(self):
        self.save_path = filedialog.asksaveasfilename(
            title="Выберите куда сохранить граф",
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        if self.save_path:
            self.log(f"Файл для сохранения графа: {self.save_path}")

    def run_analysis(self):
        if not self.project_path:
            messagebox.showwarning("Ошибка", "Сначала выберите директорию проекта")
            return
        if not self.save_path:
            messagebox.showwarning("Ошибка", "Сначала выберите файл для сохранения графа")
            return

        self.log("APPLICATION START")
        try:
            dep_finder = PythonDepFinder(self.project_path)
            graph_creator = GraphCreator()

            self.log("Начало поиска зависимостей...")
            dep_finder.start_dep_finding()
            self.log("Зависимости найдены")

            graph_creator.build_graph(dep_finder.get_dep_dict())
            visualize_graph(graph_creator.get_graph(), self.save_path)
            self.log(f"Граф сохранен: {self.save_path}")
            messagebox.showinfo("Готово", "Анализ завершен успешно!")
        except Exception as e:
            self.log(f"Ошибка: {e}")
            messagebox.showerror("Ошибка", str(e))

    def log(self, message: str):
        logger.info(message)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

def run():
    app = App()
    app.mainloop()
