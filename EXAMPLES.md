# Примеры использования SQLite Database Manager

## 🎯 Практические сценарии использования

### Сценарий 1: Создание учетной системы сотрудников

#### Шаг 1: Создание базы данных
1. Запустите программу: `python3 db_manager.py`
2. Файл → Новая база данных
3. Сохраните как `employees.db`

#### Шаг 2: Создание таблицы сотрудников
1. Нажмите "Создать таблицу"
2. Имя таблицы: `employees`
3. Добавьте поля:
   - `id` (INTEGER, Primary Key) - уже создано
   - `last_name` (TEXT, NOT NULL) - фамилия
   - `first_name` (TEXT, NOT NULL) - имя
   - `middle_name` (TEXT, NULL) - отчество
   - `position` (TEXT, NOT NULL) - должность
   - `department` (TEXT, NOT NULL) - отдел
   - `hire_date` (TEXT, NOT NULL) - дата приема
   - `salary` (REAL, NULL) - зарплата
   - `phone` (TEXT, NULL) - телефон
   - `email` (TEXT, NULL) - email

#### Шаг 3: Добавление данных
```sql
-- Через SQL запрос (Инструменты → SQL запрос)
INSERT INTO employees (last_name, first_name, middle_name, position, department, hire_date, salary, phone, email) VALUES
('Иванов', 'Иван', 'Иванович', 'Программист', 'ИТ', '2023-01-15', 80000, '+7-900-123-45-67', 'ivanov@company.ru'),
('Петров', 'Петр', 'Петрович', 'Аналитик', 'ИТ', '2023-02-01', 75000, '+7-900-234-56-78', 'petrov@company.ru'),
('Сидорова', 'Анна', 'Викторовна', 'Менеджер', 'Продажи', '2023-01-20', 65000, '+7-900-345-67-89', 'sidorova@company.ru');
```

#### Шаг 4: Полезные запросы
```sql
-- Все сотрудники ИТ отдела
SELECT last_name, first_name, position, salary 
FROM employees 
WHERE department = 'ИТ';

-- Средняя зарплата по отделам
SELECT department, AVG(salary) as avg_salary 
FROM employees 
GROUP BY department;

-- Сотрудники с зарплатой выше 70000
SELECT last_name, first_name, position, salary 
FROM employees 
WHERE salary > 70000 
ORDER BY salary DESC;
```

---

### Сценарий 2: Система учета товаров на складе

#### Таблица категорий
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT
);
```

#### Таблица товаров
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category_id INTEGER,
    price REAL NOT NULL,
    quantity INTEGER DEFAULT 0,
    min_quantity INTEGER DEFAULT 10,
    created_date TEXT,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

#### Заполнение данных
```sql
-- Категории
INSERT INTO categories (name, description) VALUES
('Электроника', 'Электронные устройства и компоненты'),
('Канцелярия', 'Канцелярские товары и принадлежности'),
('Мебель', 'Офисная и домашняя мебель');

-- Товары
INSERT INTO products (name, category_id, price, quantity, min_quantity, created_date) VALUES
('Ноутбук Dell', 1, 45000, 5, 2, '2023-01-10'),
('Мышь Logitech', 1, 1500, 25, 10, '2023-01-10'),
('Ручка синяя', 2, 15, 100, 50, '2023-01-10'),
('Стол офисный', 3, 12000, 3, 1, '2023-01-10');
```

#### Полезные запросы для склада
```sql
-- Товары, которые нужно заказать (количество меньше минимального)
SELECT p.name, p.quantity, p.min_quantity, c.name as category
FROM products p
JOIN categories c ON p.category_id = c.id
WHERE p.quantity < p.min_quantity;

-- Стоимость всех товаров на складе
SELECT 
    c.name as category,
    SUM(p.price * p.quantity) as total_value
FROM products p
JOIN categories c ON p.category_id = c.id
GROUP BY c.name;

-- Самые дорогие товары
SELECT name, price, quantity, (price * quantity) as total_cost
FROM products
ORDER BY price DESC
LIMIT 5;
```

---

### Сценарий 3: Система учета клиентов и заказов

#### Таблица клиентов
```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    company TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    registration_date TEXT
);
```

#### Таблица заказов
```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    order_date TEXT NOT NULL,
    total_amount REAL,
    status TEXT DEFAULT 'Новый',
    notes TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

#### Добавление тестовых данных
```sql
-- Клиенты
INSERT INTO customers (name, company, phone, email, address, registration_date) VALUES
('Иванов И.И.', 'ООО Рога и Копыта', '+7-900-111-22-33', 'ivanov@rk.ru', 'г. Москва, ул. Ленина, 1', '2023-01-05'),
('Петров П.П.', 'ИП Петров', '+7-900-222-33-44', 'petrov@mail.ru', 'г. СПб, пр. Мира, 15', '2023-01-10');

-- Заказы
INSERT INTO orders (customer_id, order_date, total_amount, status, notes) VALUES
(1, '2023-03-01', 15000, 'Выполнен', 'Заказ доставлен в срок'),
(1, '2023-03-15', 8500, 'В работе', 'Ожидаем поставку комплектующих'),
(2, '2023-03-10', 25000, 'Новый', 'Крупный заказ, требует особого внимания');
```

#### Аналитические запросы
```sql
-- Статистика по клиентам
SELECT 
    c.name,
    c.company,
    COUNT(o.id) as orders_count,
    SUM(o.total_amount) as total_spent
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name, c.company;

-- Заказы за текущий месяц
SELECT 
    o.id,
    c.name as customer,
    o.order_date,
    o.total_amount,
    o.status
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.order_date LIKE '2023-03%'
ORDER BY o.order_date DESC;

-- Заказы по статусам
SELECT 
    status,
    COUNT(*) as count,
    SUM(total_amount) as total_sum
FROM orders
GROUP BY status;
```

---

## 🔧 Технические приемы

### Резервное копирование перед важными операциями
```python
# Перед выполнением массовых изменений всегда делайте бэкап
# Файл → Резервная копия
```

### Оптимизация производительности
```sql
-- Создание индексов для ускорения поиска
CREATE INDEX idx_employee_department ON employees(department);
CREATE INDEX idx_customer_email ON customers(email);
CREATE INDEX idx_order_date ON orders(order_date);

-- Очистка и оптимизация БД
VACUUM; -- через Инструменты → Вакуум БД
```

### Работа с датами
```sql
-- SQLite хранит даты как текст, используйте формат YYYY-MM-DD
INSERT INTO orders (order_date, ...) VALUES ('2023-03-15', ...);

-- Поиск по датам
SELECT * FROM orders WHERE order_date >= '2023-03-01' AND order_date < '2023-04-01';

-- Функции для работы с датами
SELECT 
    order_date,
    strftime('%Y', order_date) as year,
    strftime('%m', order_date) as month,
    strftime('%d', order_date) as day
FROM orders;
```

### Экспорт данных
```sql
-- Для экспорта в CSV используйте простой SELECT
SELECT 
    last_name || ',' || first_name || ',' || position || ',' || salary
FROM employees;

-- Затем сохраните результат через "Сохранить результат" в диалоге SQL
```

---

## 🎓 Обучающие упражнения

### Упражнение 1: Библиотека
Создайте систему учета книг в библиотеке:
- Таблица авторов (authors)
- Таблица книг (books) 
- Таблица читателей (readers)
- Таблица выдач (loans)

### Упражнение 2: Интернет-магазин
Спроектируйте базу для интернет-магазина:
- Категории товаров
- Товары
- Пользователи
- Заказы
- Позиции заказов

### Упражнение 3: Учебное заведение
Создайте систему для управления учебным процессом:
- Студенты
- Преподаватели  
- Предметы
- Группы
- Оценки

---

## 💡 Полезные советы

### 1. Именование объектов
- Используйте понятные имена таблиц и полей
- Применяйте единый стиль (snake_case)
- Избегайте зарезервированных слов SQL

### 2. Типы данных
- TEXT для строк любой длины
- INTEGER для целых чисел
- REAL для дробных чисел
- Даты храните как TEXT в формате 'YYYY-MM-DD'

### 3. Ограничения целостности
- Всегда создавайте PRIMARY KEY
- Используйте NOT NULL для обязательных полей
- Применяйте FOREIGN KEY для связей

### 4. Безопасность данных
- Регулярно делайте резервные копии
- Проверяйте данные перед массовыми операциями
- Используйте транзакции для сложных операций

Удачного использования SQLite Database Manager! 🚀