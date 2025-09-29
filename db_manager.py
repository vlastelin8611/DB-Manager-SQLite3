#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import sqlite3
import os
import shutil
import json
from datetime import datetime
import threading
import sys
import logging
import traceback

# Настройка системы логирования
def setup_logging():
    """подробное логирование для отладки"""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f'db_manager_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    # Настраиваем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # Файловый хендлер
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Консольный хендлер
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Настраиваем root logger
    logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, console_handler])
    
    logger = logging.getLogger('db_manager')
    logger.info(f"Логирование инициализировано. Файл лога: {log_file}")
    return logger

# Инициализируем логгер
logger = setup_logging()

# Импортируем дополнительные диалоги
try:
    from dialogs import (TableStructureDialog, EditRecordDialog, 
                        SQLQueryDialog, SettingsDialog, CreateTableDialog, FieldDialog)
    logger.info("Успешно импортированы все диалоги")
except ImportError as e:
    logger.error(f"Ошибка импорта диалогов: {e}")
    # Если файл dialogs.py не найден, определяем заглушки
    class TableStructureDialog:
        def __init__(self, *args, **kwargs):
            logger.error("Попытка использования недоступного TableStructureDialog")
            messagebox.showinfo("Информация", "Диалог структуры таблицы недоступен")
    
    class EditRecordDialog:
        def __init__(self, *args, **kwargs):
            logger.error("Попытка использования недоступного EditRecordDialog")
            messagebox.showinfo("Информация", "Диалог редактирования недоступен")
            self.result = False
    
    class SQLQueryDialog:
        def __init__(self, *args, **kwargs):
            messagebox.showinfo("Информация", "Диалог SQL запросов недоступен")
    
    class SettingsDialog:
        def __init__(self, *args, **kwargs):
            messagebox.showinfo("Информация", "Диалог настроек недоступен")
    
    class CreateTableDialog:
        def __init__(self, *args, **kwargs):
            messagebox.showinfo("Информация", "Диалог создания таблицы недоступен")
            self.result = False
    
    class FieldDialog:
        def __init__(self, *args, **kwargs):
            messagebox.showinfo("Информация", "Диалог добавления поля недоступен")
            self.result = None

class DatabaseManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SQLite Database Manager - AstraLinux")
        self.root.geometry("1200x800")
        
        # Текущая БД
        self.current_db = None
        self.connection = None
        
        # Настройки автобэкапа
        self.auto_backup = True
        self.backup_dir = os.path.join(os.path.expanduser("~"), "db_backups")
        
        self.setup_ui()
        self.create_backup_dir()
        
    def create_backup_dir(self):
        """Создает директорию для бэкапов"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def setup_ui(self):
        """Создает интерфейс"""
        # Меню
        self.create_menu()
        
        # Главная панель
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Левая панель - структура БД
        left_frame = ttk.LabelFrame(main_frame, text="Структура базы данных")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))
        left_frame.config(width=300)
        
        # Дерево таблиц
        self.tree_tables = ttk.Treeview(left_frame, selectmode='browse')
        self.tree_tables.heading('#0', text='Таблицы')
        self.tree_tables.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tree_tables.bind('<<TreeviewSelect>>', self.on_table_select)
        
        # Кнопки управления таблицами
        table_buttons_frame = ttk.Frame(left_frame)
        table_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(table_buttons_frame, text="Создать таблицу", 
                  command=self.create_table_dialog).pack(fill=tk.X, pady=1)
        ttk.Button(table_buttons_frame, text="Удалить таблицу", 
                  command=self.delete_table).pack(fill=tk.X, pady=1)
        ttk.Button(table_buttons_frame, text="Структура таблицы", 
                  command=self.show_table_structure).pack(fill=tk.X, pady=1)
        
        # Правая панель - данные
        right_frame = ttk.LabelFrame(main_frame, text="Данные таблицы")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Панель инструментов для данных
        toolbar_frame = ttk.Frame(right_frame)
        toolbar_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar_frame, text="Добавить запись", 
                  command=self.add_record).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Изменить запись", 
                  command=self.edit_record).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Удалить запись", 
                  command=self.delete_record).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Обновить", 
                  command=self.refresh_data).pack(side=tk.LEFT, padx=2)
        
        # Поиск
        search_frame = ttk.Frame(toolbar_frame)
        search_frame.pack(side=tk.RIGHT, padx=5)
        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT, padx=2)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=2)
        self.search_entry.bind('<KeyRelease>', self.on_search)
        ttk.Button(search_frame, text="Очистить", 
                  command=self.clear_search).pack(side=tk.LEFT, padx=2)
        
        # Таблица данных
        data_frame = ttk.Frame(right_frame)
        data_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.data_tree = ttk.Treeview(data_frame)
        
        # Скроллбары для таблицы данных
        v_scrollbar = ttk.Scrollbar(data_frame, orient=tk.VERTICAL, command=self.data_tree.yview)
        h_scrollbar = ttk.Scrollbar(data_frame, orient=tk.HORIZONTAL, command=self.data_tree.xview)
        self.data_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Статусная строка
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_menu(self):
        """Создает меню приложения"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новая база данных", command=self.new_database)
        file_menu.add_command(label="Открыть базу данных", command=self.open_database)
        file_menu.add_separator()
        file_menu.add_command(label="Резервная копия", command=self.backup_database)
        file_menu.add_command(label="Восстановить из копии", command=self.restore_database)
        file_menu.add_separator()
        file_menu.add_command(label="Экспорт в SQL", command=self.export_sql)
        file_menu.add_command(label="Импорт из SQL", command=self.import_sql)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Инструменты
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Инструменты", menu=tools_menu)
        tools_menu.add_command(label="SQL запрос", command=self.sql_query_dialog)
        tools_menu.add_command(label="Вакуум БД", command=self.vacuum_database)
        tools_menu.add_separator()
        tools_menu.add_command(label="Настройки", command=self.settings_dialog)
        
        # Справка
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.about_dialog)
    
    def new_database(self):
        """Создает новую базу данных"""
        filename = filedialog.asksaveasfilename(
            title="Создать новую базу данных",
            defaultextension=".db",
            filetypes=[("SQLite files", "*.db"), ("All files", "*.*")]
        )
        if filename:
            try:
                # Создаем новую БД
                conn = sqlite3.connect(filename)
                conn.close()
                self.open_database_file(filename)
                self.status_var.set(f"Создана новая база данных: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать базу данных: {str(e)}")
    
    def open_database(self):
        """Открывает существующую базу данных"""
        filename = filedialog.askopenfilename(
            title="Открыть базу данных",
            filetypes=[("SQLite files", "*.db"), ("All files", "*.*")]
        )
        if filename:
            self.open_database_file(filename)
    
    def open_database_file(self, filename):
        """Открывает файл базы данных"""
        try:
            # Закрываем текущее соединение
            if self.connection:
                self.connection.close()
            
            self.connection = sqlite3.connect(filename)
            self.current_db = filename
            self.refresh_tables()
            self.root.title(f"SQLite Database Manager - {os.path.basename(filename)}")
            self.status_var.set(f"Открыта база данных: {os.path.basename(filename)}")
            
            # Автобэкап при открытии
            if self.auto_backup:
                self.auto_backup_database()
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть базу данных: {str(e)}")
    
    def refresh_tables(self):
        """Обновляет список таблиц"""
        logger.info("Начинаем обновление списка таблиц")
        
        if not self.connection:
            logger.warning("Нет подключения к БД при обновлении таблиц")
            return
            
        try:
            # Очищаем дерево
            logger.debug("Очищаем дерево таблиц")
            for item in self.tree_tables.get_children():
                self.tree_tables.delete(item)
            
            # Получаем список таблиц
            cursor = self.connection.cursor()
            logger.debug("Выполняем запрос для получения списка таблиц")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = cursor.fetchall()
            logger.info(f"Найдено таблиц: {len(tables)}")
            
            for table in tables:
                logger.debug(f"Добавляем таблицу в дерево: {table[0]}")
                self.tree_tables.insert('', 'end', text=table[0], values=[table[0]])
            
            logger.info("Обновление списка таблиц завершено успешно")
                
        except Exception as e:
            logger.error(f"Ошибка при обновлении списка таблиц: {str(e)}")
            logger.error(f"Тип ошибки: {type(e).__name__}")
            logger.error(f"Трассировка: {traceback.format_exc()}")
            messagebox.showerror("Ошибка", f"Не удалось получить список таблиц: {str(e)}")
    
    def on_table_select(self, event):
        """Обработка выбора таблицы"""
        selection = self.tree_tables.selection()
        if selection:
            table_name = self.tree_tables.item(selection[0])['text']
            self.load_table_data(table_name)
    
    def load_table_data(self, table_name):
        """Загружает данные таблицы"""
        logger.info(f"Начинаем загрузку данных таблицы: {table_name}")
        
        if not self.connection:
            logger.warning("Нет подключения к БД при загрузке данных таблицы")
            return
            
        try:
            # Очищаем текущие данные
            logger.debug("Очищаем текущие данные в дереве")
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)
            
            # Получаем структуру таблицы
            cursor = self.connection.cursor()
            logger.debug(f"Получаем структуру таблицы: {table_name}")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            logger.debug(f"Структура таблицы {table_name}: {columns}")
            
            # Настраиваем колонки
            column_names = [col[1] for col in columns]
            logger.debug(f"Имена колонок: {column_names}")
            self.data_tree['columns'] = column_names
            self.data_tree['show'] = 'headings'
            
            for col in column_names:
                logger.debug(f"Настраиваем колонку: {col}")
                self.data_tree.heading(col, text=col)
                self.data_tree.column(col, width=100)
            
            # Загружаем данные
            logger.debug(f"Выполняем запрос SELECT * FROM {table_name}")
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            logger.info(f"Получено {len(rows)} записей из таблицы {table_name}")
            
            for i, row in enumerate(rows):
                logger.debug(f"Добавляем строку {i+1}: {row}")
                self.data_tree.insert('', 'end', values=row)
                
            self.current_table = table_name
            status_msg = f"Загружена таблица '{table_name}': {len(rows)} записей"
            self.status_var.set(status_msg)
            logger.info(f"Загрузка данных завершена успешно. {status_msg}")
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке данных таблицы {table_name}: {str(e)}")
            logger.error(f"Тип ошибки: {type(e).__name__}")
            logger.error(f"Трассировка: {traceback.format_exc()}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные таблицы: {str(e)}")
    
    def create_table_dialog(self):
        """Диалог создания новой таблицы"""
        logger.info("Открываем диалог создания новой таблицы")
        
        if not self.connection:
            logger.warning("Нет подключения к БД при попытке создания таблицы")
            messagebox.showwarning("Предупреждение", "Сначала откройте или создайте базу данных")
            return
            
        try:
            logger.debug("Создаем экземпляр CreateTableDialog")
            dialog = CreateTableDialog(self.root, self.connection)
            logger.debug(f"Результат диалога: {dialog.result}")
            
            if dialog.result:
                logger.info("Пользователь подтвердил создание таблицы")
                logger.debug("Вызываем refresh_tables()")
                self.refresh_tables()
                
                if self.auto_backup:
                    logger.debug("Выполняем автоматическое резервное копирование")
                    self.auto_backup_database()
                logger.info("Создание таблицы завершено успешно")
            else:
                logger.info("Пользователь отменил создание таблицы")
                
        except Exception as e:
            logger.error(f"Ошибка при создании таблицы: {str(e)}")
            logger.error(f"Тип ошибки: {type(e).__name__}")
            logger.error(f"Трассировка: {traceback.format_exc()}")
            messagebox.showerror("Ошибка", f"Ошибка при создании таблицы: {str(e)}")
    
    def delete_table(self):
        """Удаляет выбранную таблицу"""
        if not self.connection:
            return
            
        selection = self.tree_tables.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите таблицу для удаления")
            return
            
        table_name = self.tree_tables.item(selection[0])['text']
        
        if messagebox.askyesno("Подтверждение", 
                              f"Вы действительно хотите удалить таблицу '{table_name}'?\n"
                              "Все данные будут потеряны!"):
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"DROP TABLE {table_name}")
                self.connection.commit()
                self.refresh_tables()
                
                # Очищаем область данных
                for item in self.data_tree.get_children():
                    self.data_tree.delete(item)
                    
                self.status_var.set(f"Таблица '{table_name}' удалена")
                
                if self.auto_backup:
                    self.auto_backup_database()
                    
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить таблицу: {str(e)}")
    
    def show_table_structure(self):
        """Показывает структуру выбранной таблицы"""
        selection = self.tree_tables.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите таблицу")
            return
            
        table_name = self.tree_tables.item(selection[0])['text']
        TableStructureDialog(self.root, self.connection, table_name)
    
    def add_record(self):
        """Добавляет новую запись"""
        if not hasattr(self, 'current_table'):
            messagebox.showwarning("Предупреждение", "Выберите таблицу")
            return
            
        dialog = EditRecordDialog(self.root, self.connection, self.current_table)
        if dialog.result:
            self.load_table_data(self.current_table)
            if self.auto_backup:
                self.auto_backup_database()
    
    def edit_record(self):
        """Редактирует выбранную запись"""
        selection = self.data_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите запись для редактирования")
            return
            
        values = self.data_tree.item(selection[0])['values']
        dialog = EditRecordDialog(self.root, self.connection, self.current_table, values)
        if dialog.result:
            self.load_table_data(self.current_table)
            if self.auto_backup:
                self.auto_backup_database()
    
    def delete_record(self):
        """Удаляет выбранную запись"""
        selection = self.data_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return
            
        if messagebox.askyesno("Подтверждение", "Удалить выбранную запись?"):
            try:
                values = self.data_tree.item(selection[0])['values']
                
                # Получаем структуру таблицы для формирования WHERE
                cursor = self.connection.cursor()
                cursor.execute(f"PRAGMA table_info({self.current_table})")
                columns = cursor.fetchall()
                
                # Формируем WHERE условие
                where_parts = []
                for i, col in enumerate(columns):
                    if i < len(values):
                        if values[i] is None:
                            where_parts.append(f"{col[1]} IS NULL")
                        else:
                            where_parts.append(f"{col[1]} = ?")
                
                where_clause = " AND ".join(where_parts)
                values_for_where = [v for v in values if v is not None]
                
                cursor.execute(f"DELETE FROM {self.current_table} WHERE {where_clause}", 
                             values_for_where)
                self.connection.commit()
                
                self.load_table_data(self.current_table)
                self.status_var.set("Запись удалена")
                
                if self.auto_backup:
                    self.auto_backup_database()
                    
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить запись: {str(e)}")
    
    def refresh_data(self):
        """Обновляет данные текущей таблицы"""
        if hasattr(self, 'current_table'):
            self.load_table_data(self.current_table)
    
    def on_search(self, event):
        """Поиск в данных таблицы"""
        search_text = self.search_var.get().strip().lower()
        if not search_text:
            self.refresh_data()
            return
            
        # Фильтруем отображаемые строки
        all_items = self.data_tree.get_children()
        for item in all_items:
            values = self.data_tree.item(item)['values']
            found = False
            for value in values:
                if str(value).lower().find(search_text) != -1:
                    found = True
                    break
            
            if not found:
                self.data_tree.delete(item)
    
    def clear_search(self):
        """Очищает поиск"""
        self.search_var.set("")
        self.refresh_data()
    
    def backup_database(self):
        """Создает резервную копию БД"""
        if not self.current_db:
            messagebox.showwarning("Предупреждение", "Сначала откройте базу данных")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Сохранить резервную копию",
            defaultextension=".db",
            initialname=f"{os.path.splitext(os.path.basename(self.current_db))[0]}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
            filetypes=[("SQLite files", "*.db"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                shutil.copy2(self.current_db, filename)
                messagebox.showinfo("Успех", f"Резервная копия создана: {filename}")
                self.status_var.set("Резервная копия создана")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать резервную копию: {str(e)}")
    
    def auto_backup_database(self):
        """Автоматическое создание резервной копии"""
        if not self.current_db or not self.auto_backup:
            return
            
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            basename = os.path.splitext(os.path.basename(self.current_db))[0]
            backup_filename = f"{basename}_auto_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            shutil.copy2(self.current_db, backup_path)
            
            # Удаляем старые автобэкапы (оставляем последние 10)
            self.cleanup_old_backups(basename)
            
        except Exception:
            pass  # Игнорируем ошибки автобэкапа
    
    def cleanup_old_backups(self, basename):
        """Удаляет старые автобэкапы"""
        try:
            backups = []
            for filename in os.listdir(self.backup_dir):
                if filename.startswith(f"{basename}_auto_") and filename.endswith('.db'):
                    filepath = os.path.join(self.backup_dir, filename)
                    backups.append((filepath, os.path.getmtime(filepath)))
            
            # Сортируем по времени изменения
            backups.sort(key=lambda x: x[1], reverse=True)
            
            # Удаляем старые (оставляем 10 последних)
            for filepath, _ in backups[10:]:
                os.remove(filepath)
                
        except Exception:
            pass
    
    def restore_database(self):
        """Восстанавливает БД из резервной копии"""
        filename = filedialog.askopenfilename(
            title="Выберите резервную копию для восстановления",
            filetypes=[("SQLite files", "*.db"), ("All files", "*.*")]
        )
        
        if filename:
            if messagebox.askyesno("Подтверждение", 
                                 "Текущая база данных будет заменена резервной копией.\n"
                                 "Продолжить?"):
                try:
                    if self.connection:
                        self.connection.close()
                        
                    if self.current_db:
                        shutil.copy2(filename, self.current_db)
                        self.open_database_file(self.current_db)
                    else:
                        self.open_database_file(filename)
                        
                    messagebox.showinfo("Успех", "База данных восстановлена из резервной копии")
                    
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось восстановить базу данных: {str(e)}")
    
    def export_sql(self):
        """Экспортирует БД в SQL файл"""
        if not self.connection:
            messagebox.showwarning("Предупреждение", "Сначала откройте базу данных")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Экспорт в SQL",
            defaultextension=".sql",
            filetypes=[("SQL files", "*.sql"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    for line in self.connection.iterdump():
                        f.write(f"{line}\n")
                        
                messagebox.showinfo("Успех", f"База данных экспортирована в: {filename}")
                self.status_var.set("Экспорт завершен")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось экспортировать базу данных: {str(e)}")
    
    def import_sql(self):
        """Импортирует SQL файл"""
        if not self.connection:
            messagebox.showwarning("Предупреждение", "Сначала откройте базу данных")
            return
            
        filename = filedialog.askopenfilename(
            title="Импорт SQL",
            filetypes=[("SQL files", "*.sql"), ("All files", "*.*")]
        )
        
        if filename:
            if messagebox.askyesno("Подтверждение", 
                                 "Импорт может изменить структуру и данные базы.\n"
                                 "Продолжить?"):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        sql_script = f.read()
                        
                    cursor = self.connection.cursor()
                    cursor.executescript(sql_script)
                    self.connection.commit()
                    
                    self.refresh_tables()
                    messagebox.showinfo("Успех", "SQL файл успешно импортирован")
                    self.status_var.set("Импорт завершен")
                    
                    if self.auto_backup:
                        self.auto_backup_database()
                        
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось импортировать SQL файл: {str(e)}")
    
    def sql_query_dialog(self):
        """Диалог выполнения SQL запросов"""
        if not self.connection:
            messagebox.showwarning("Предупреждение", "Сначала откройте базу данных")
            return
            
        SQLQueryDialog(self.root, self.connection)
    
    def vacuum_database(self):
        """Выполняет вакуум БД"""
        if not self.connection:
            messagebox.showwarning("Предупреждение", "Сначала откройте базу данных")
            return
            
        if messagebox.askyesno("Подтверждение", 
                              "Выполнить вакуум базы данных?\n"
                              "Это может занять некоторое время."):
            try:
                cursor = self.connection.cursor()
                cursor.execute("VACUUM")
                self.connection.commit()
                messagebox.showinfo("Успех", "Вакуум базы данных выполнен")
                self.status_var.set("Вакуум завершен")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось выполнить вакуум: {str(e)}")
    
    def settings_dialog(self):
        """Диалог настроек"""
        SettingsDialog(self.root, self)
    
    def about_dialog(self):
        """О программе"""
        messagebox.showinfo("О программе", 
                           "SQLite Database Manager для AstraLinux\n"
                           "Версия 1.0\n\n"
                           "Менеджер баз данных SQLite с графическим интерфейсом\n"
                           "Совместимость: Python 3.5+\n"
                           "Зависимости: только стандартная библиотека Python\n\n"
                           "Возможности:\n"
                           "• Создание и редактирование БД\n"
                           "• Управление таблицами и данными\n"
                           "• Автоматическое резервное копирование\n"
                           "• Экспорт/импорт SQL\n"
                           "• Выполнение произвольных SQL запросов\n"
                           "• Поиск и фильтрация данных")
    
    def run(self):
        """Запускает приложение"""
        self.root.mainloop()
        if self.connection:
            self.connection.close()


if __name__ == "__main__":
    app = DatabaseManager()
    app.run()