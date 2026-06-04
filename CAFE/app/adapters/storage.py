"""
Адаптер для работы с хранилищем данных.

Отвечает за:
- Резервное копирование базы данных
- Экспорт данных в различные форматы (CSV, JSON)
- Импорт данных из файлов
- Работу с конфигурационными файлами
- Управление файловой системой приложения
"""
import os
import json
import csv
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
import sys

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.config import config


class StorageAdapter:
    """Адаптер для работы с файловым хранилищем"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        Инициализация адаптера хранилища.
        
        Args:
            base_dir: Базовая директория (по умолчанию из config)
        """
        self.base_dir = base_dir or config.BASE_DIR
        self.data_dir = self.base_dir / 'data'
        self.backup_dir = self.data_dir / 'backups'
        self.export_dir = self.data_dir / 'exports'
        
        # Создаем директории если их нет
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Создание необходимых директорий"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    # ========== Backup Operations ==========
    
    def create_backup(self, db_path: Optional[str] = None) -> Path:
        """
        Создание резервной копии базы данных.
        
        Args:
            db_path: Путь к базе данных (по умолчанию из config)
            
        Returns:
            Путь к созданному backup файлу
        """
        db_path = db_path or str(config.DB_PATH)
        
        if not Path(db_path).exists():
            raise FileNotFoundError(f"База данных не найдена: {db_path}")
        
        # Формируем имя файла с датой и временем
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"cafe_backup_{timestamp}.db"
        backup_path = self.backup_dir / backup_filename
        
        # Копируем файл БД
        shutil.copy2(db_path, backup_path)
        
        return backup_path
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        Получить список всех резервных копий.
        
        Returns:
            Список словарей с информацией о backup файлах
        """
        backups = []
        
        for backup_file in self.backup_dir.glob('*.db'):
            stat = backup_file.stat()
            backups.append({
                'filename': backup_file.name,
                'path': str(backup_file),
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created_at': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'modified_at': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # Сортируем по дате создания (новые сверху)
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        
        return backups
    
    def restore_backup(self, backup_path: str, target_db: Optional[str] = None) -> bool:
        """
        Восстановление базы данных из резервной копии.
        
        Args:
            backup_path: Путь к backup файлу
            target_db: Путь для восстановления (по умолчанию оригинальная БД)
            
        Returns:
            True если восстановление успешно
        """
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup файл не найден: {backup_path}")
        
        target_db = target_db or str(config.DB_PATH)
        target_file = Path(target_db)
        
        # Создаем резервную копию текущей БД перед восстановлением
        if target_file.exists():
            self.create_backup(target_db)
        
        # Копируем backup в целевую директорию
        shutil.copy2(backup_file, target_file)
        
        return True
    
    def delete_backup(self, backup_path: str) -> bool:
        """
        Удаление резервной копии.
        
        Args:
            backup_path: Путь к backup файлу
            
        Returns:
            True если удалено успешно
        """
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup файл не найден: {backup_path}")
        
        # Проверяем что файл находится в директории backups
        if not str(backup_file.parent).startswith(str(self.backup_dir)):
            raise ValueError("Можно удалять только файлы из директории backups")
        
        backup_file.unlink()
        return True
    
    def cleanup_old_backups(self, days_to_keep: int =
