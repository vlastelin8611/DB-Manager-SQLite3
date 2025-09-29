#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест для воспроизведения проблемы с добавлением TEXT поля
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_field_creation():
    """Тест создания поля с типом TEXT"""
    
    print("🧪 Тест создания поля с типом TEXT")
    print("=" * 50)
    
    try:
        # Импортируем с логированием
        import db_manager
        import dialogs
        import sqlite3
        import tempfile
        
        print("✅ Модули импортированы")
        
        # Создаем временную БД
        temp_db = tempfile.mktemp(suffix='.db')
        conn = sqlite3.connect(temp_db)
        print(f"✅ Временная БД создана: {temp_db}")
        
        # Создаем главное окно
        root = tk.Tk()
        root.withdraw()  # Скрываем главное окно
        
        print("🔧 Тестируем CreateTableDialog...")
        
        # Создаем диалог создания таблицы
        dialog = dialogs.CreateTableDialog(root, conn)
        
        print("✅ CreateTableDialog создан")
        
        # Симулируем добавление поля TEXT
        print("🔧 Симулируем FieldDialog...")
        
        # Мокаем результат FieldDialog
        class MockFieldDialog:
            def __init__(self, parent):
                self.result = ("test_field", "TEXT", False, "", False)
                print(f"📝 Мок FieldDialog создан с результатом: {self.result}")
        
        # Заменяем FieldDialog на мок
        original_field_dialog = dialogs.FieldDialog
        dialogs.FieldDialog = MockFieldDialog
        
        print("🔧 Добавляем поле через add_field()...")
        
        try:
            # Вызываем add_field
            dialog.add_field()
            print("✅ add_field() выполнен")
            
            # Проверяем содержимое дерева
            children = dialog.fields_tree.get_children()
            print(f"📊 Полей в дереве: {len(children)}")
            
            if children:
                for i, child in enumerate(children):
                    item_data = dialog.fields_tree.item(child)
                    print(f"Поле {i+1}: text='{item_data['text']}', values={item_data['values']}")
                    
                    # Проверяем тип первого поля
                    if item_data['values'] and len(item_data['values']) > 0:
                        field_type = item_data['values'][0]
                        print(f"🎯 Тип поля: '{field_type}' (ожидался TEXT)")
                        
                        if field_type == "TEXT":
                            print("✅ Тип поля корректен!")
                        else:
                            print(f"❌ ПРОБЛЕМА: ожидался TEXT, получен {field_type}")
            else:
                print("❌ Поля не добавлены в дерево")
                
        finally:
            # Восстанавливаем оригинальный FieldDialog
            dialogs.FieldDialog = original_field_dialog
            
        # Закрываем диалог
        dialog.dialog.destroy()
        root.destroy()
        conn.close()
        
        print("✅ Тест завершен")
        
        # Проверяем логи
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        if os.path.exists(log_dir):
            log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
            if log_files:
                latest_log = os.path.join(log_dir, sorted(log_files)[-1])
                print(f"\n📋 Проверьте лог файл для деталей: {latest_log}")
        
        os.unlink(temp_db)
        
    except Exception as e:
        print(f"❌ Ошибка в тесте: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_field_creation()
    input("\nНажмите Enter для завершения...")