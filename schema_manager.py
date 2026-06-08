import sqlite3
import os

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASES = {
    "ecommerce": os.path.join(DB_DIR, "ecommerce.db"),
    "company": os.path.join(DB_DIR, "company.db"),
    "music": os.path.join(DB_DIR, "music.db"),
    "custom": os.path.join(DB_DIR, "custom.db")
}

def get_connection(db_key):
    if db_key not in DATABASES:
        raise ValueError(f"Database {db_key} not registered.")
    db_path = DATABASES[db_key]
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys support in SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_databases():
    """Initializes and seeds the sample databases if they do not exist."""
    init_ecommerce()
    init_company()
    init_music()

def init_ecommerce():
    db_path = DATABASES["ecommerce"]
    # We will seed fresh data to ensure rich datasets
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Drop tables to recreate with clean seeded data
    cursor.execute("DROP TABLE IF EXISTS order_items;")
    cursor.execute("DROP TABLE IF EXISTS orders;")
    cursor.execute("DROP TABLE IF EXISTS products;")
    cursor.execute("DROP TABLE IF EXISTS customers;")
    
    # Create tables
    cursor.execute("""
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        city TEXT,
        join_date TEXT NOT NULL
    );
    """)
    
    cursor.execute("""
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        stock_quantity INTEGER NOT NULL
    );
    """)
    
    cursor.execute("""
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        order_date TEXT NOT NULL,
        total_amount REAL NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE order_items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
    """)
    
    # Seed data
    customers = [
        ("Sarah", "Connor", "sarah.connor@sky.net", "Los Angeles", "2025-01-15"),
        ("John", "Doe", "john.doe@gmail.com", "New York", "2025-02-10"),
        ("Alice", "Smith", "alice.s@yahoo.com", "San Francisco", "2025-03-01"),
        ("Bob", "Johnson", "bob.j@gmail.com", "Chicago", "2025-03-15"),
        ("Emma", "Watson", "emma.w@outlook.com", "Los Angeles", "2025-04-02"),
        ("Michael", "Jordan", "m.jordan@bulls.com", "Chicago", "2025-04-10"),
        ("David", "Beckham", "d.beckham@galaxy.com", "Miami", "2025-05-01"),
        ("Bruce", "Wayne", "bruce@waynecorp.com", "Gotham", "2025-05-12"),
        ("Clark", "Kent", "clark.k@dailyplanet.com", "Metropolis", "2025-05-20"),
        ("Peter", "Parker", "spidey@dailybugle.com", "New York", "2025-06-01")
    ]
    cursor.executemany("INSERT INTO customers (first_name, last_name, email, city, join_date) VALUES (?, ?, ?, ?, ?);", customers)
    
    products = [
        ("iPhone 15 Pro", "Electronics", 999.99, 50),
        ("Samsung Galaxy S24", "Electronics", 899.99, 45),
        ("MacBook Air M3", "Electronics", 1199.99, 30),
        ("Sony WH-1000XM5", "Audio", 349.99, 80),
        ("Bose QuietComfort Ultra", "Audio", 429.99, 60),
        ("Nike Air Max", "Footwear", 150.00, 120),
        ("Adidas Ultraboost", "Footwear", 180.00, 100),
        ("Levi's 501 Original", "Apparel", 79.99, 150),
        ("Patagonia Down Sweater", "Apparel", 229.00, 40),
        ("Dell XPS 15", "Electronics", 1499.99, 15)
    ]
    cursor.executemany("INSERT INTO products (name, category, price, stock_quantity) VALUES (?, ?, ?, ?);", products)
    
    orders = [
        (1, "2025-02-15", 1349.98, "Completed"),
        (2, "2025-02-20", 899.99, "Completed"),
        (3, "2025-03-05", 229.99, "Shipped"),
        (4, "2025-03-18", 1549.98, "Completed"),
        (5, "2025-04-05", 79.99, "Processing"),
        (1, "2025-04-12", 429.99, "Completed"),
        (6, "2025-04-20", 300.00, "Shipped"),
        (7, "2025-05-05", 180.00, "Completed"),
        (8, "2025-05-15", 2699.98, "Completed"),
        (9, "2025-05-25", 79.99, "Pending"),
        (10, "2025-06-02", 499.99, "Completed")
    ]
    cursor.executemany("INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES (?, ?, ?, ?);", orders)
    
    order_items = [
        (1, 1, 1, 999.99), # order 1, product 1 (iPhone), Qty 1
        (1, 4, 1, 349.99), # order 1, product 4 (Sony), Qty 1
        (2, 2, 1, 899.99), # order 2, product 2 (Samsung)
        (3, 8, 1, 79.99),  # order 3, product 8 (Levi's)
        (3, 6, 1, 150.00), # order 3, product 6 (Nike)
        (4, 3, 1, 1199.99),# order 4, product 3 (MacBook)
        (4, 4, 1, 349.99), # order 4, product 4 (Sony)
        (5, 8, 1, 79.99),  # order 5, product 8 (Levi's)
        (6, 5, 1, 429.99), # order 6, product 5 (Bose)
        (7, 6, 2, 150.00), # order 7, product 6 (Nike) x 2
        (8, 7, 1, 180.00), # order 8, product 7 (Adidas)
        (9, 3, 1, 1199.99),# order 9, product 3 (MacBook)
        (9, 10, 1, 1499.99),# order 9, product 10 (Dell XPS)
        (10, 8, 1, 79.99), # order 10, product 8 (Levi's)
        (11, 4, 1, 349.99), # order 11, product 4 (Sony)
        (11, 6, 1, 150.00)  # order 11, product 6 (Nike)
    ]
    cursor.executemany("INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?);", order_items)
    
    conn.commit()
    conn.close()

def init_company():
    db_path = DATABASES["company"]
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    cursor.execute("DROP TABLE IF EXISTS employee_projects;")
    cursor.execute("DROP TABLE IF EXISTS projects;")
    cursor.execute("DROP TABLE IF EXISTS employees;")
    cursor.execute("DROP TABLE IF EXISTS departments;")
    
    cursor.execute("""
    CREATE TABLE departments (
        dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
        dept_name TEXT NOT NULL,
        manager_id INTEGER,
        location TEXT
    );
    """)
    
    cursor.execute("""
    CREATE TABLE employees (
        emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        hire_date TEXT NOT NULL,
        salary REAL NOT NULL,
        dept_id INTEGER,
        FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE projects (
        project_id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT NOT NULL,
        budget REAL NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT
    );
    """)
    
    cursor.execute("""
    CREATE TABLE employee_projects (
        emp_id INTEGER NOT NULL,
        project_id INTEGER NOT NULL,
        hours_worked REAL NOT NULL,
        role TEXT NOT NULL,
        PRIMARY KEY (emp_id, project_id),
        FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE,
        FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
    );
    """)
    
    # Seed data
    departments = [
        ("Engineering", 1, "San Francisco"),
        ("Sales", 3, "New York"),
        ("Marketing", 5, "Los Angeles"),
        ("Human Resources", 8, "Chicago"),
        ("Finance", 10, "New York")
    ]
    cursor.executemany("INSERT INTO departments (dept_name, manager_id, location) VALUES (?, ?, ?);", departments)
    
    employees = [
        ("Jared", "Hendricks", "jared@company.com", "555-0101", "2020-05-10", 125000.00, 1),
        ("Sarah", "Jenkins", "sarah@company.com", "555-0102", "2021-03-12", 98000.00, 1),
        ("David", "Miller", "david@company.com", "555-0103", "2019-11-01", 115000.00, 2),
        ("Emily", "Davis", "emily@company.com", "555-0104", "2022-08-15", 72000.00, 2),
        ("Michael", "Clark", "michael@company.com", "555-0105", "2018-02-14", 105000.00, 3),
        ("Jessica", "Taylor", "jessica@company.com", "555-0106", "2023-01-10", 65000.00, 3),
        ("Kevin", "Martin", "kevin@company.com", "555-0107", "2020-10-20", 92000.00, 1),
        ("Amanda", "White", "amanda@company.com", "555-0108", "2017-06-01", 85000.00, 4),
        ("Robert", "Jackson", "robert@company.com", "555-0109", "2022-11-05", 68000.00, 4),
        ("Lisa", "Anderson", "lisa@company.com", "555-0110", "2016-04-18", 130000.00, 5),
        ("Thomas", "Brown", "thomas@company.com", "555-0111", "2023-04-01", 75000.00, 5)
    ]
    cursor.executemany("INSERT INTO employees (first_name, last_name, email, phone, hire_date, salary, dept_id) VALUES (?, ?, ?, ?, ?, ?, ?);", employees)
    
    projects = [
        ("Cloud Migration", 250000.00, "2025-01-01", "2025-08-30"),
        ("CRM Overhaul", 120000.00, "2025-03-15", "2025-12-15"),
        ("Global Branding Sync", 85000.00, "2025-02-01", "2025-07-01"),
        ("Corporate Restructuring", 45000.00, "2025-05-01", "2025-10-01"),
        ("Q3 Financial Audit", 30000.00, "2025-06-01", "2025-09-30")
    ]
    cursor.executemany("INSERT INTO projects (project_name, budget, start_date, end_date) VALUES (?, ?, ?, ?);", projects)
    
    employee_projects = [
        (1, 1, 120.5, "Lead Architect"),
        (2, 1, 240.0, "Frontend Engineer"),
        (7, 1, 180.0, "DevOps Specialist"),
        (3, 2, 150.0, "Project Sponsor"),
        (4, 2, 320.0, "Sales Analyst"),
        (5, 3, 90.0, "Marketing Lead"),
        (6, 3, 200.0, "Content Designer"),
        (8, 4, 60.0, "HR Coordinator"),
        (9, 4, 110.0, "Legal Liaison"),
        (10, 5, 80.0, "Financial Director"),
        (11, 5, 140.0, "Senior Auditor"),
        (2, 2, 50.0, "UI Support") # Emily working on CRM overhaul
    ]
    cursor.executemany("INSERT INTO employee_projects (emp_id, project_id, hours_worked, role) VALUES (?, ?, ?, ?);", employee_projects)
    
    conn.commit()
    conn.close()

def init_music():
    db_path = DATABASES["music"]
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    cursor.execute("DROP TABLE IF EXISTS listening_history;")
    cursor.execute("DROP TABLE IF EXISTS users;")
    cursor.execute("DROP TABLE IF EXISTS songs;")
    cursor.execute("DROP TABLE IF EXISTS albums;")
    cursor.execute("DROP TABLE IF EXISTS artists;")
    
    cursor.execute("""
    CREATE TABLE artists (
        artist_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        genre TEXT,
        country TEXT
    );
    """)
    
    cursor.execute("""
    CREATE TABLE albums (
        album_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        artist_id INTEGER NOT NULL,
        release_year INTEGER,
        FOREIGN KEY (artist_id) REFERENCES artists(artist_id)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE songs (
        song_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        album_id INTEGER NOT NULL,
        duration_seconds INTEGER NOT NULL,
        play_count INTEGER DEFAULT 0,
        FOREIGN KEY (album_id) REFERENCES albums(album_id)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        premium_member INTEGER DEFAULT 0
    );
    """)
    
    cursor.execute("""
    CREATE TABLE listening_history (
        history_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        song_id INTEGER NOT NULL,
        listen_timestamp TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (song_id) REFERENCES songs(song_id)
    );
    """)
    
    # Seed data
    artists = [
        ("The Beatles", "Rock", "UK"),
        ("Taylor Swift", "Pop", "USA"),
        ("Daft Punk", "Electronic", "France"),
        ("Miles Davis", "Jazz", "USA"),
        ("Coldplay", "Alternative", "UK"),
        ("Eminem", "Hip Hop", "USA"),
        ("Hans Zimmer", "Soundtrack", "Germany"),
        ("Billie Eilish", "Alternative", "USA")
    ]
    cursor.executemany("INSERT INTO artists (name, genre, country) VALUES (?, ?, ?);", artists)
    
    albums = [
        ("Abbey Road", 1, 1969),          # Beatles
        ("1989 (Taylor's Version)", 2, 2023), # Taylor Swift
        ("Random Access Memories", 3, 2013),  # Daft Punk
        ("Kind of Blue", 4, 1959),         # Miles Davis
        ("A Rush of Blood to the Head", 5, 2002), # Coldplay
        ("The Marshall Mathers LP", 6, 2000), # Eminem
        ("Interstellar", 7, 2014),         # Hans Zimmer
        ("HIT ME HARD AND SOFT", 8, 2024)   # Billie Eilish
    ]
    cursor.executemany("INSERT INTO albums (title, artist_id, release_year) VALUES (?, ?, ?);", albums)
    
    songs = [
        ("Come Together", 1, 259, 154200),
        ("Here Comes the Sun", 1, 185, 290100),
        ("Blank Space", 2, 231, 420800),
        ("Style", 2, 231, 350100),
        ("Get Lucky", 3, 369, 580200),
        ("Instant Crush", 3, 337, 490500),
        ("So What", 4, 562, 98200),
        ("Flamenco Sketches", 4, 562, 45100),
        ("Clocks", 5, 307, 310500),
        ("The Scientist", 5, 309, 450900),
        ("Lose Yourself", 6, 326, 680400),
        ("Cornfield Chase", 7, 126, 210200),
        ("Stay", 7, 412, 190400),
        ("LUNCH", 8, 180, 250100),
        ("CHIHIRO", 8, 303, 280400)
    ]
    cursor.executemany("INSERT INTO songs (title, album_id, duration_seconds, play_count) VALUES (?, ?, ?, ?);", songs)
    
    users = [
        ("music_lover", "lover@music.com", 1),
        ("vinyl_collector", "collector@retro.com", 1),
        ("casual_listener", "casual@gmail.com", 0),
        ("rocker_99", "rocker@yahoo.com", 0),
        ("jazz_cat", "jazzcat@outlook.com", 1),
        ("pop_fan", "popfan@gmail.com", 1)
    ]
    cursor.executemany("INSERT INTO users (username, email, premium_member) VALUES (?, ?, ?);", users)
    
    listening_history = [
        (1, 2, "2025-06-01 10:15:30"),
        (1, 5, "2025-06-01 10:20:00"),
        (2, 9, "2025-06-01 11:00:22"),
        (3, 3, "2025-06-01 12:45:10"),
        (4, 1, "2025-06-01 14:30:15"),
        (5, 7, "2025-06-01 16:15:00"),
        (6, 3, "2025-06-01 17:05:40"),
        (6, 4, "2025-06-01 17:10:00"),
        (6, 14, "2025-06-01 17:15:00"),
        (2, 11, "2025-06-02 09:30:00"),
        (1, 15, "2025-06-02 10:45:22")
    ]
    cursor.executemany("INSERT INTO listening_history (user_id, song_id, listen_timestamp) VALUES (?, ?, ?);", listening_history)
    
    conn.commit()
    conn.close()

def get_database_schema(db_key):
    """
    Returns the schema of the specified database key.
    Format:
    {
        "tables": {
            "table_name": {
                "columns": [
                    {"name": "col_name", "type": "TEXT", "pk": 1, "fk": {"table": "other_table", "to": "other_col"}}
                ],
                "row_count": 12
            }
        },
        "relationships": [
            {"from_table": "orders", "from_col": "customer_id", "to_table": "customers", "to_col": "customer_id"}
        ]
    }
    """
    conn = get_connection(db_key)
    cursor = conn.cursor()
    
    # 1. Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]
    
    schema = {
        "tables": {},
        "relationships": []
    }
    
    for table in tables:
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        row_count = cursor.fetchone()[0]
        
        # Get columns
        cursor.execute(f"PRAGMA table_info({table});")
        columns_info = cursor.fetchall()
        
        # Get foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table});")
        fkeys_info = cursor.fetchall()
        
        # Build fkeys dictionary for mapping
        fkeys = {}
        for fk in fkeys_info:
            # fk schema: (id, seq, table, from, to, on_update, on_delete, match)
            fkeys[fk[3]] = {
                "table": fk[2],
                "to": fk[4]
            }
            # Record global relationship list
            schema["relationships"].append({
                "from_table": table,
                "from_col": fk[3],
                "to_table": fk[2],
                "to_col": fk[4]
            })
            
        columns = []
        for col in columns_info:
            # col schema: (cid, name, type, notnull, dflt_value, pk)
            col_name = col[1]
            columns.append({
                "name": col_name,
                "type": col[2],
                "pk": col[5],
                "fk": fkeys.get(col_name)
            })
            
        schema["tables"][table] = {
            "columns": columns,
            "row_count": row_count
        }
        
    conn.close()
    return schema

def execute_query(db_key, query_sql):
    """
    Executes a query and returns the results.
    Enforces basic safety limits (MAX 100 rows, read-only statements check).
    """
    query_upper = query_sql.strip().upper()
    
    # We do a basic check to prevent arbitrary drops or modifications if the query is not SELECT.
    # Note: We want to support DDL for custom database creation, but for general querying, we restrict it.
    is_write = any(query_upper.startswith(word) for word in ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "REPLACE"])
    
    conn = get_connection(db_key)
    cursor = conn.cursor()
    
    try:
        if is_write:
            # For writes, execute and commit, returning number of rows affected
            cursor.execute(query_sql)
            conn.commit()
            rows_affected = cursor.rowcount
            return {
                "success": True,
                "type": "write",
                "rows_affected": rows_affected,
                "message": f"Query executed successfully. Rows affected: {rows_affected}."
            }
        else:
            # For SELECT, execute and fetch
            cursor.execute(query_sql)
            
            # Fetch column headers
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
            # Limit to 100 rows to prevent crashes
            rows = cursor.fetchmany(100)
            
            results = []
            for row in rows:
                results.append(dict(row))
                
            return {
                "success": True,
                "type": "read",
                "columns": columns,
                "rows": results,
                "total_rows": len(results),
                "has_more": len(cursor.fetchmany(1)) > 0
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        conn.close()

if __name__ == "__main__":
    init_databases()
    print("Databases initialized successfully.")
    schema = get_database_schema("ecommerce")
    print("E-commerce Tables:", list(schema["tables"].keys()))
