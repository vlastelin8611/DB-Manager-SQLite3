#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест исправления проблемы с добавлением полей
"""

import sys
import os
import tkinter as tk
import sqlite3
import tempfile

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_field_addition_fix():
    """Тест исправления добавления полей"""
    
    print("🔧 Тест исправления добавления полей")
    print("=" * 50)
    
    try:
        # Импортируем модули
        import dialogs
        
        # Создаем временную БД
        temp_db = tempfile.mktemp(suffix='.db')
        conn = sqlite3.connect(temp_db)
        
        # Создаем главное окно
        root = tk.Tk()
        root.withdraw()
        
        print("✅ Создаем CreateTableDialog...")
        
        # Создаем диалог
        dialog = dialogs.CreateTableDialog(root, conn)
        
        print("✅ Диалог создан")
        print("🎯 Теперь попробуйте:")
        print("   1. Введите имя таблицы: test_table")
        print("   2. Нажмите 'Добавить поле'")
        print("   3. Введите имя поля: description")
        print("   4. Выберите тип: TEXT") 
        print("   5. Нажмите OK")
        print("   6. Поле должно появиться в списке!")
        print("   7. Нажмите 'Создать таблицу'")
        
        # Чистим
        conn.close()
        os.unlink(temp_db)
        
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_field_addition_fix()