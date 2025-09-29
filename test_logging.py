#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест для проверки системы логирования
"""

import sys
import os

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔍 Тест системы логирования")
    print("=" * 50)
    
    # Импортируем модуль с логированием
    print("Импортируем db_manager...")
    import db_manager
    
    print("✅ db_manager импортирован успешно")
    print(f"Логгер создан: {db_manager.logger}")
    
    # Проверяем импорт диалогов
    print("Импортируем dialogs...")
    import dialogs
    
    print("✅ dialogs импортированы успешно")
    print(f"Логгер диалогов: {dialogs.logger}")
    
    # Проверяем создание лог файлов
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    if os.path.exists(log_dir):
        log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
        print(f"✅ Папка logs создана, файлов: {len(log_files)}")
        
        if log_files:
            latest_log = os.path.join(log_dir, sorted(log_files)[-1])
            print(f"Последний лог файл: {latest_log}")
            
            # Читаем несколько строк из лога
            try:
                with open(latest_log, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-10:]  # Последние 10 строк
                    print("Последние записи в логе:")
                    for line in lines:
                        print(f"  {line.strip()}")
            except Exception as e:
                print(f"Ошибка чтения лога: {e}")
        else:
            print("❌ Лог файлы не найдены")
    else:
        print("❌ Папка logs не создана")
    
    print("\n🎯 Тест логирования завершен")
    
except Exception as e:
    print(f"❌ Ошибка при тесте логирования: {str(e)}")
    import traceback
    traceback.print_exc()

print("\nНажмите Enter для завершения...")
input()