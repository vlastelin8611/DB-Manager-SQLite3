#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Дополнительные диалоги для SQLite Database Manager
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
import logging
import traceback

# Получаем логгер
logger = logging.getLogger('db_manager.dialogs')


class TableStructureDialog:
    def __init__(self, parent, connection, table_name):
        self.connection = connection
        self.table_name = table_name
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Структура таблицы: {table_name}")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.load_structure()
        
    def setup_ui(self):
        # Информация о таблице
        info_frame = ttk.LabelFrame(self.dialog, text="Информация о таблице")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.info_text = tk.Text(info_frame, height=3, wrap=tk.WORD)
        self.info_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Структура полей
        fields_frame = ttk.LabelFrame(self.dialog, text="Поля таблицы")
        fields_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.fields_tree = ttk.Treeview(fields_frame, 
                                      columns=('type', 'null', 'default', 'pk'))
        self.fields_tree.heading('#0', text='Поле')
        self.fields_tree.heading('type', text='Тип')
        self.fields_tree.heading('null', text='NULL')
        self.fields_tree.heading('default', text='По умолчанию')
        self.fields_tree.heading('pk', text='PK')
        
        self.fields_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Индексы
        indexes_frame = ttk.LabelFrame(self.dialog, text="Индексы")
        indexes_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.indexes_text = tk.Text(indexes_frame, height=4)
        self.indexes_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Кнопка закрытия
        ttk.Button(self.dialog, text="Закрыть", 
                  command=self.dialog.destroy).pack(pady=10)
    
    def load_structure(self):
        try:
            cursor = self.connection.cursor()
            
            # Информация о таблице
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{self.table_name}'")
            sql = cursor.fetchone()
            if sql:
                self.info_text.insert(tk.END, f"CREATE TABLE:\n{sql[0]}")
            
            # Поля таблицы
            cursor.execute(f"PRAGMA table_info({self.table_name})")
            columns = cursor.fetchall()
            
            for col in columns:
                cid, name, col_type, notnull, default, pk = col
                null_text = "NO" if notnull else "YES"
                pk_text = "YES" if pk else "NO"
                default_text = str(default) if default is not None else ""
                
                self.fields_tree.insert('', 'end', text=name,
                                      values=(col_type, null_text, default_text, pk_text))
            
            # Индексы
            cursor.execute(f"PRAGMA index_list({self.table_name})")
            indexes = cursor.fetchall()
            
            if indexes:
                for index in indexes:
                    cursor.execute(f"PRAGMA index_info({index[1]})")
                    index_info = cursor.fetchall()
                    columns_list = [info[2] for info in index_info]
                    self.indexes_text.insert(tk.END, 
                                           f"{index[1]}: {', '.join(columns_list)}\n")
            else:
                self.indexes_text.insert(tk.END, "Индексы не найдены")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить структуру: {str(e)}")


class EditRecordDialog:
    def __init__(self, parent, connection, table_name, values=None):
        self.connection = connection
        self.table_name = table_name
        self.original_values = values
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"{'Редактировать' if values else 'Добавить'} запись - {table_name}")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.load_fields()
        
    def setup_ui(self):
        # Фрейм для полей
        self.fields_frame = ttk.Frame(self.dialog)
        self.fields_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Скроллбар
        canvas = tk.Canvas(self.fields_frame)
        scrollbar = ttk.Scrollbar(self.fields_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.scrollable_frame = scrollable_frame
        self.field_vars = {}
        
        # Кнопки
        buttons_frame = ttk.Frame(self.dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(buttons_frame, text="Сохранить", command=self.save_record).pack(side=tk.RIGHT, padx=2)
        ttk.Button(buttons_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=2)
    
    def load_fields(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"PRAGMA table_info({self.table_name})")
            columns = cursor.fetchall()
            
            for i, col in enumerate(columns):
                cid, name, col_type, notnull, default, pk = col
                
                row_frame = ttk.Frame(self.scrollable_frame)
                row_frame.pack(fill=tk.X, padx=5, pady=2)
                
                # Метка поля
                label_text = name
                if notnull:
                    label_text += " *"
                if pk:
                    label_text += " (PK)"
                    
                ttk.Label(row_frame, text=label_text, width=20).pack(side=tk.LEFT, padx=5)
                
                # Поле ввода
                var = tk.StringVar()
                
                # Заполняем существующими значениями
                if self.original_values and i < len(self.original_values):
                    value = self.original_values[i]
                    if value is not None:
                        var.set(str(value))
                
                if col_type.upper() in ['TEXT', 'BLOB']:
                    entry = tk.Text(row_frame, height=3, width=30)
                    entry.insert('1.0', var.get())
                    entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                    self.field_vars[name] = ('text', entry)
                else:
                    entry = ttk.Entry(row_frame, textvariable=var, width=30)
                    entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                    self.field_vars[name] = ('entry', var)
                
                # Информация о типе
                ttk.Label(row_frame, text=col_type, 
                         foreground='gray').pack(side=tk.RIGHT, padx=5)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить поля: {str(e)}")
    
    def save_record(self):
        try:
            # Получаем значения полей
            values = []
            field_names = []
            
            cursor = self.connection.cursor()
            cursor.execute(f"PRAGMA table_info({self.table_name})")
            columns = cursor.fetchall()
            
            for col in columns:
                name = col[1]
                field_names.append(name)
                
                if name in self.field_vars:
                    field_type, widget = self.field_vars[name]
                    if field_type == 'text':
                        value = widget.get('1.0', tk.END).strip()
                    else:
                        value = widget.get().strip()
                    
                    # Обработка пустых значений
                    if not value:
                        values.append(None)
                    else:
                        values.append(value)
                else:
                    values.append(None)
            
            # Выполняем INSERT или UPDATE
            if self.original_values:  # Редактирование
                # Формируем UPDATE запрос
                set_parts = []
                for i, name in enumerate(field_names):
                    set_parts.append(f"{name} = ?")
                
                # WHERE условие по всем полям оригинальной записи
                where_parts = []
                where_values = []
                for i, (name, orig_val) in enumerate(zip(field_names, self.original_values)):
                    if orig_val is None:
                        where_parts.append(f"{name} IS NULL")
                    else:
                        where_parts.append(f"{name} = ?")
                        where_values.append(orig_val)
                
                sql = f"UPDATE {self.table_name} SET {', '.join(set_parts)} WHERE {' AND '.join(where_parts)}"
                cursor.execute(sql, values + where_values)
                
            else:  # Добавление
                placeholders = ', '.join(['?' for _ in values])
                sql = f"INSERT INTO {self.table_name} ({', '.join(field_names)}) VALUES ({placeholders})"
                cursor.execute(sql, values)
            
            self.connection.commit()
            self.result = True
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить запись: {str(e)}")


class SQLQueryDialog:
    def __init__(self, parent, connection):
        self.connection = connection
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("SQL запрос")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Панель инструментов
        toolbar = ttk.Frame(self.dialog)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Выполнить", command=self.execute_query).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Очистить", command=self.clear_query).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Сохранить результат", command=self.save_result).pack(side=tk.LEFT, padx=2)
        
        # Поле для SQL запроса
        query_frame = ttk.LabelFrame(self.dialog, text="SQL запрос")
        query_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.query_text = scrolledtext.ScrolledText(query_frame, height=8, wrap=tk.WORD)
        self.query_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Результат
        result_frame = ttk.LabelFrame(self.dialog, text="Результат")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Таблица результата
        self.result_tree = ttk.Treeview(result_frame)
        
        # Скроллбары
        v_scroll = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        h_scroll = ttk.Scrollbar(result_frame, orient=tk.HORIZONTAL, command=self.result_tree.xview)
        self.result_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Статус
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к выполнению запроса")
        status_label = ttk.Label(self.dialog, textvariable=self.status_var)
        status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
        
        # Примеры запросов
        examples_frame = ttk.LabelFrame(self.dialog, text="Примеры запросов")
        examples_frame.pack(fill=tk.X, padx=5, pady=2)
        
        examples_text = "SELECT * FROM table_name; | INSERT INTO table_name VALUES (...); | UPDATE table_name SET ...; | DELETE FROM table_name WHERE ..."
        ttk.Label(examples_frame, text=examples_text, foreground='gray').pack(padx=5, pady=2)
    
    def execute_query(self):
        query = self.query_text.get('1.0', tk.END).strip()
        if not query:
            messagebox.showwarning("Предупреждение", "Введите SQL запрос")
            return
        
        try:
            cursor = self.connection.cursor()
            
            # Очищаем предыдущий результат
            for item in self.result_tree.get_children():
                self.result_tree.delete(item)
            
            # Выполняем запрос
            cursor.execute(query)
            
            # Если это SELECT запрос
            if query.upper().strip().startswith('SELECT'):
                # Получаем описание колонок
                columns = [description[0] for description in cursor.description] if cursor.description else []
                
                if columns:
                    # Настраиваем колонки
                    self.result_tree['columns'] = columns
                    self.result_tree['show'] = 'headings'
                    
                    for col in columns:
                        self.result_tree.heading(col, text=col)
                        self.result_tree.column(col, width=100)
                    
                    # Загружаем данные
                    rows = cursor.fetchall()
                    for row in rows:
                        self.result_tree.insert('', 'end', values=row)
                    
                    self.status_var.set(f"Найдено записей: {len(rows)}")
                else:
                    self.status_var.set("Запрос выполнен, данных нет")
            else:
                # Для других запросов (INSERT, UPDATE, DELETE)
                self.connection.commit()
                affected_rows = cursor.rowcount
                self.status_var.set(f"Запрос выполнен. Затронуто строк: {affected_rows}")
                
                # Очищаем отображение колонок
                self.result_tree['columns'] = ()
                self.result_tree['show'] = 'tree'
                
        except Exception as e:
            messagebox.showerror("Ошибка SQL", f"Ошибка выполнения запроса:\n{str(e)}")
            self.status_var.set(f"Ошибка: {str(e)}")
    
    def clear_query(self):
        self.query_text.delete('1.0', tk.END)
        
        # Очищаем результат
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        self.result_tree['columns'] = ()
        self.result_tree['show'] = 'tree'
        self.status_var.set("Готов к выполнению запроса")
    
    def save_result(self):
        # Простое сохранение результата в текстовый файл
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                title="Сохранить результат",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    # Заголовки
                    if self.result_tree['columns']:
                        f.write('\t'.join(self.result_tree['columns']) + '\n')
                        
                        # Данные
                        for item in self.result_tree.get_children():
                            values = self.result_tree.item(item)['values']
                            f.write('\t'.join(str(v) for v in values) + '\n')
                    else:
                        f.write("Нет данных для сохранения\n")
                
                messagebox.showinfo("Успех", f"Результат сохранен в: {filename}")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить результат: {str(e)}")


class SettingsDialog:
    def __init__(self, parent, main_app):
        self.main_app = main_app
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Настройки")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Вкладка "Общие"
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="Общие")
        
        # Автобэкап
        backup_frame = ttk.LabelFrame(general_frame, text="Резервное копирование")
        backup_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.auto_backup_var = tk.BooleanVar(value=self.main_app.auto_backup)
        ttk.Checkbutton(backup_frame, text="Автоматическое резервное копирование",
                       variable=self.auto_backup_var).pack(anchor=tk.W, padx=5, pady=5)
        
        # Путь к бэкапам
        path_frame = ttk.Frame(backup_frame)
        path_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(path_frame, text="Папка для бэкапов:").pack(anchor=tk.W)
        
        path_entry_frame = ttk.Frame(path_frame)
        path_entry_frame.pack(fill=tk.X, pady=2)
        
        self.backup_path_var = tk.StringVar(value=self.main_app.backup_dir)
        ttk.Entry(path_entry_frame, textvariable=self.backup_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(path_entry_frame, text="Обзор", command=self.browse_backup_dir).pack(side=tk.RIGHT, padx=2)
        
        # Кнопки
        buttons_frame = ttk.Frame(self.dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(buttons_frame, text="OK", command=self.save_settings).pack(side=tk.RIGHT, padx=2)
        ttk.Button(buttons_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=2)
    
    def browse_backup_dir(self):
        from tkinter import filedialog
        directory = filedialog.askdirectory(title="Выберите папку для бэкапов")
        if directory:
            self.backup_path_var.set(directory)
    
    def save_settings(self):
        self.main_app.auto_backup = self.auto_backup_var.get()
        self.main_app.backup_dir = self.backup_path_var.get()
        
        # Создаем папку если не существует
        import os
        if not os.path.exists(self.main_app.backup_dir):
            os.makedirs(self.main_app.backup_dir)
        
        messagebox.showinfo("Успех", "Настройки сохранены")
        self.dialog.destroy()


class CreateTableDialog:
    def __init__(self, parent, connection):
        logger.info("Инициализируем CreateTableDialog")
        self.connection = connection
        self.result = False
        
        try:
            self.dialog = tk.Toplevel(parent)
            self.dialog.title("Создать таблицу")
            self.dialog.geometry("600x500")
            self.dialog.transient(parent)
            self.dialog.grab_set()
            
            logger.debug("Диалог создан, вызываем setup_ui()")
            self.setup_ui()
            logger.info("CreateTableDialog успешно инициализирован")
            
            # Ждем закрытия диалога
            logger.debug("Ждем закрытия CreateTableDialog")
            parent.wait_window(self.dialog)
            logger.debug(f"CreateTableDialog закрыт, результат: {self.result}")
            
        except Exception as e:
            logger.error(f"Ошибка при инициализации CreateTableDialog: {str(e)}")
            logger.error(f"Трассировка: {traceback.format_exc()}")
            raise
        
    def setup_ui(self):
        # Имя таблицы
        name_frame = ttk.Frame(self.dialog)
        name_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(name_frame, text="Имя таблицы:").pack(side=tk.LEFT)
        self.table_name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.table_name_var, width=30).pack(side=tk.LEFT, padx=5)
        
        # Поля таблицы
        fields_frame = ttk.LabelFrame(self.dialog, text="Поля таблицы")
        fields_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Список полей
        self.fields_tree = ttk.Treeview(fields_frame, columns=('type', 'null', 'default', 'pk'), height=10)
        self.fields_tree.heading('#0', text='Имя поля')
        self.fields_tree.heading('type', text='Тип')
        self.fields_tree.heading('null', text='NULL')
        self.fields_tree.heading('default', text='По умолчанию')
        self.fields_tree.heading('pk', text='PK')
        
        self.fields_tree.column('#0', width=150)
        self.fields_tree.column('type', width=100)
        self.fields_tree.column('null', width=60)
        self.fields_tree.column('default', width=100)
        self.fields_tree.column('pk', width=40)
        
        self.fields_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Кнопки управления полями
        fields_buttons = ttk.Frame(fields_frame)
        fields_buttons.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(fields_buttons, text="Добавить поле", command=self.add_field).pack(side=tk.LEFT, padx=2)
        ttk.Button(fields_buttons, text="Удалить поле", command=self.remove_field).pack(side=tk.LEFT, padx=2)
        
        # Кнопки диалога
        buttons_frame = ttk.Frame(self.dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(buttons_frame, text="Создать", command=self.create_table).pack(side=tk.RIGHT, padx=2)
        ttk.Button(buttons_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=2)
        
        # Добавляем поле ID по умолчанию
        self.fields_tree.insert('', 'end', text='id', values=('INTEGER', 'NO', '', 'YES'))
    
    def add_field(self):
        logger.info("Пользователь нажал 'Добавить поле'")
        
        try:
            logger.debug("Создаем FieldDialog")
            field_dialog = FieldDialog(self.dialog)
            logger.debug(f"FieldDialog завершен, результат: {field_dialog.result}")
            
            if field_dialog.result:
                name, field_type, allow_null, default, is_pk = field_dialog.result
                logger.info(f"Добавляем поле: name='{name}', type='{field_type}', null={allow_null}, default='{default}', pk={is_pk}")
                
                null_text = 'YES' if allow_null else 'NO'
                pk_text = 'YES' if is_pk else 'NO'
                
                logger.debug(f"Преобразованные значения: null_text='{null_text}', pk_text='{pk_text}'")
                
                tree_values = (field_type, null_text, default, pk_text)
                logger.debug(f"Значения для вставки в дерево: {tree_values}")
                
                self.fields_tree.insert('', 'end', text=name, values=tree_values)
                logger.info(f"Поле '{name}' успешно добавлено в дерево")
                
                # Проверим, что поле действительно добавилось
                children = self.fields_tree.get_children()
                logger.debug(f"Количество полей в дереве после добавления: {len(children)}")
                
                for child in children:
                    item_data = self.fields_tree.item(child)
                    logger.debug(f"Поле в дереве: text='{item_data['text']}', values={item_data['values']}")
                    
            else:
                logger.info("Пользователь отменил добавление поля")
                
        except Exception as e:
            logger.error(f"Ошибка при добавлении поля: {str(e)}")
            logger.error(f"Тип ошибки: {type(e).__name__}")
            logger.error(f"Трассировка: {traceback.format_exc()}")
            messagebox.showerror("Ошибка", f"Не удалось добавить поле: {str(e)}")
    
    def remove_field(self):
        selection = self.fields_tree.selection()
        if selection:
            self.fields_tree.delete(selection[0])
    
    def create_table(self):
        logger.info("Пользователь нажал 'Создать таблицу'")
        
        table_name = self.table_name_var.get().strip()
        logger.debug(f"Имя таблицы: '{table_name}'")
        
        if not table_name:
            logger.warning("Пустое имя таблицы")
            messagebox.showwarning("Предупреждение", "Введите имя таблицы")
            return
            
        # Проверяем корректность имени таблицы
        if not table_name.replace('_', '').replace('-', '').isalnum():
            logger.warning(f"Некорректное имя таблицы: '{table_name}'")
            messagebox.showwarning("Предупреждение", 
                                 "Имя таблицы должно содержать только буквы, цифры, _ и -")
            return
            
        try:
            fields = []
            primary_keys = []
            
            children = self.fields_tree.get_children()
            logger.info(f"Обрабатываем {len(children)} полей")
            
            for i, item in enumerate(children):
                field_name = self.fields_tree.item(item)['text']
                values = self.fields_tree.item(item)['values']
                
                logger.debug(f"Поле {i+1}: name='{field_name}', values={values}")
                
                if len(values) < 4:
                    logger.error(f"Некорректные данные для поля {field_name}: недостаточно значений ({len(values)})")
                    messagebox.showerror("Ошибка", f"Некорректные данные для поля {field_name}")
                    return
                    
                field_type, allow_null, default, is_pk = values
                logger.debug(f"Распаковка значений: type='{field_type}', null='{allow_null}', default='{default}', pk='{is_pk}'")
                
                # Проверяем корректность имени поля
                if not field_name or not field_name.replace('_', '').replace('-', '').isalnum():
                    logger.warning(f"Некорректное имя поля: '{field_name}'")
                    messagebox.showwarning("Предупреждение", 
                                         f"Некорректное имя поля: {field_name}")
                    return
                
                field_def = f'"{field_name}" {field_type.upper()}'
                logger.debug(f"Базовое определение поля: {field_def}")
                
                if is_pk == 'YES':
                    primary_keys.append(field_name)
                    logger.debug(f"Поле '{field_name}' является первичным ключом")
                    
                    if field_type.upper() == 'INTEGER' and len([pk for pk in self.fields_tree.get_children() 
                                                               if self.fields_tree.item(pk)['values'][3] == 'YES']) == 1:
                        field_def += " PRIMARY KEY AUTOINCREMENT"
                        logger.debug("Добавлен AUTOINCREMENT для единственного INTEGER PK")
                    else:
                        field_def += " PRIMARY KEY"
                        logger.debug("Добавлен PRIMARY KEY")
                
                if allow_null == 'NO' and is_pk != 'YES':
                    field_def += " NOT NULL"
                    logger.debug("Добавлено NOT NULL")
                    
                if default and default.strip() and default.strip().upper() != 'NULL':
                    # Экранируем строковые значения
                    if field_type.upper() in ['TEXT', 'BLOB']:
                        field_def += f" DEFAULT '{default.strip()}'"
                        logger.debug(f"Добавлено DEFAULT '{default.strip()}' для {field_type}")
                    else:
                        field_def += f" DEFAULT {default.strip()}"
                        logger.debug(f"Добавлено DEFAULT {default.strip()} для {field_type}")
                    
                fields.append(field_def)
                logger.info(f"Финальное определение поля: {field_def}")
            
            logger.info(f"Всего полей обработано: {len(fields)}")
            
            if not fields:
                logger.warning("Нет полей для создания таблицы")
                messagebox.showwarning("Предупреждение", "Добавьте хотя бы одно поле")
                return
                
            # Если есть составной первичный ключ
            if len(primary_keys) > 1:
                pk_fields = [f'"{pk}"' for pk in primary_keys]
                pk_constraint = f'PRIMARY KEY ({", ".join(pk_fields)})'
                fields.append(pk_constraint)
                logger.info(f"Добавлен составной первичный ключ: {pk_constraint}")
                
            sql = f'CREATE TABLE "{table_name}" ({", ".join(fields)})'
            logger.info(f"Сгенерированный SQL: {sql}")
            
            # Показываем SQL для проверки
            if messagebox.askyesno("Подтверждение", 
                                 f"Создать таблицу со следующим SQL:\n\n{sql}\n\nПродолжить?"):
                logger.info("Пользователь подтвердил создание таблицы")
                
                try:
                    cursor = self.connection.cursor()
                    cursor.execute(sql)
                    self.connection.commit()
                    
                    self.result = True
                    logger.info(f"Таблица '{table_name}' успешно создана")
                    messagebox.showinfo("Успех", f"Таблица '{table_name}' создана успешно")
                    self.dialog.destroy()
                    
                except sqlite3.Error as e:
                    logger.error(f"Ошибка SQLite при создании таблицы: {str(e)}")
                    logger.error(f"SQL: {sql}")
                    messagebox.showerror("Ошибка", f"Не удалось создать таблицу:\n{str(e)}\n\nSQL:\n{sql}")
                    
            else:
                logger.info("Пользователь отменил создание таблицы")
                
        except Exception as e:
            logger.error(f"Общая ошибка при создании таблицы: {str(e)}")
            logger.error(f"Тип ошибки: {type(e).__name__}")
            logger.error(f"Трассировка: {traceback.format_exc()}")
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")


class FieldDialog:
    def __init__(self, parent):
        logger.info("Инициализируем FieldDialog")
        self.result = None
        
        try:
            self.dialog = tk.Toplevel(parent)
            self.dialog.title("Добавить поле")
            self.dialog.geometry("500x450")  # Увеличиваем размер окна
            self.dialog.transient(parent)
            self.dialog.grab_set()
            logger.debug("FieldDialog окно создано успешно")
            
        except Exception as e:
            logger.error(f"Ошибка при создании FieldDialog: {str(e)}")
            logger.error(f"Трассировка: {traceback.format_exc()}")
            raise
        
        self.setup_ui()
        
        # Ждем закрытия диалога
        logger.debug("Ждем закрытия FieldDialog")
        parent.wait_window(self.dialog)
        logger.debug(f"FieldDialog закрыт, финальный результат: {self.result}")
        
    def setup_ui(self):
        # Имя поля
        name_frame = ttk.Frame(self.dialog)
        name_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(name_frame, text="Имя поля:").pack(side=tk.LEFT)
        self.name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.name_var, width=30).pack(side=tk.LEFT, padx=5)
        
        # Тип поля
        type_frame = ttk.Frame(self.dialog)
        type_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(type_frame, text="Тип:").pack(side=tk.LEFT)
        self.type_var = tk.StringVar(value="TEXT")
        type_combo = ttk.Combobox(type_frame, textvariable=self.type_var, 
                                values=["TEXT", "INTEGER", "REAL", "BLOB", "NUMERIC"],
                                state="readonly", width=15)
        type_combo.pack(side=tk.LEFT, padx=5)
        
        # Информация о типах
        info_frame = ttk.LabelFrame(self.dialog, text="Информация о типах данных")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        info_text = """TEXT - текстовые строки любой длины
INTEGER - целые числа (поддерживает автоинкремент)
REAL - числа с плавающей точкой
BLOB - бинарные данные
NUMERIC - числовые значения (автопреобразование)"""
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT, 
                              font=('Arial', 8), foreground='gray')
        info_label.pack(padx=5, pady=5, anchor=tk.W)
        
        # Параметры
        options_frame = ttk.LabelFrame(self.dialog, text="Параметры")
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.allow_null_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Разрешить NULL", 
                       variable=self.allow_null_var).pack(anchor=tk.W, padx=5, pady=2)
        
        self.is_pk_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Первичный ключ", 
                       variable=self.is_pk_var).pack(anchor=tk.W, padx=5, pady=2)
        
        # Значение по умолчанию
        default_frame = ttk.Frame(options_frame)
        default_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(default_frame, text="По умолчанию:").pack(side=tk.LEFT)
        self.default_var = tk.StringVar()
        ttk.Entry(default_frame, textvariable=self.default_var, width=20).pack(side=tk.LEFT, padx=5)
        
        # Кнопки
        buttons_frame = ttk.Frame(self.dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(buttons_frame, text="OK", command=self.ok_clicked).pack(side=tk.RIGHT, padx=2)
        ttk.Button(buttons_frame, text="Отмена", command=self.cancel_clicked).pack(side=tk.RIGHT, padx=2)
    
    def cancel_clicked(self):
        """Обработка нажатия кнопки Отмена"""
        logger.info("Пользователь нажал Отмена в FieldDialog")
        self.result = None
        self.dialog.destroy()
    
    def ok_clicked(self):
        logger.info("Пользователь нажал OK в FieldDialog")
        
        try:
            name = self.name_var.get().strip()
            logger.debug(f"Имя поля: '{name}'")
            
            if not name:
                logger.warning("Пустое имя поля")
                messagebox.showwarning("Предупреждение", "Введите имя поля")
                return
                
            # Проверяем корректность имени поля
            if not name.replace('_', '').replace('-', '').isalnum():
                logger.warning(f"Некорректное имя поля: '{name}'")
                messagebox.showwarning("Предупреждение", 
                                     "Имя поля должно содержать только буквы, цифры, _ и -")
                return
                
            # Проверяем зарезервированные слова SQLite
            reserved_words = {'TABLE', 'CREATE', 'INSERT', 'SELECT', 'UPDATE', 'DELETE', 
                             'DROP', 'ALTER', 'INDEX', 'WHERE', 'ORDER', 'GROUP', 'HAVING',
                             'UNION', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'OUTER', 'ON'}
            
            if name.upper() in reserved_words:
                logger.warning(f"Использование зарезервированного слова: '{name}'")
                messagebox.showwarning("Предупреждение", 
                                     f"'{name}' является зарезервированным словом SQLite.\n"
                                     "Используйте другое имя поля.")
                return
                
            # Проверяем значение по умолчанию для числовых типов
            default_value = self.default_var.get().strip()
            field_type = self.type_var.get()
            
            logger.debug(f"Значения поля: type='{field_type}', default='{default_value}'")
        
            if default_value and field_type in ['INTEGER', 'REAL', 'NUMERIC']:
                logger.debug(f"Проверяем значение по умолчанию '{default_value}' для типа {field_type}")
                try:
                    if field_type == 'INTEGER':
                        int(default_value)
                        logger.debug("Значение по умолчанию для INTEGER валидно")
                    elif field_type in ['REAL', 'NUMERIC']:
                        float(default_value)
                        logger.debug("Значение по умолчанию для REAL/NUMERIC валидно")
                except ValueError:
                    logger.warning(f"Некорректное значение по умолчанию '{default_value}' для типа {field_type}")
                    messagebox.showwarning("Предупреждение", 
                                         f"Значение по умолчанию '{default_value}' "
                                         f"не совместимо с типом {field_type}")
                    return
        
            # Проверяем логику первичного ключа
            if self.is_pk_var.get() and self.allow_null_var.get():
                if not messagebox.askyesno("Подтверждение", 
                                         "Первичный ключ не может быть NULL.\n"
                                         "Автоматически установить NOT NULL?"):
                    return
                else:
                    self.allow_null_var.set(False)
                
            # Получаем выбранный тип
            selected_type = self.type_var.get()
            logger.debug(f"Выбранный тип: '{selected_type}'")
            
            allow_null = self.allow_null_var.get()
            is_pk = self.is_pk_var.get()
            
            logger.info(f"Создаем результат поля: name='{name}', type='{selected_type}', null={allow_null}, default='{default_value}', pk={is_pk}")
            
            self.result = (
                name,
                selected_type,
                allow_null,
                default_value,
                is_pk
            )
            
            logger.info(f"FieldDialog завершен успешно с результатом: {self.result}")
            self.dialog.destroy()
            
        except Exception as e:
            logger.error(f"Ошибка в ok_clicked FieldDialog: {str(e)}")
            logger.error(f"Тип ошибки: {type(e).__name__}")
            logger.error(f"Трассировка: {traceback.format_exc()}")
            messagebox.showerror("Ошибка", f"Произошла ошибка при сохранении поля: {str(e)}")