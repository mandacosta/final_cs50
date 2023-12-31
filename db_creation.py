import sqlite3

connection = sqlite3.connect("database.db")

cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        gender TEXT,
        birth TEXT,
        password_hash TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER,
        name TEXT,
        description TEXT,
        creation_date TEXT,
        event_date TEXT,
        draw_date TEXT,
        image_url TEXT,
        FOREIGN KEY (owner_id) REFERENCES users(id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS groups_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER,
        user_id INTEGER,
        addtion_date TEXT,
        FOREIGN KEY (group_id) REFERENCES groups(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS draw (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER,
        took_id INTEGER,
        taken_id INTEGER,
        date TEXT,
        FOREIGN KEY (group_id) REFERENCES groups(id),
        FOREIGN KEY (took_id) REFERENCES users(id),
        FOREIGN KEY (taken_id) REFERENCES users(id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS gift_option (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gift TEXT,
        description TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS group_user_option (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_user_id INTEGER,
        gift_option_id INTEGER,
        FOREIGN KEY (group_user_id) REFERENCES groups_users(id),
        FOREIGN KEY (gift_option_id) REFERENCES gift_option(id)
    )
""")


connection.commit()
connection.close()