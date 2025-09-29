#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест функционала программы - создание таблицы с отслеживанием процесса
"""

import sys
import os
import sqlite3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_manager import DatabaseManager
import tempfile

def test_table_creation_trace():
    """Тестируем создание таблицы с детальным отслеживанием"""
    
    # Создаем временную БД
    temp_db = tempfile.mktemp(suffix='.db')
    print(f"🗄️ Создана временная БД: {temp_db}")
    
    try:
        # Создаем подключение к БД
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # Тестируем SQL генерацию как в программе
        print("\n1️⃣ Тест SQL генерации:")
        
        # Симулируем данные полей как в программе
        fields_data = [
            {'name': 'id', 'type': 'INTEGER', 'primary_key': True, 'auto_increment': True, 'not_null': False},
            {'name': 'username', 'type': 'TEXT', 'primary_key': False, 'auto_increment': False, 'not_null': True},
            {'name': 'email', 'type': 'TEXT', 'primary_key': False, 'auto_increment': False, 'not_null': False},
            {'name': 'age', 'type': 'INTEGER', 'primary_key': False, 'auto_increment': False, 'not_null': False}
        ]
        
        table_name = "users_test"
        
        # Генерируем SQL как в программе (упрощенно)
        sql_parts = []
        sql_parts.append(f'CREATE TABLE "{table_name}" (')
        
        field_definitions = []
        for field in fields_data:
            field_def = f'"{field["name"]}" {field["type"]}'
            
            if field.get('primary_key') and field.get('auto_increment'):
                field_def += ' PRIMARY KEY AUTOINCREMENT'
            elif field.get('primary_key'):
                field_def += ' PRIMARY KEY'
                
            if field.get('not_null') and not field.get('primary_key'):
                field_def += ' NOT NULL'
                
            field_definitions.append(field_def)
        
        sql_parts.append('    ' + ',\n    '.join(field_definitions))
        sql_parts.append(')')
        
        sql = '\n'.join(sql_parts)
        
        print(f"📝 Сгенерированный SQL:")
        print(sql)
        print()
        
        # Выполняем SQL
        cursor.execute(sql)
        conn.commit()
        print("✅ SQL выполнен успешно")
        
        # Проверяем результат
        cursor.execute(f'PRAGMA table_info("{table_name}")')
        columns = cursor.fetchall()
        
        print(f"\n📊 Реальная структура созданной таблицы:")
        for col in columns:
            cid, name, col_type, notnull, default, pk = col
            print(f"   '{name}': {col_type} | NOT NULL: {bool(notnull)} | PK: {bool(pk)}")
            
            # Сравниваем с ожидаемым
            expected_field = next((f for f in fields_data if f['name'] == name), None)
            if expected_field:
                expected_type = expected_field['type']
                if col_type != expected_type:
                    print(f"   ❌ НЕСООТВЕТСТВИЕ: ожидался {expected_type}, получен {col_type}")
                else:
                    print(f"   ✅ Тип корректен")
        
        # Тест 2: Проверяем с типами как в реальной программе
        print(f"\n2️⃣ Тест с данными из Combobox программы:")
        
        # Возможные значения типов из программы
        type_values = ['INTEGER', 'TEXT', 'REAL', 'BLOB', 'NUMERIC']
        
        for i, type_name in enumerate(type_values):
            field_name = f"test_{type_name.lower()}_field"
            
            # Создаем таблицу для каждого типа
            test_table = f"type_test_{i}"
            test_sql = f'CREATE TABLE "{test_table}" ("id" INTEGER PRIMARY KEY, "{field_name}" {type_name})'
            
            print(f"   Тестируем тип {type_name}:")
            print(f"   SQL: {test_sql}")
            
            cursor.execute(test_sql)
            conn.commit()
            
            # Проверяем
            cursor.execute(f'PRAGMA table_info("{test_table}")')
            test_columns = cursor.fetchall()
            
            for col in test_columns:
                cid, name, col_type, notnull, default, pk = col
                if name == field_name:
                    if col_type == type_name:
                        print(f"   ✅ {type_name}: корректно сохранен как {col_type}")
                    else:
                        print(f"   ❌ {type_name}: ожидался, получен {col_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тесте: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        try:
            conn.close()
            os.remove(temp_db)
        except:
            pass

def test_combobox_values():
    """Тестируем значения которые могут быть в Combobox"""
    
    print(f"\n3️⃣ Тест значений Combobox:")
    
    # Значения из программы (dialogs.py)
    type_values = ['INTEGER', 'TEXT', 'REAL', 'BLOB', 'NUMERIC']
    
    print("Доступные типы в программе:")
    for i, val in enumerate(type_values):
        print(f"   {i}: '{val}' (тип: {type(val)})")
    
    # Симулируем выбор пользователя
    print(f"\nСимуляция выбора пользователя:")
    for val in type_values:
        selected = val  # Как будто пользователь выбрал
        print(f"   Пользователь выбрал: '{selected}'")
        print(f"   Тип Python: {type(selected)}")
        print(f"   Длина: {len(selected)}")
        print(f"   repr(): {repr(selected)}")
        
        # Проверяем, что произойдет в SQL
        sql_fragment = f'"test_field" {selected}'
        print(f"   В SQL: {sql_fragment}")
        print()

if __name__ == "__main__":
    print("=" * 70)
    print("🔬 ДЕТАЛЬНЫЙ ТЕСТ СОЗДАНИЯ ТАБЛИЦ")
    print("=" * 70)
    
    try:
        success1 = test_table_creation_trace()
        test_combobox_values()
        
        print("\n" + "=" * 70)
        if success1:
            print("✅ Тесты SQL и типов данных прошли успешно")
            print("💭 Если проблема все еще есть, она может быть в:")
            print("   1. Интерфейсе программы (отображение)")
            print("   2. Обработке событий tkinter")
            print("   3. Передаче данных между диалогами")
            print("   4. Конвертации данных где-то в коде")
        else:
            print("❌ Найдены проблемы в SQL или типах")
            
    except Exception as e:
        print(f"❌ Критическая ошибка: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("=" * 70)
    input("Нажмите Enter для завершения...")