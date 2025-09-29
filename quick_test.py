#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрый тест основных функций без GUI
"""

import sqlite3
import tempfile
import os

def test_sql_generation():
    """Тестируем генерацию SQL с новой логикой"""
    print("🔧 Тестирование улучшенной генерации SQL...")
    
    # Имитируем данные из диалога создания таблицы
    test_cases = [
        {
            'name': 'users',
            'fields': [
                ('id', 'INTEGER', 'NO', '', 'YES'),
                ('name', 'TEXT', 'NO', '', 'NO'), 
                ('email', 'TEXT', 'YES', 'NULL', 'NO'),
                ('age', 'INTEGER', 'YES', '18', 'NO')
            ]
        },
        {
            'name': 'products',
            'fields': [
                ('category_id', 'INTEGER', 'NO', '', 'YES'),
                ('product_id', 'INTEGER', 'NO', '', 'YES'),
                ('name', 'TEXT', 'NO', '', 'NO'),
                ('price', 'REAL', 'NO', '0.0', 'NO')
            ]
        }
    ]
    
    for case in test_cases:
        table_name = case['name']
        fields_data = case['fields']
        
        print(f"\n   Таблица '{table_name}':")
        
        fields = []
        primary_keys = []
        
        for field_name, field_type, allow_null, default, is_pk in fields_data:
            field_def = f'"{field_name}" {field_type.upper()}'
            
            if is_pk == 'YES':
                primary_keys.append(field_name)
                if field_type.upper() == 'INTEGER' and len([pk for fn, ft, an, d, pk in fields_data if pk == 'YES']) == 1:
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
        
        # Составной первичный ключ
        if len(primary_keys) > 1:
            pk_fields = [f'"{pk}"' for pk in primary_keys]
            pk_constraint = f'PRIMARY KEY ({", ".join(pk_fields)})'
            fields.append(pk_constraint)
            
        sql = f'CREATE TABLE "{table_name}" ({", ".join(fields)})'
        print(f"   SQL: {sql}")
        
        # Проверяем валидность
        try:
            conn = sqlite3.connect(':memory:')
            cursor = conn.cursor()
            cursor.execute(sql)
            print("   ✅ SQL валиден")
            
            # Проверяем структуру
            cursor.execute(f'PRAGMA table_info("{table_name}")')
            columns = cursor.fetchall()
            print(f"   📊 Колонок создано: {len(columns)}")
            
            for col in columns:
                cid, name, col_type, notnull, default, pk = col
                print(f"      {name}: {col_type} (NULL: {'NO' if notnull else 'YES'}, PK: {'YES' if pk else 'NO'})")
            
            conn.close()
            
        except Exception as e:
            print(f"   ❌ Ошибка SQL: {str(e)}")

def test_data_operations():
    """Тестируем операции с данными"""
    print("\n💾 Тестирование операций с данными...")
    
    temp_db = tempfile.mktemp(suffix='.db')
    
    try:
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # Создаем тестовую таблицу
        cursor.execute('''
        CREATE TABLE "test_table" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "name" TEXT NOT NULL,
            "age" INTEGER DEFAULT 18,
            "email" TEXT
        )
        ''')
        
        print("   ✅ Таблица создана")
        
        # Вставляем данные разных типов
        test_data = [
            ('Алексей Иванов', 25, 'alex@example.com'),
            ('Мария Петрова', None, 'maria@example.com'),
            ('John Smith', 30, None),
            ('Тест Тестов', 18, 'test@test.ru')
        ]
        
        cursor.executemany(
            'INSERT INTO test_table (name, age, email) VALUES (?, ?, ?)', 
            test_data
        )
        conn.commit()
        
        print(f"   ✅ Вставлено {len(test_data)} записей")
        
        # Проверяем данные
        cursor.execute('SELECT * FROM test_table')
        results = cursor.fetchall()
        
        print(f"   📊 Получено записей: {len(results)}")
        
        for row in results:
            print(f"      ID: {row[0]}, Name: {row[1]}, Age: {row[2]}, Email: {row[3]}")
            
        # Тестируем поиск
        cursor.execute("SELECT * FROM test_table WHERE name LIKE '%Тест%'")
        search_results = cursor.fetchall()
        print(f"   🔍 Найдено по поиску 'Тест': {len(search_results)} записей")
        
        # Тестируем NULL значения
        cursor.execute("SELECT COUNT(*) FROM test_table WHERE age IS NULL")
        null_count = cursor.fetchone()[0]
        print(f"   ⚪ Записей с NULL в age: {null_count}")
        
        conn.close()
        print("   ✅ Тест операций с данными завершен")
        
    except Exception as e:
        print(f"   ❌ Ошибка операций с данными: {str(e)}")
    finally:
        try:
            os.remove(temp_db)
        except:
            pass

def test_backup_functionality():
    """Тестируем функциональность бэкапов"""
    print("\n💼 Тестирование бэкапов...")
    
    import shutil
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Создаем исходную БД
        source_db = os.path.join(temp_dir, 'source.db')
        conn = sqlite3.connect(source_db)
        cursor = conn.cursor()
        
        cursor.execute('CREATE TABLE backup_test (id INTEGER, data TEXT)')
        cursor.execute("INSERT INTO backup_test VALUES (1, 'test data')")
        conn.commit()
        conn.close()
        
        print("   ✅ Исходная БД создана")
        
        # Создаем бэкап
        backup_db = os.path.join(temp_dir, 'backup.db')
        shutil.copy2(source_db, backup_db)
        
        if os.path.exists(backup_db):
            print("   ✅ Бэкап создан")
            
            # Проверяем содержимое бэкапа
            conn = sqlite3.connect(backup_db)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM backup_test')
            result = cursor.fetchone()
            
            if result and result[0] == 1 and result[1] == 'test data':
                print("   ✅ Содержимое бэкапа корректно")
            else:
                print("   ❌ Содержимое бэкапа некорректно")
                
            conn.close()
        else:
            print("   ❌ Бэкап не создан")
            
    except Exception as e:
        print(f"   ❌ Ошибка бэкапа: {str(e)}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    """Главная функция тестирования"""
    print("=" * 60)
    print("🚀 БЫСТРЫЙ ТЕСТ ИСПРАВЛЕННОЙ ФУНКЦИОНАЛЬНОСТИ")
    print("=" * 60)
    
    test_sql_generation()
    test_data_operations() 
    test_backup_functionality()
    
    print("\n" + "=" * 60)
    print("✅ ВСЕ БЫСТРЫЕ ТЕСТЫ ЗАВЕРШЕНЫ")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        input("\nНажмите Enter для завершения...")
    except Exception as e:
        print(f"\n💥 ОШИБКА: {str(e)}")
        input("Нажмите Enter для завершения...")