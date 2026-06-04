"""Модуль работы с базой данных"""
import sqlite3
import os
from src.config import DB_NAME

SQL_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sql', 'init_db.sql')
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'init_data.txt')


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Создаёт таблицы из SQL и загружает данные из TXT"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Создание таблиц
    with open(SQL_FILE, 'r', encoding='utf-8') as f:
        cursor.executescript(f.read())
    
    # Загрузка данных из TXT
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        sections = content.strip().split('\n\n')
        
        table_map = {
            '# СТОЛИКИ': 'tables_cafe',
            '# ДОЛЖНОСТИ': 'job_titles',
            '# СОТРУДНИКИ': 'employees',
            '# КАТЕГОРИИ': 'categories',
            '# МЕНЮ': 'menu',
            '# ПРОДУКТЫ': 'products',
            '# СОСТАВ БЛЮД': 'dish_composition',
        }
        
        for section in sections:
            lines = section.strip().split('\n')
            if not lines:
                continue
            
            header = lines[0].strip()
            if header not in table_map:
                continue
            
            table = table_map[header]
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            if cursor.fetchone()[0] > 0:
                continue
            
            if len(lines) < 2:
                continue
            
            columns = lines[1].strip().split('|')
            
            for line in lines[2:]:
                values = line.strip().split('|')
                if len(values) == len(columns):
                    placeholders = ','.join(['?' for _ in columns])
                    cols = ','.join(columns)
                    cursor.execute(f"INSERT INTO {table} ({cols}) VALUES ({placeholders})", values)
    
    conn.commit()
    conn.close()


def execute_query(query, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result


def execute_insert(query, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    last_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return last_id