"""Точка входа в приложение"""
import tkinter as tk
from src.database import init_db
from src.ui.main_window import MainWindow
import sys
from pathlib import Path


def main():
    init_db()
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ui.main_window import main

if __name__ == '__main__':
    main()