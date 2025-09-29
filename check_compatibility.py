#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт проверки совместимости для SQLite Database Manager
Проверяет все зависимости и готовность системы к запуску
"""

import sys
import os
import platform
from datetime import datetime

def print_header():
    """Печатает заголовок проверки"""
    print("=" * 70)
    print("🔍 ПРОВЕРКА СОВМЕСТИМОСТИ SQLite Database Manager")
    print("=" * 70)
    print(f"Дата проверки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Операционная система: {platform.system()} {platform.release()}")
    print("-" * 70)

def check_python_version():
    """Проверяет версию Python"""
    print("📋 Проверка версии Python...")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version >= (3, 5):
        print(f"   ✅ Python {version_str} - совместим")
        return True
    else:
        print(f"   ❌ Python {version_str} - НЕ совместим (требуется 3.5+)")
        return False

def check_tkinter():
    """Проверяет доступность tkinter"""
    print("\n🖼️  Проверка графической библиотеки tkinter...")
    
    try:
        import tkinter as tk
        
        # Пробуем создать тестовое окно
        root = tk.Tk()
        root.withdraw()  # Скрываем окно
        
        # Проверяем базовые компоненты
        ttk_available = False
        try:
            from tkinter import ttk
            ttk_available = True
        except ImportError:
            pass
        
        root.destroy()
        
        print("   ✅ tkinter доступен")
        if ttk_available:
            print("   ✅ tkinter.ttk доступен")
        else:
            print("   ⚠️  tkinter.ttk недоступен (будут использованы базовые виджеты)")
            
        return True
        
    except ImportError:
        print("   ❌ tkinter недоступен")
        print("   💡 Установите: sudo apt-get install python3-tk")
        return False
    except Exception as e:
        print(f"   ⚠️  Проблема с tkinter: {str(e)}")
        return False

def check_sqlite3():
    """Проверяет доступность sqlite3"""
    print("\n💾 Проверка базы данных SQLite...")
    
    try:
        import sqlite3
        
        # Проверяем версию SQLite
        sqlite_version = sqlite3.sqlite_version
        python_sqlite_version = sqlite3.version
        
        print(f"   ✅ sqlite3 доступен (Python API: {python_sqlite_version})")
        print(f"   ✅ SQLite версия: {sqlite_version}")
        
        # Тестируем создание БД в памяти
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE test (id INTEGER)')
        cursor.execute('INSERT INTO test VALUES (1)')
        cursor.execute('SELECT * FROM test')
        result = cursor.fetchone()
        conn.close()
        
        if result == (1,):
            print("   ✅ SQLite функционирует корректно")
            return True
        else:
            print("   ⚠️  Проблема с функционированием SQLite")
            return False
            
    except ImportError:
        print("   ❌ sqlite3 недоступен")
        return False
    except Exception as e:
        print(f"   ❌ Ошибка SQLite: {str(e)}")
        return False

def check_standard_modules():
    """Проверяет стандартные модули Python"""
    print("\n📚 Проверка стандартных модулей...")
    
    modules = {
        'os': 'работа с файловой системой',
        'shutil': 'операции с файлами',
        'datetime': 'работа с датами',
        'threading': 'многопоточность',
        'json': 'работа с JSON'
    }
    
    all_available = True
    
    for module, description in modules.items():
        try:
            __import__(module)
            print(f"   ✅ {module} - {description}")
        except ImportError:
            print(f"   ❌ {module} - {description} [НЕДОСТУПЕН]")
            all_available = False
    
    return all_available

def check_file_structure():
    """Проверяет структуру файлов проекта"""
    print("\n📁 Проверка файлов проекта...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    required_files = {
        'db_manager.py': 'основной файл приложения',
        'dialogs.py': 'дополнительные диалоги'
    }
    
    optional_files = {
        'README.md': 'документация',
        'EXAMPLES.md': 'примеры использования',
        'run.py': 'скрипт запуска'
    }
    
    all_required = True
    
    print("   Обязательные файлы:")
    for filename, description in required_files.items():
        filepath = os.path.join(script_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"   ✅ {filename} - {description} ({size} байт)")
        else:
            print(f"   ❌ {filename} - {description} [НЕ НАЙДЕН]")
            all_required = False
    
    print("   Дополнительные файлы:")
    for filename, description in optional_files.items():
        filepath = os.path.join(script_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"   ✅ {filename} - {description} ({size} байт)")
        else:
            print(f"   ⚠️  {filename} - {description} [отсутствует]")
    
    return all_required

def check_permissions():
    """Проверяет права доступа"""
    print("\n🔐 Проверка прав доступа...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    home_dir = os.path.expanduser("~")
    
    # Проверка прав на чтение в папке программы
    if os.access(script_dir, os.R_OK):
        print("   ✅ Права на чтение файлов программы")
    else:
        print("   ❌ Нет прав на чтение файлов программы")
        return False
    
    # Проверка прав на запись в домашней папке
    if os.access(home_dir, os.W_OK):
        print("   ✅ Права на запись в домашней папке")
    else:
        print("   ⚠️  Нет прав на запись в домашней папке")
    
    # Проверка возможности создания папки бэкапов
    backup_dir = os.path.join(home_dir, "db_backups")
    try:
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            print("   ✅ Папка резервных копий создана")
        else:
            print("   ✅ Папка резервных копий существует")
        
        if os.access(backup_dir, os.W_OK):
            print("   ✅ Права на запись в папку бэкапов")
        else:
            print("   ⚠️  Нет прав на запись в папку бэкапов")
            
    except Exception as e:
        print(f"   ⚠️  Проблема с папкой бэкапов: {str(e)}")
    
    return True

def check_display():
    """Проверяет возможность отображения GUI"""
    print("\n🖥️  Проверка графического окружения...")
    
    # Проверяем переменную DISPLAY (для X11)
    display = os.environ.get('DISPLAY')
    if display:
        print(f"   ✅ DISPLAY установлен: {display}")
    else:
        print("   ⚠️  DISPLAY не установлен (может быть проблемой для SSH)")
    
    # Проверяем сеанс рабочего стола
    desktop = os.environ.get('XDG_CURRENT_DESKTOP')
    if desktop:
        print(f"   ✅ Рабочий стол: {desktop}")
    else:
        print("   ⚠️  Рабочий стол не определен")
    
    return True

def test_gui_creation():
    """Тестирует создание GUI"""
    print("\n🎨 Тест создания графического интерфейса...")
    
    try:
        import tkinter as tk
        from tkinter import ttk
        
        # Создаем тестовое окно
        root = tk.Tk()
        root.title("Тест GUI")
        root.geometry("300x200")
        
        # Добавляем виджеты
        label = ttk.Label(root, text="Тест успешен!")
        label.pack(pady=20)
        
        button = ttk.Button(root, text="OK", command=root.destroy)
        button.pack(pady=10)
        
        # Показываем окно на 2 секунды
        root.after(2000, root.destroy)
        
        print("   ✅ Тестовое окно будет показано на 2 секунды...")
        root.mainloop()
        
        print("   ✅ Графический интерфейс работает корректно")
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка создания GUI: {str(e)}")
        return False

def provide_recommendations(results):
    """Предоставляет рекомендации по результатам проверки"""
    print("\n" + "=" * 70)
    print("📋 РЕЗУЛЬТАТЫ И РЕКОМЕНДАЦИИ")
    print("=" * 70)
    
    all_passed = all(results.values())
    
    if all_passed:
        print("🎉 ОТЛИЧНО! Все проверки пройдены успешно.")
        print("\n✅ SQLite Database Manager готов к работе!")
        print("\n🚀 Для запуска используйте:")
        print("   python3 db_manager.py")
        print("   или")
        print("   python3 run.py")
        
    else:
        print("⚠️  Обнаружены проблемы, требующие внимания:")
        
        if not results['python']:
            print("\n❌ КРИТИЧНО: Обновите Python до версии 3.5 или новее")
            
        if not results['tkinter']:
            print("\n❌ КРИТИЧНО: Установите tkinter:")
            print("   sudo apt-get install python3-tk")
            
        if not results['sqlite']:
            print("\n❌ КРИТИЧНО: Проблема с SQLite")
            
        if not results['files']:
            print("\n❌ КРИТИЧНО: Отсутствуют необходимые файлы")
            
        if not results['modules']:
            print("\n⚠️  Отсутствуют некоторые стандартные модули")
            
        print(f"\n📊 Статус проверок:")
        for check, status in results.items():
            icon = "✅" if status else "❌"
            print(f"   {icon} {check}")

def main():
    """Главная функция проверки"""
    print_header()
    
    # Выполняем все проверки
    results = {
        'python': check_python_version(),
        'tkinter': check_tkinter(),
        'sqlite': check_sqlite3(),
        'modules': check_standard_modules(),
        'files': check_file_structure(),
        'permissions': check_permissions(),
        'display': check_display()
    }
    
    # Если основные компоненты работают, тестируем GUI
    if results['python'] and results['tkinter']:
        results['gui_test'] = test_gui_creation()
    else:
        results['gui_test'] = False
        print("\n🚫 Тест GUI пропущен из-за отсутствия зависимостей")
    
    # Предоставляем рекомендации
    provide_recommendations(results)
    
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        print(f"\n{'='*70}")
        input("Нажмите Enter для завершения...")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 Проверка прервана пользователем")
        sys.exit(1)