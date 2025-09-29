#!/bin/bash
# Скрипт установки и настройки SQLite Database Manager для AstraLinux

set -e

echo "============================================="
echo "Установка SQLite Database Manager"
echo "============================================="
echo ""

# Определяем директории
INSTALL_DIR="$HOME/Programs/SQLiteManager"
DESKTOP_FILE="$HOME/.local/share/applications/sqlite-manager.desktop"

# Создаем директорию установки
echo "📁 Создание директории установки..."
mkdir -p "$INSTALL_DIR"

# Копируем файлы
echo "📋 Копирование файлов программы..."
cp *.py "$INSTALL_DIR/"
cp *.md "$INSTALL_DIR/" 2>/dev/null || true
cp start.sh "$INSTALL_DIR/"

# Делаем файлы исполняемыми
chmod +x "$INSTALL_DIR/db_manager.py"
chmod +x "$INSTALL_DIR/run.py"
chmod +x "$INSTALL_DIR/start.sh"

# Создаем ярлык на рабочем столе
echo "🖥️  Создание ярлыка..."
mkdir -p "$(dirname "$DESKTOP_FILE")"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=SQLite Database Manager
Name[ru]=Менеджер баз данных SQLite
Comment=Database management tool for SQLite
Comment[ru]=Инструмент управления базами данных SQLite
Exec=python3 "$INSTALL_DIR/db_manager.py"
Icon=applications-databases
Terminal=false
Categories=Development;Database;
StartupNotify=true
EOF

# Делаем ярлык исполняемым
chmod +x "$DESKTOP_FILE"

# Создаем папку для бэкапов
echo "💾 Создание папки для резервных копий..."
mkdir -p "$HOME/db_backups"

echo ""
echo "✅ Установка завершена!"
echo ""
echo "📍 Программа установлена в: $INSTALL_DIR"
echo "🖥️  Ярлык создан в меню приложений"
echo "💾 Папка бэкапов: $HOME/db_backups"
echo ""
echo "🚀 Способы запуска:"
echo "   1. Через меню приложений: SQLite Database Manager"
echo "   2. Из терминала: $INSTALL_DIR/start.sh"
echo "   3. Прямой запуск: python3 $INSTALL_DIR/db_manager.py"
echo ""
echo "📚 Документация: $INSTALL_DIR/README.md"
echo "💡 Примеры использования: $INSTALL_DIR/EXAMPLES.md"