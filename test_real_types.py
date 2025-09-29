#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест создания таблицы для проверки проблемы с типами
"""

import sqlite3
import tempfile
import os

def create_test_table():
    """Создаем тестовую таблицу как программа и проверяем результат"""
    
    # Создаем временную БД
    temp_db = tempfile.mktemp(suffix='.db')
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    try:
        # SQL который должна генерировать программа для поля TEXT
        sql1 = '''CREATE TABLE "test1" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "name" TEXT NOT NULL,
            "description" TEXT
        )'''
        
        print("1️⃣ Создаем таблицу с полями TEXT:")
        print(f"SQL: {sql1}")
        
        cursor.execute(sql1)
        conn.commit()
        
        # Проверяем структуру
        cursor.execute('PRAGMA table_info("test1")')
        columns = cursor.fetchall()
        
        print("📊 Структура созданной таблицы:")
        for col in columns:
            cid, name, col_type, notnull, default, pk = col
            print(f"   Поле '{name}': тип '{col_type}', NOT NULL: {bool(notnull)}")
            
            # Проверяем конкретно проблемные поля
            if name == 'name':
                if col_type != 'TEXT':
                    print(f"   ❌ ПРОБЛЕМА: поле 'name' должно быть TEXT, а стало {col_type}")
                else:
                    print(f"   ✅ Поле 'name' корректно: {col_type}")
            
            if name == 'description':
                if col_type != 'TEXT':
                    print(f"   ❌ ПРОБЛЕМА: поле 'description' должно быть TEXT, а стало {col_type}")
                else:
                    print(f"   ✅ Поле 'description' корректно: {col_type}")
        
        # Тест 2: более сложная таблица
        print(f"\n2️⃣ Создаем таблицу со всеми типами данных:")
        
        sql2 = '''CREATE TABLE "test2" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "text_field" TEXT,
            "int_field" INTEGER,
            "real_field" REAL,
            "blob_field" BLOB,
            "numeric_field" NUMERIC
        )'''
        
        print(f"SQL: {sql2}")
        cursor.execute(sql2)
        conn.commit()
        
        cursor.execute('PRAGMA table_info("test2")')
        columns = cursor.fetchall()
        
        print("📊 Структура таблицы со всеми типами:")
        expected_types = {
            'text_field': 'TEXT',
            'int_field': 'INTEGER', 
            'real_field': 'REAL',
            'blob_field': 'BLOB',
            'numeric_field': 'NUMERIC'
        }
        
        for col in columns:
            cid, name, col_type, notnull, default, pk = col
            if name in expected_types:
                expected = expected_types[name]
                if col_type == expected:
                    print(f"   ✅ {name}: {col_type} (корректно)")
                else:
                    print(f"   ❌ {name}: ожидался {expected}, получен {col_type}")
            else:
                print(f"   📝 {name}: {col_type}")
        
        print(f"\n3️⃣ Проверяем работу с данными:")
        
        # Вставляем тестовые данные
        cursor.execute('''INSERT INTO test1 (name, description) VALUES (?, ?)''',
                      ('Тестовое имя', 'Тестовое описание'))
        
        cursor.execute('''INSERT INTO test2 (text_field, int_field, real_field) VALUES (?, ?, ?)''',
                      ('Текст', 42, 3.14))
        
        conn.commit()
        
        # Читаем данные
        cursor.execute('SELECT * FROM test1')
        row1 = cursor.fetchone()
        print(f"   Данные из test1: {row1}")
        print(f"   Тип поля name: {type(row1[1])}")
        print(f"   Тип поля description: {type(row1[2])}")
        
        cursor.execute('SELECT * FROM test2')
        row2 = cursor.fetchone()
        print(f"   Данные из test2: {row2}")
        if row2:
            print(f"   text_field: {row2[1]} (тип: {type(row2[1])})")
            print(f"   int_field: {row2[2]} (тип: {type(row2[2])})")
            print(f"   real_field: {row2[3]} (тип: {type(row2[3])})")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return False
        
    finally:
        conn.close()
        try:
            os.remove(temp_db)
        except:
            pass

if __name__ == "__main__":
    print("=" * 60)
    print("🔬 ТЕСТ СОЗДАНИЯ ТАБЛИЦ С РАЗНЫМИ ТИПАМИ ДАННЫХ")
    print("=" * 60)
    
    success = create_test_table()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Тест завершен успешно")
        print("💡 Если все типы корректны, проблема может быть в:")
        print("   - Отображении в программе")  
        print("   - Интерпретации пользователем")
        print("   - Конкретном сценарии использования")
    else:
        print("❌ Тест провален - есть реальные проблемы")
    
    print("=" * 60)
    input("Нажмите Enter для завершения...")