import sqlite3

DATABASE = 'scheduled_posts.db'

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT,
    platforms TEXT,
    image TEXT,
    scheduled_time DATETIME
)
''')

conn.commit()
conn.close()

print("Database initialized successfully.")
