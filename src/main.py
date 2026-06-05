"""Точка входа в приложение"""
import tkinter as tk
from src.database import init_db
from src.ui.main_window import MainWindow


def main():
    init_db()
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()