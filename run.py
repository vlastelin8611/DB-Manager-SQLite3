#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт запуска SQLite Database Manager для AstraLinux
"""

import sys
import os

def main():
    """Главная функция запуска"""
    print("=" * 60)
    print("SQLite Database Manager для AstraLinux")
    print("=" * 60)
    
    # Проверяем версию Python
    if sys.version_info < (3, 5):
        print("❌ ОШИБКА: Требуется Python 3.5 или новее")
        print(f"   Текущая версия: {sys.version}")
        return 1
    
    print(f"✅ Python версия: {sys.version.split()[0]}")
    
    # Проверяем tkinter
    try:
        import tkinter
        print("✅ tkinter: доступен")
    except ImportError:
        print("❌ ОШИБКА: tkinter недоступен")
        print("   Установите: sudo apt-get install python3-tk")
        return 1
    
    # Проверяем sqlite3
    try:
        import sqlite3
        print(f"✅ SQLite версия: {sqlite3.sqlite_version}")
    except ImportError:
        print("❌ ОШИБКА: sqlite3 недоступен")
        return 1
    
    # Проверяем основные файлы
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_file = os.path.join(script_dir, "db_manager.py")
    dialogs_file = os.path.join(script_dir, "dialogs.py")
    
    if not os.path.exists(main_file):
        print(f"❌ ОШИБКА: Файл {main_file} не найден")
        return 1
    
    if not os.path.exists(dialogs_file):
        print(f"⚠️  ПРЕДУПРЕЖДЕНИЕ: Файл {dialogs_file} не найден")
        print("   Некоторые диалоги могут быть недоступны")
    else:
        print("✅ Все файлы найдены")
    
    print("\n🚀 Запуск программы...")
    print("-" * 60)
    
    # Запускаем основную программу
    try:
        # Добавляем текущую папку в путь для импортов
        sys.path.insert(0, script_dir)
        
        # Импортируем и запускаем
        from db_manager import DatabaseManager
        
        app = DatabaseManager()
        app.run()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n👋 Программа завершена пользователем")
        return 0
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
        print("\nДля отладки запустите:")
        print(f"   python3 {main_file}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    if exit_code != 0:
        input("\nНажмите Enter для выхода...")
    sys.exit(exit_code)