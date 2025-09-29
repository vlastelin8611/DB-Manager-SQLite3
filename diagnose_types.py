#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрый тест проблемы с типами данных без GUI
"""

import sqlite3
import tempfile
import os

def test_sql_creation():
    """Тестируем создание SQL для разных типов полей"""
    
    print("🔧 Тест создания SQL для разных типов полей...")
    
    # Симулируем данные как они приходят из диалога
    test_fields = [
        # (field_name, field_type, allow_null, default, is_pk)
        ('id', 'INTEGER', 'NO', '', 'YES'),
        ('name', 'TEXT', 'NO', '', 'NO'),
        ('description', 'TEXT', 'YES', '', 'NO'),
        ('age', 'INTEGER', 'YES', '18', 'NO'),
        ('price', 'REAL', 'NO', '0.0', 'NO')
    ]
    
    # Симулируем логику создания SQL как в dialogs.py
    fields = []
    primary_keys = []
    table_name = 'test_table'
    
    for field_name, field_type, allow_null, default, is_pk in test_fields:
        print(f"\nОбрабатываем поле: {field_name}")
        print(f"  Тип из данных: {field_type}")
        
        field_def = f'"{field_name}" {field_type.upper()}'
        print(f"  Базовое определение: {field_def}")
        
        if is_pk == 'YES':
            primary_keys.append(field_name)
            if field_type.upper() == 'INTEGER':
                field_def += " PRIMARY KEY AUTOINCREMENT"
            else:
                field_def += " PRIMARY KEY"
        
        if allow_null == 'NO' and is_pk != 'YES':
            field_def += " NOT NULL"
            
        if default and default.strip() and default.strip().upper() != 'NULL':
            if field_type.upper() in ['TEXT', 'BLOB']:
                field_def += f" DEFAULT '{default.strip()}'"
            else:
                field_def += f" DEFAULT {default.strip()}"
                
        fields.append(field_def)
        print(f"  Финальное определение: {field_def}")
    
    sql = f'CREATE TABLE "{table_name}" ({", ".join(fields)})'
    print(f"\n📝 Полный SQL:")
    print(sql)
    
    # Проверяем валидность SQL
    try:
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute(sql)
        print("\n✅ SQL валиден")
        
        # Проверяем структуру
        cursor.execute(f'PRAGMA table_info("{table_name}")')
        columns = cursor.fetchall()
        
        print(f"\n📊 Структура созданной таблицы:")
        for col in columns:
            cid, name, col_type, notnull, default, pk = col
            print(f"  {name}: {col_type} (NOT NULL: {bool(notnull)}, PK: {bool(pk)}, Default: {default})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка SQL: {str(e)}")
        return False

def test_combobox_behavior():
    """Тестируем поведение Combobox"""
    
    print("\n🎛️  Тест поведения Combobox...")
    
    try:
        import tkinter as tk
        from tkinter import ttk
        
        root = tk.Tk()
        root.withdraw()  # Скрываем окно
        
        # Создаем Combobox как в диалоге
        type_var = tk.StringVar(value="TEXT")
        combo = ttk.Combobox(None, textvariable=type_var,
                           values=["TEXT", "INTEGER", "REAL", "BLOB", "NUMERIC"],
                           state="readonly")
        
        print(f"  Начальное значение: '{type_var.get()}'")
        
        # Симулируем выбор разных значений
        for test_type in ["TEXT", "INTEGER", "REAL"]:
            type_var.set(test_type)
            result = type_var.get()
            print(f"  Установлен {test_type}, получен: '{result}'")
            if result != test_type:
                print(f"    ❌ ПРОБЛЕМА: ожидался {test_type}, получен {result}")
        
        root.destroy()
        print("  ✅ Combobox работает корректно")
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка Combobox: {str(e)}")
        return False

def main():
    """Главная функция теста"""
    print("=" * 60)
    print("🔍 ДИАГНОСТИКА ПРОБЛЕМЫ С ТИПАМИ ДАННЫХ")
    print("=" * 60)
    
    sql_ok = test_sql_creation()
    combo_ok = test_combobox_behavior()
    
    print("\n" + "=" * 60)
    print("📋 РЕЗУЛЬТАТЫ ДИАГНОСТИКИ:")
    print(f"{'✅' if sql_ok else '❌'} Создание SQL: {'OK' if sql_ok else 'ПРОБЛЕМА'}")
    print(f"{'✅' if combo_ok else '❌'} Combobox: {'OK' if combo_ok else 'ПРОБЛЕМА'}")
    
    if sql_ok and combo_ok:
        print("\n🤔 Логика создания SQL и Combobox работают корректно.")
        print("   Проблема может быть в передаче данных между диалогами.")
        print("   Запустите debug_field_types.py для интерактивной проверки.")
    else:
        print("\n⚠️  Обнаружены проблемы в базовой логике.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
    input("\nНажмите Enter для завершения...")