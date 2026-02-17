import sqlite3
import hashlib

def init_db():
    conn = sqlite3.connect('pg_management.db')
    c = conn.cursor()

    c.execute('DROP TABLE IF EXISTS users')
    c.execute('DROP TABLE IF EXISTS rooms')
    c.execute('DROP TABLE IF EXISTS bookings')
    c.execute('DROP TABLE IF EXISTS complaints')
    c.execute('DROP TABLE IF EXISTS payments')

    # Users Table
    c.execute('''CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'RESIDENT',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # Rooms Table
    c.execute('''CREATE TABLE rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_number TEXT UNIQUE NOT NULL,
        type TEXT NOT NULL,
        price_per_month REAL NOT NULL,
        total_beds INTEGER NOT NULL,
        available_beds INTEGER NOT NULL
    )''')

    # Bookings Table (Status: Confirmed, Staying, Vacated, Kicked Out)
    c.execute('''CREATE TABLE bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        room_id INTEGER,
        start_date DATE,
        duration_months INTEGER,
        status TEXT DEFAULT 'Confirmed',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (room_id) REFERENCES rooms (id)
    )''')

    c.execute('''CREATE TABLE complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'Pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')

    c.execute('''CREATE TABLE payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        month TEXT,
        status TEXT DEFAULT 'Paid',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')

    common_pass = hashlib.sha256('password123'.encode()).hexdigest()
    admin_pass = hashlib.sha256('admin123'.encode()).hexdigest()

    # Dynamic Users
    users_data = [
        ('Hostel Warden Maya', 'admin@example.com', admin_pass, 'ADMIN'),
        ('Ananya Sharma', 'ananya@example.com', common_pass, 'RESIDENT'),
        ('Priya Reddy', 'priya@example.com', common_pass, 'RESIDENT'),
        ('Sita Lakshmi', 'sita@example.com', common_pass, 'RESIDENT'),
        ('Kavya Singh', 'kavya@example.com', common_pass, 'RESIDENT'),
        ('Sneha Kapoor', 'sneha@example.com', common_pass, 'RESIDENT')
    ]
    c.executemany("INSERT INTO users (name, email, password_hash, role) VALUES (?,?,?,?)", users_data)

    # Rooms Setup (Total 14 beds, only ~7 occupied = 50% capacity)
    rooms_data = [
        ('101', '1-sharing', 16000, 1, 0), # Occupied by Ananya (Staying)
        ('102', '1-sharing', 16000, 1, 1), # Empty
        ('201', '2-sharing', 9000, 2, 1),  # 1 Occupied by Priya (Staying), 1 Free
        ('202', '2-sharing', 9000, 2, 2),  # Full Empty
        ('301', '3-sharing', 7000, 3, 2),  # 1 Occupied by Sita (Staying), 2 Free
        ('401', '5-sharing', 5000, 5, 4)   # 1 Occupied by Kavya (Staying), 4 Free
    ]
    c.executemany("INSERT INTO rooms (room_number, type, price_per_month, total_beds, available_beds) VALUES (?,?,?,?,?)", rooms_data)

    # Bookings Data (Real History and Current Stays)
    # statuses: Confirmed, Staying, Vacated, Kicked Out
    bookings_data = [
        # Ananya: Current staying
        (2, 1, '2026-01-01', 12, 'Staying'),
        # Ananya: Historical stay in same PG but different room/type (Vacated)
        (2, 4, '2025-06-01', 6, 'Vacated'),
        
        # Priya: Current staying
        (3, 3, '2026-02-01', 6, 'Staying'),
        
        # Sita: Just confirmed, not yet check-in
        (4, 5, '2026-03-01', 3, 'Confirmed'),
        
        # Kavya: Currently staying
        (5, 6, '2026-01-15', 6, 'Staying'),
        
        # Sneha: Was staying but Kicked Out for loud music 😂
        (6, 3, '2025-01-01', 1, 'Kicked Out')
    ]
    c.executemany("INSERT INTO bookings (user_id, room_id, start_date, duration_months, status) VALUES (?,?,?,?,?)", bookings_data)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database Updated: 50% Capacity, History Saved, New Statuses! 🌈🏠👑")
