from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import hashlib
from functools import wraps
import os

# Absolute path for database to avoid "Page Not Found" or "500 Error" on deployment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, 'pg_management.db')

app = Flask(__name__, 
            static_folder=os.path.join(BASE_DIR, 'static'),
            template_folder=os.path.join(BASE_DIR, 'templates'))
app.secret_key = 'rainbow_sparkle_pg_secret'

def get_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"DATABASE CONNECTION ERROR: {e}")
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'ADMIN':
            return "Halt! This area is for Admin Queens only 👑", 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    db = get_db()
    # Basic room search/listing
    room_type = request.args.get('type', 'all')
    if room_type == 'all':
        rooms = db.execute('SELECT * FROM rooms').fetchall()
    else:
        rooms = db.execute('SELECT * FROM rooms WHERE type = ?', (room_type,)).fetchall()
    db.close()
    return render_template('index.html', rooms=rooms)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_pass = hashlib.sha256(password.encode()).hexdigest()

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ? AND password_hash = ?', (email, hashed_pass)).fetchone()
        db.close()

        if user:
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            db.close()
            flash('Oops! Check your email or password sweetie! 💖')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_pass = hashlib.sha256(password.encode()).hexdigest()

        db = get_db()
        try:
            db.execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)', (name, email, hashed_pass))
            db.commit()
            flash('Yay! Registered successfully. Now login! 🌈')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists! Try another one 🌸')
        finally:
            db.close()
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if session.get('role') == 'ADMIN':
        return redirect(url_for('admin_dashboard'))
    
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if not user:
        db.close()
        session.clear()
        return redirect(url_for('login'))

    # Categorize bookings: Active (Staying, Confirmed) vs History (Vacated, Kicked Out)
    all_bookings = db.execute('''
        SELECT b.*, r.room_number, r.type 
        FROM bookings b JOIN rooms r ON b.room_id = r.id 
        WHERE b.user_id = ? ORDER BY b.created_at DESC''', (session['user_id'],)).fetchall()
    
    active_stays = [b for b in all_bookings if b['status'] in ['Staying', 'Confirmed']]
    stay_history = [b for b in all_bookings if b['status'] in ['Vacated', 'Kicked Out']]
    
    complaints = db.execute('SELECT * FROM complaints WHERE user_id = ? ORDER BY created_at DESC', (session['user_id'],)).fetchall()
    payments = db.execute('SELECT * FROM payments WHERE user_id = ? ORDER BY created_at DESC', (session['user_id'],)).fetchall()
    db.close()
    return render_template('resident_dashboard.html', active_stays=active_stays, stay_history=stay_history, complaints=complaints, payments=payments)

@app.route('/book/<int:room_id>', methods=['GET', 'POST'])
@login_required
def book_room(room_id):
    db = get_db()
    room = db.execute('SELECT * FROM rooms WHERE id = ?', (room_id,)).fetchone()
    
    if request.method == 'POST':
        start_date = request.form['start_date']
        duration = request.form['duration']
        
        if room['available_beds'] > 0:
            db.execute('INSERT INTO bookings (user_id, room_id, start_date, duration_months) VALUES (?,?,?,?)',
                       (session['user_id'], room_id, start_date, duration))
            db.execute('UPDATE rooms SET available_beds = available_beds - 1 WHERE id = ?', (room_id,))
            db.commit()
            flash('Room booked! Welcome home! ✨')
            db.close()
            return redirect(url_for('dashboard'))
        else:
            flash('Sorry, this room is full! 😢')
            
    db.close()
    return render_template('book_room.html', room=room)

@app.route('/complaint', methods=['POST'])
@login_required
def raise_complaint():
    title = request.form['title']
    desc = request.form['description']
    db = get_db()
    db.execute('INSERT INTO complaints (user_id, title, description) VALUES (?,?,?)', 
               (session['user_id'], title, desc))
    db.commit()
    db.close()
    flash('Complaint registered. We will fix it ASAP! ✨')
    return redirect(url_for('dashboard'))

# --- ADMIN ROUTES ---
@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    db = get_db()
    # Fetch bookings with room capacity info
    bookings = db.execute('''
        SELECT b.*, u.name as user_name, r.room_number, r.available_beds, r.total_beds 
        FROM bookings b 
        JOIN users u ON b.user_id = u.id 
        JOIN rooms r ON b.room_id = r.id
        ORDER BY b.created_at DESC''').fetchall()
    
    complaints = db.execute('''
        SELECT c.*, u.name as user_name 
        FROM complaints c 
        JOIN users u ON c.user_id = u.id
        ORDER BY c.created_at DESC''').fetchall()
    
    total_revenue = db.execute('SELECT SUM(amount) FROM payments WHERE status="Paid"').fetchone()[0] or 0
    db.close()
    return render_template('admin_dashboard.html', bookings=bookings, complaints=complaints, revenue=total_revenue)

@app.route('/admin/update_booking/<int:booking_id>', methods=['POST'])
@login_required
@admin_required
def update_booking_status(booking_id):
    new_status = request.form['status']
    db = get_db()
    
    # Get current booking and room capacity
    booking = db.execute('''
        SELECT b.room_id, b.status, r.available_beds, r.total_beds 
        FROM bookings b JOIN rooms r ON b.room_id = r.id 
        WHERE b.id = ?''', (booking_id,)).fetchone()
    
    if booking:
        old_status = booking['status']
        active_statuses = ['Staying', 'Confirmed']
        inactive_statuses = ['Vacated', 'Kicked Out']
        
        # If status is NOT changing, just redirect
        if old_status == new_status:
            db.close()
            return redirect(url_for('admin_dashboard'))

        error = None
        # Logic: Releasing a bed
        if old_status in active_statuses and new_status in inactive_statuses:
            # Only increment if it's below total beds (prevent accidental double increments)
            if booking['available_beds'] < booking['total_beds']:
                db.execute('UPDATE rooms SET available_beds = available_beds + 1 WHERE id = ?', (booking['room_id'],))
                print(f"DEBUG: Bed released for Room {booking['room_id']}. New status: {new_status}")
            else:
                print(f"DEBUG: Room {booking['room_id']} already at max capacity. Increment skipped.")

        # Logic: Occupying a bed (re-activating a stay)
        elif old_status in inactive_statuses and new_status in active_statuses:
            if booking['available_beds'] > 0:
                db.execute('UPDATE rooms SET available_beds = available_beds - 1 WHERE id = ?', (booking['room_id'],))
                print(f"DEBUG: Bed occupied for Room {booking['room_id']}. New status: {new_status}")
            else:
                error = "Cannot set to active - Room is already FULL! ⚠️"
                print(f"DEBUG: Failed to occupy bed for Room {booking['room_id']} - FULL.")

        if not error:
            db.execute('UPDATE bookings SET status = ? WHERE id = ?', (new_status, booking_id))
            db.commit()
            flash(f'Status updated to {new_status}! 🌈')
        else:
            flash(error)
    
    db.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/resolve/<int:complaint_id>')
@login_required
@admin_required
def resolve_complaint(complaint_id):
    db = get_db()
    db.execute('UPDATE complaints SET status = "Resolved" WHERE id = ?', (complaint_id,))
    db.commit()
    db.close()
    flash('Complaint marked as resolved! ✅')
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
