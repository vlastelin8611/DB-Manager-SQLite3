#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест для проверки проблемы с типами данных
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import tempfile

def test_field_type_issue():
    """Тестируем проблему с типами данных"""
    
    # Создаем временную БД
    temp_db = tempfile.mktemp(suffix='.db')
    conn = sqlite3.connect(temp_db)
    
    # Импортируем диалог
    try:
        from dialogs import CreateTableDialog
    except ImportError:
        print("❌ Не удалось импортировать dialogs.py")
        return
    
    # Создаем главное окно
    root = tk.Tk()
    root.title("Тест типов данных")
    root.geometry("600x400")
    
    info_label = ttk.Label(root, text="Тест создания поля с типом TEXT\n\n"
                          "1. Нажмите 'Создать таблицу'\n"
                          "2. Добавьте поле с типом TEXT\n"
                          "3. Проверьте отладочные сообщения\n"
                          "4. Создайте таблицу\n"
                          "5. Проверьте структуру БД")
    info_label.pack(pady=20)
    
    def test_create_table():
        dialog = CreateTableDialog(root, conn)
        if dialog.result:
            # Показываем структуру созданной таблицы
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            if tables:
                table_name = tables[-1][0]  # Последняя созданная таблица
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                structure = f"Структура таблицы '{table_name}':\n\n"
                for col in columns:
                    cid, name, col_type, notnull, default, pk = col
                    structure += f"Поле: {name}\n"
                    structure += f"  Тип: {col_type}\n"
                    structure += f"  NOT NULL: {bool(notnull)}\n"
                    structure += f"  По умолчанию: {default}\n"
                    structure += f"  Первичный ключ: {bool(pk)}\n\n"
                
                # Показываем SQL создания
                cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table_name}'")
                sql = cursor.fetchone()
                if sql:
                    structure += f"SQL создания:\n{sql[0]}"
                
                messagebox.showinfo("Структура созданной таблицы", structure)
            else:
                messagebox.showinfo("Информация", "Таблицы не созданы")
    
    def show_all_tables():
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if tables:
            table_info = "Все таблицы в БД:\n\n"
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                table_info += f"Таблица: {table_name}\n"
                for col in columns:
                    cid, name, col_type, notnull, default, pk = col
                    table_info += f"  {name}: {col_type}\n"
                table_info += "\n"
            
            messagebox.showinfo("Все таблицы", table_info)
        else:
            messagebox.showinfo("Информация", "Таблиц нет")
    
    ttk.Button(root, text="Создать таблицу", command=test_create_table).pack(pady=10)
    ttk.Button(root, text="Показать все таблицы", command=show_all_tables).pack(pady=5)
    ttk.Button(root, text="Выход", command=root.destroy).pack(pady=5)
    
    root.mainloop()
    
    conn.close()

if __name__ == "__main__":
    test_field_type_issue()