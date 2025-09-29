#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест для проверки проблемы с типами данных
"""

import tkinter as tk
from tkinter import ttk

def test_combobox_issue():
    """Тест проблемы с Combobox типов"""
    
    print("🔍 ТЕСТ ПРОБЛЕМЫ С ТИПАМИ ДАННЫХ")
    print("=" * 50)
    
    # Создаем временное окно
    root = tk.Tk()
    root.withdraw()  # Скрываем главное окно
    
    # Тестируем Combobox как в программе
    type_var = tk.StringVar(value="TEXT")
    type_combo = ttk.Combobox(root, textvariable=type_var,
                             values=["TEXT", "INTEGER", "REAL", "BLOB", "NUMERIC"],
                             state="readonly")
    
    # Тестируем разные сценарии
    test_cases = ["TEXT", "INTEGER", "REAL", "BLOB", "NUMERIC"]
    
    print("Тестируем Combobox:")
    for test_value in test_cases:
        # Устанавливаем значение
        type_var.set(test_value)
        
        # Получаем значение
        retrieved = type_var.get()
        
        print(f"   Установлено: '{test_value}' -> Получено: '{retrieved}'")
        print(f"   Типы: set={type(test_value)} get={type(retrieved)}")
        print(f"   Равны: {test_value == retrieved}")
        
        # Тестируем индекс
        try:
            index = type_combo['values'].index(test_value)
            print(f"   Индекс в списке: {index}")
        except ValueError:
            print(f"   ❌ Значение не найдено в списке!")
        
        # Тестируем current()
        try:
            type_combo.current(index)
            current_value = type_combo.get()
            print(f"   current() возвращает: '{current_value}'")
        except:
            print(f"   ❌ Ошибка при использовании current()")
        
        print()
    
    root.destroy()
    
    # Теперь тестируем Tree как в программе  
    print("Тестируем TreeView:")
    print("-" * 30)
    
    root = tk.Tk()
    root.withdraw()
    
    tree = ttk.Treeview(root, columns=('type', 'null', 'default', 'pk'))
    
    # Добавляем тестовые записи
    test_fields = [
        ('field1', 'TEXT'),
        ('field2', 'INTEGER'),
        ('field3', 'REAL'),
        ('field4', 'BLOB'),
        ('field5', 'NUMERIC')
    ]
    
    for field_name, field_type in test_fields:
        # Добавляем в дерево
        item_id = tree.insert('', 'end', text=field_name, 
                             values=(field_type, 'YES', '', 'NO'))
        
        # Читаем обратно
        item_values = tree.item(item_id)['values']
        retrieved_type = item_values[0]
        
        print(f"   {field_name}: записан '{field_type}' -> прочитан '{retrieved_type}'")
        print(f"   Типы: записан={type(field_type)} прочитан={type(retrieved_type)}")
        print(f"   Равны: {field_type == retrieved_type}")
        print(f"   Полные values: {item_values}")
        print()
    
    root.destroy()
    
    print("✅ Тесты завершены")

if __name__ == "__main__":
    test_combobox_issue()
    input("Нажмите Enter для завершения...")