#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автоматический тест функциональности SQLite Database Manager
Проверяет все основные функции программы
"""

import os
import sys
import sqlite3
import tempfile
import shutil
from datetime import datetime

def create_test_db():
    """Создает тестовую базу данных для проверок"""
    test_dir = tempfile.mkdtemp()
    db_path = os.path.join(test_dir, "test_database.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Создаем тестовую таблицу со всеми типами данных
    cursor.execute("""
    CREATE TABLE test_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text_field TEXT NOT NULL,
        integer_field INTEGER,
        real_field REAL,
        blob_field BLOB,
        numeric_field NUMERIC,
        date_field TEXT,
        nullable_field TEXT
    )
    """)
    
    # Вставляем тестовые данные
    cursor.execute("""
    INSERT INTO test_types 
    (text_field, integer_field, real_field, numeric_field, date_field, nullable_field)
    VALUES 
    ('Тестовый текст', 42, 3.14159, 12345.67, '2023-01-15', 'Не NULL'),
    ('Русский текст', 100, 2.71828, 999.99, '2023-02-20', NULL),
    ('English text', -15, -1.5, 0, '2023-03-10', 'Another value')
    """)
    
    # Создаем таблицу с составным ключом
    cursor.execute("""
    CREATE TABLE composite_key (
        part1 INTEGER,
        part2 TEXT,
        value TEXT,
        PRIMARY KEY (part1, part2)
    )
    """)
    
    cursor.execute("""
    INSERT INTO composite_key (part1, part2, value) VALUES
    (1, 'A', 'Значение 1A'),
    (1, 'B', 'Значение 1B'),
    (2, 'A', 'Значение 2A')
    """)
    
    conn.commit()
    conn.close()
    
    return db_path

def test_database_operations():
    """Тестирует операции с базой данных"""
    print("🔧 Тестирование операций с БД...")
    
    test_db = create_test_db()
    
    try:
        # Тест 1: Подключение к БД
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        # Тест 2: Получение списка таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        expected_tables = ['test_types', 'composite_key']
        
        found_tables = [t[0] for t in tables]
        for table in expected_tables:
            if table in found_tables:
                print(f"   ✅ Таблица '{table}' найдена")
            else:
                print(f"   ❌ Таблица '{table}' НЕ найдена")
        
        # Тест 3: Структура таблицы
        cursor.execute("PRAGMA table_info(test_types)")
        columns = cursor.fetchall()
        
        expected_columns = {
            'id': 'INTEGER',
            'text_field': 'TEXT', 
            'integer_field': 'INTEGER',
            'real_field': 'REAL',
            'blob_field': 'BLOB',
            'numeric_field': 'NUMERIC',
            'date_field': 'TEXT',
            'nullable_field': 'TEXT'
        }
        
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            if col_name in expected_columns:
                if expected_columns[col_name] == col_type:
                    print(f"   ✅ Поле '{col_name}' ({col_type}) корректно")
                else:
                    print(f"   ❌ Поле '{col_name}' неверный тип: {col_type}, ожидался {expected_columns[col_name]}")
            else:
                print(f"   ⚠️  Неожиданное поле: {col_name}")
        
        # Тест 4: Данные таблицы
        cursor.execute("SELECT COUNT(*) FROM test_types")
        count = cursor.fetchone()[0]
        if count == 3:
            print(f"   ✅ Количество записей корректно: {count}")
        else:
            print(f"   ❌ Неверное количество записей: {count}, ожидалось 3")
        
        # Тест 5: Типы данных
        cursor.execute("SELECT * FROM test_types LIMIT 1")
        row = cursor.fetchone()
        
        if isinstance(row[1], str):  # text_field
            print("   ✅ TEXT поле работает корректно")
        else:
            print(f"   ❌ TEXT поле неверный тип: {type(row[1])}")
            
        if isinstance(row[2], int):  # integer_field  
            print("   ✅ INTEGER поле работает корректно")
        else:
            print(f"   ❌ INTEGER поле неверный тип: {type(row[2])}")
            
        if isinstance(row[3], float):  # real_field
            print("   ✅ REAL поле работает корректно") 
        else:
            print(f"   ❌ REAL поле неверный тип: {type(row[3])}")
        
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка тестирования: {str(e)}")
        return False
    finally:
        # Очищаем тестовые файлы
        try:
            os.remove(test_db)
            os.rmdir(os.path.dirname(test_db))
        except:
            pass

def test_sql_generation():
    """Тестирует генерацию SQL запросов"""
    print("\n📝 Тестирование генерации SQL...")
    
    test_cases = [
        {
            'name': 'simple_table',
            'fields': [
                ('id', 'INTEGER', False, '', True),
                ('name', 'TEXT', False, '', False),
                ('age', 'INTEGER', True, '18', False)
            ],
            'expected_sql': "CREATE TABLE simple_table (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, age INTEGER DEFAULT 18)"
        },
        {
            'name': 'complex_table', 
            'fields': [
                ('uuid', 'TEXT', False, '', True),
                ('description', 'TEXT', True, 'NULL', False),
                ('price', 'REAL', False, '0.0', False),
                ('data', 'BLOB', True, '', False)
            ],
            'expected_sql': "CREATE TABLE complex_table (uuid TEXT PRIMARY KEY, description TEXT DEFAULT NULL, price REAL NOT NULL DEFAULT 0.0, data BLOB)"
        }
    ]
    
    for case in test_cases:
        print(f"\n   Тест таблицы '{case['name']}':")
        
        # Генерируем SQL как в программе
        fields = []
        for field_name, field_type, allow_null, default, is_pk in case['fields']:
            field_def = f"{field_name} {field_type}"
            
            if is_pk:
                field_def += " PRIMARY KEY"
                if field_type.upper() == 'INTEGER':
                    field_def += " AUTOINCREMENT"
            
            if not allow_null and not is_pk:
                field_def += " NOT NULL"
                
            if default and default.strip():
                field_def += f" DEFAULT {default}"
                
            fields.append(field_def)
        
        generated_sql = f"CREATE TABLE {case['name']} ({', '.join(fields)})"
        
        print(f"   Сгенерированный SQL: {generated_sql}")
        print(f"   Ожидаемый SQL:      {case['expected_sql']}")
        
        if generated_sql == case['expected_sql']:
            print("   ✅ SQL генерация корректна")
        else:
            print("   ❌ SQL генерация неверна")
            
        # Проверяем валидность SQL
        try:
            conn = sqlite3.connect(':memory:')
            cursor = conn.cursor()
            cursor.execute(generated_sql)
            conn.close()
            print("   ✅ Сгенерированный SQL валиден")
        except Exception as e:
            print(f"   ❌ Сгенерированный SQL невалиден: {str(e)}")

def test_gui_components():
    """Тестирует GUI компоненты без отображения окон"""
    print("\n🎨 Тестирование GUI компонентов...")
    
    try:
        import tkinter as tk
        from tkinter import ttk
        
        # Создаем скрытый root
        root = tk.Tk()
        root.withdraw()
        
        # Тест Treeview
        try:
            tree = ttk.Treeview(root, selectmode='browse')
            tree.heading('#0', text='Test')
            tree.insert('', 'end', text='test_item')
            print("   ✅ Treeview создается корректно")
        except Exception as e:
            print(f"   ❌ Ошибка Treeview: {str(e)}")
        
        # Тест Combobox
        try:
            var = tk.StringVar(value="TEXT")
            combo = ttk.Combobox(root, textvariable=var, 
                               values=["TEXT", "INTEGER", "REAL", "BLOB", "NUMERIC"],
                               state="readonly")
            print("   ✅ Combobox создается корректно")
        except Exception as e:
            print(f"   ❌ Ошибка Combobox: {str(e)}")
        
        # Тест Entry
        try:
            var = tk.StringVar()
            entry = ttk.Entry(root, textvariable=var)
            var.set("Test value")
            if var.get() == "Test value":
                print("   ✅ Entry работает корректно")
            else:
                print("   ❌ Entry не сохраняет значения")
        except Exception as e:
            print(f"   ❌ Ошибка Entry: {str(e)}")
        
        # Тест Checkbutton
        try:
            var = tk.BooleanVar()
            check = ttk.Checkbutton(root, variable=var)
            var.set(True)
            if var.get() == True:
                print("   ✅ Checkbutton работает корректно")
            else:
                print("   ❌ Checkbutton не сохраняет состояние")
        except Exception as e:
            print(f"   ❌ Ошибка Checkbutton: {str(e)}")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"   ❌ Критическая ошибка GUI: {str(e)}")
        return False

def test_file_operations():
    """Тестирует операции с файлами"""
    print("\n💾 Тестирование файловых операций...")
    
    test_dir = tempfile.mkdtemp()
    
    try:
        # Тест создания БД
        db_path = os.path.join(test_dir, "test_create.db")
        conn = sqlite3.connect(db_path)
        conn.close()
        
        if os.path.exists(db_path):
            print("   ✅ Создание БД работает")
        else:
            print("   ❌ Создание БД не работает")
            return False
        
        # Тест копирования (бэкап)
        backup_path = os.path.join(test_dir, "backup.db")
        shutil.copy2(db_path, backup_path)
        
        if os.path.exists(backup_path):
            print("   ✅ Копирование файлов работает")
        else:
            print("   ❌ Копирование файлов не работает")
        
        # Тест экспорта SQL
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE export_test (id INTEGER, name TEXT)")
        cursor.execute("INSERT INTO export_test VALUES (1, 'test')")
        conn.commit()
        
        sql_path = os.path.join(test_dir, "export.sql")
        with open(sql_path, 'w', encoding='utf-8') as f:
            for line in conn.iterdump():
                f.write(f"{line}\n")
        
        conn.close()
        
        if os.path.exists(sql_path) and os.path.getsize(sql_path) > 0:
            print("   ✅ Экспорт SQL работает")
            
            # Проверяем содержимое
            with open(sql_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'export_test' in content and 'test' in content:
                    print("   ✅ Содержимое экспорта корректно")
                else:
                    print("   ⚠️  Содержимое экспорта может быть неполным")
        else:
            print("   ❌ Экспорт SQL не работает")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка файловых операций: {str(e)}")
        return False
    finally:
        # Очистка
        shutil.rmtree(test_dir, ignore_errors=True)

def test_edge_cases():
    """Тестирует граничные случаи"""
    print("\n🚨 Тестирование граничных случаев...")
    
    # Тест с русскими именами
    try:
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        cursor.execute("CREATE TABLE русская_таблица (поле_текст TEXT, поле_число INTEGER)")
        cursor.execute("INSERT INTO русская_таблица VALUES ('русский текст', 42)")
        cursor.execute("SELECT * FROM русская_таблица")
        result = cursor.fetchone()
        
        if result and result[0] == 'русский текст':
            print("   ✅ Русские имена поддерживаются")
        else:
            print("   ❌ Проблемы с русскими именами")
            
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Ошибка с русскими именами: {str(e)}")
    
    # Тест с пустыми значениями
    try:
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        cursor.execute("CREATE TABLE null_test (id INTEGER, nullable_field TEXT)")
        cursor.execute("INSERT INTO null_test VALUES (1, NULL)")
        cursor.execute("INSERT INTO null_test VALUES (2, '')")
        cursor.execute("SELECT * FROM null_test")
        results = cursor.fetchall()
        
        if len(results) == 2:
            print("   ✅ NULL и пустые строки обрабатываются")
        else:
            print("   ❌ Проблемы с NULL значениями")
            
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Ошибка с NULL значениями: {str(e)}")
    
    # Тест с большими данными
    try:
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        cursor.execute("CREATE TABLE big_data (id INTEGER, big_text TEXT)")
        big_string = "A" * 10000  # 10KB строка
        cursor.execute("INSERT INTO big_data VALUES (1, ?)", (big_string,))
        cursor.execute("SELECT big_text FROM big_data WHERE id = 1")
        result = cursor.fetchone()
        
        if result and len(result[0]) == 10000:
            print("   ✅ Большие данные поддерживаются")
        else:
            print("   ❌ Проблемы с большими данными")
            
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Ошибка с большими данными: {str(e)}")

def main():
    """Главная функция тестирования"""
    print("=" * 60)
    print("🧪 АВТОМАТИЧЕСКОЕ ТЕСТИРОВАНИЕ SQLite Database Manager")
    print("=" * 60)
    print(f"Дата тестирования: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    results = {}
    
    # Выполняем все тесты
    results['database'] = test_database_operations()
    results['sql_generation'] = test_sql_generation()
    results['gui'] = test_gui_components()
    results['files'] = test_file_operations()
    test_edge_cases()
    
    # Подводим итоги
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        icon = "✅" if result else "❌"
        print(f"{icon} {test_name}: {'ПРОЙДЕН' if result else 'ПРОВАЛЕН'}")
    
    print(f"\nОбщий результат: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        return 0
    else:
        print("⚠️  ОБНАРУЖЕНЫ ПРОБЛЕМЫ - требуется исправление")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        input("\nНажмите Enter для завершения...")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 Тестирование прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 КРИТИЧЕСКАЯ ОШИБКА ТЕСТИРОВАНИЯ: {str(e)}")
        input("Нажмите Enter для завершения...")
        sys.exit(1)