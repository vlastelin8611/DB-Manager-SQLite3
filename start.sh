#!/bin/bash
# Скрипт запуска SQLite Database Manager для AstraLinux

echo "========================================"
echo "SQLite Database Manager для AstraLinux"
echo "========================================"
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python3:"
    echo "   sudo apt-get install python3"
    exit 1
fi

echo "✅ Python3 найден: $(python3 --version)"

# Проверка tkinter
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "❌ tkinter не найден. Установите:"
    echo "   sudo apt-get install python3-tk"
    exit 1
fi

echo "✅ tkinter доступен"

# Проверка sqlite3
if ! python3 -c "import sqlite3" 2>/dev/null; then
    echo "❌ sqlite3 не найден"
    exit 1
fi

echo "✅ sqlite3 доступен"

# Проверка файлов
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -f "$SCRIPT_DIR/db_manager.py" ]; then
    echo "❌ Файл db_manager.py не найден"
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/dialogs.py" ]; then
    echo "⚠️  Файл dialogs.py не найден, некоторые функции могут быть недоступны"
fi

echo "✅ Все проверки пройдены"
echo ""
echo "🚀 Запуск SQLite Database Manager..."
echo "----------------------------------------"

# Запуск программы
cd "$SCRIPT_DIR"
python3 db_manager.py

echo ""
echo "👋 Программа завершена"