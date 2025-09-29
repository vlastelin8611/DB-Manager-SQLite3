import sqlite3

print("=== ТЕСТ ТИПОВ ДАННЫХ SQLITE ===")

# Создаем временную БД в памяти
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Тестируем создание таблицы с разными типами
test_sql = '''CREATE TABLE test_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    age INTEGER DEFAULT 18,
    price REAL DEFAULT 0.0
)'''

print("SQL для создания:")
print(test_sql)

# Выполняем SQL
cursor.execute(test_sql)
conn.commit()

# Проверяем структуру
cursor.execute('PRAGMA table_info(test_types)')
columns = cursor.fetchall()

print("\nСтруктура созданной таблицы:")
for col in columns:
    cid, name, col_type, notnull, default, pk = col
    print(f"  {name}: {col_type} (NOT NULL: {bool(notnull)}, PK: {bool(pk)})")

# Проверяем вставку данных
cursor.execute("INSERT INTO test_types (name, description) VALUES (?, ?)", 
               ("Тест", "Описание теста"))

cursor.execute("SELECT * FROM test_types")
row = cursor.fetchone()

print(f"\nВставленные данные: {row}")
print(f"Типы Python: {[type(x) for x in row]}")

conn.close()

print("\n✅ Тест завершен успешно - типы данных работают корректно!")