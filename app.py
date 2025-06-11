from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('doctor.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('login_options.html')

@app.route('/doctor_loc')
def doctor_loc():
    conn = get_db_connection()
    locations = conn.execute('SELECT DISTINCT location FROM doctors').fetchall()
    conn.close()
    location_list = [loc['location'] for loc in locations]
    return render_template('doctor_loc.html', locations=location_list)

@app.route('/select_doctor', methods=['POST'])
def select_doctor():
    location = request.form['location']
    conn = get_db_connection()
    doctors = conn.execute('SELECT * FROM doctors WHERE location = ?', (location,)).fetchall()
    conn.close()
    return render_template('select_doctor.html', doctors=doctors)

def get_available_slots_for_date_and_doctor(doctor_id, date_str):
    conn = get_db_connection()
    base_time = datetime.strptime("09:00", "%H:%M")
    slots = [(base_time + timedelta(hours=i)).strftime("%H:%M") for i in range(13)]
    available_slots = []
    now = datetime.now()
    selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    for slot in slots:
        slot_datetime = datetime.strptime(f"{selected_date} {slot}", "%Y-%m-%d %H:%M")
        if selected_date == now.date() and slot_datetime < now:
            continue
        count = conn.execute('''
            SELECT COUNT(*) FROM appointments 
            WHERE doctor_id = ? AND appointment_date = ? AND appointment_time = ?
        ''', (doctor_id, date_str, slot)).fetchone()[0]
        if count < 4:
            available_slots.append(slot)

    conn.close()
    return available_slots

@app.route('/doctor_profile/<int:doctor_id>', methods=['GET', 'POST'])
def doctor_profile(doctor_id):
    conn = get_db_connection()
    doctor = conn.execute('SELECT * FROM doctors WHERE id = ?', (doctor_id,)).fetchone()

    if doctor is None:
        return "Doctor Not Found", 404

    base_time = datetime.strptime("09:00", "%H:%M")
    slots = [(base_time + timedelta(hours=i)).strftime("%H:%M") for i in range(13)]
    available_slots = []
    today = datetime.now().date()
    now = datetime.now()
    selected_date = request.args.get('date')
    appointment_date = datetime.strptime(selected_date, "%Y-%m-%d").date() if selected_date else today

    for slot in slots:
        slot_datetime = datetime.strptime(f"{appointment_date} {slot}", "%Y-%m-%d %H:%M")
        if appointment_date == today and slot_datetime < now:
            continue
        count = conn.execute('''SELECT COUNT(*) FROM appointments 
                                WHERE doctor_id = ? AND appointment_date = ? AND appointment_time = ?''',
                             (doctor_id, str(appointment_date), slot)).fetchone()[0]
        if count < 4:
            available_slots.append(slot)

    conn.close()
    return render_template('doctor_profile.html', doctor=doctor, available_slots=available_slots)

@app.route('/enter_patient_details/<int:doctor_id>', methods=['POST'])
def enter_patient_details(doctor_id):
    date = request.form['date']
    time = request.form['time']
    conn = get_db_connection()
    doctor = conn.execute('SELECT * FROM doctors WHERE id = ?', (doctor_id,)).fetchone()
    conn.close()
    return render_template('enter_patient_details.html', doctor=doctor, date=date, time=time)

@app.route('/booking_successful')
def booking_successful():
    return render_template('booking_successful.html')

@app.route('/get_available_slots_for_date')
def get_available_slots_for_date():
    date = request.args.get('date')
    doctor_id = request.args.get('doctor_id')
    available_slots = get_available_slots_for_date_and_doctor(doctor_id, date)
    return jsonify({'available_slots': available_slots})

@app.route('/user_signup', methods=['GET', 'POST'])
def user_signup():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        blood_group = request.form['blood_group']
        dob = request.form['dob']
        medical_history = request.form['medical_history']
        username = request.form['username']
        password = request.form['password']
        cpassword = request.form['cpassword']

        if password != cpassword:
            flash('Passwords do not match!', 'danger')
            return render_template('user_signup.html')

        conn = get_db_connection()
        try:
            conn.execute('''INSERT INTO users 
                            (name, age, blood_group, dob, medical_history, username, password) 
                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                         (name, age, blood_group, dob, medical_history, username, password))
            conn.commit()
            flash('Account Created Successfully!', 'success')
            return redirect('/user_login')
        except Exception as e:
            flash(f'Username already exists or other error: {e}', 'danger')
        conn.close()

    return render_template('user_signup.html')

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        if user:
            session['user'] = username
            return redirect('/Homepage')
        else:
            flash('Invalid Username or Password', 'danger')
    return render_template('user_login.html')

@app.route('/user_profile')
def user_profile():
    if 'user' not in session:
        return redirect('/user_login')
    username = session['user']
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    if user:
        return render_template('user_profile.html', user=user)
    else:
        flash('User not found', 'danger')
        return redirect('/user_login')

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user' not in session:
        return redirect('/user_login')
    username = session['user']
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        blood_group = request.form['blood_group']
        dob = request.form['dob']
        medical_history = request.form['medical_history']
        try:
            conn.execute('''UPDATE users 
                            SET name = ?, age = ?, blood_group = ?, dob = ?, medical_history = ? 
                            WHERE username = ?''',
                         (name, age, blood_group, dob, medical_history, username))
            conn.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('user_profile'))
        except Exception as e:
            flash(f"Error updating profile: {e}", 'danger')
            conn.rollback()
    conn.close()
    return render_template('edit_profile.html', user=user)

@app.route("/appointments")
def view_appointments():
    if 'user' not in session:
        return redirect('/login')

    username = session['user']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT doctor_name, appointment_date, appointment_time, status 
        FROM appointments 
        WHERE patient_email = ?
        ORDER BY appointment_date DESC
    """, (username,))
    rows = cursor.fetchall()
    conn.close()
    appointments = [{'doctor_name': r[0], 'date': r[1], 'time': r[2], 'status': r[3]} for r in rows]
    return render_template("appointments.html", appointments=appointments)

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect('/login')

    username = session['user']
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT name, age, blood_group, dob, history, username FROM users WHERE username = ?", (username,))
    user_data = c.fetchone()
    conn.close()

    user = {
        'name': user_data[0],
        'age': user_data[1],
        'blood_group': user_data[2],
        'dob': user_data[3],
        'history': user_data[4],
        'username': user_data[5],
    }
    return render_template('edit_profile.html', user=user)
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        date = request.form.get('date')  # Returns None if 'date' is missing
        name = request.form['name']
        message = request.form['message']
        print(f"Message from {name} ({email}): {message}")
        flash('Thank you for contacting us. We will get back to you soon!', 'success')
        return redirect('/contact')
    return render_template('contact.html')

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user' not in session:
        return redirect('/login')

    name = request.form['name']
    age = request.form['age']
    blood_group = request.form['blood_group']
    dob = request.form['dob']
    history = request.form['history']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    username = session['user']

    if password and password != confirm_password:
        flash('Passwords do not match', 'danger')
        return redirect('/profile')

    conn = get_db_connection()
    c = conn.cursor()

    if password:
        c.execute('''
            UPDATE users SET name=?, age=?, blood_group=?, dob=?, history=?, password=?
            WHERE username=?
        ''', (name, age, blood_group, dob, history, password, username))
    else:
        c.execute('''
            UPDATE users SET name=?, age=?, blood_group=?, dob=?, history=?
            WHERE username=?
        ''', (name, age, blood_group, dob, history, username))

    conn.commit()
    conn.close()
    flash('Profile updated successfully!', 'success')
    return redirect('/profile')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if username == 'admin' and password == 'admin123':
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash('Invalid Admin Credentials', 'danger')
    return render_template('admin_login.html')

@app.route('/admin')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    appointments = conn.execute('SELECT * FROM appointments').fetchall()
    conn.close()
    return render_template('admin_panel.html', appointments=appointments)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('user_login'))

@app.route('/medic')
def medic():
    return render_template('medic.html')

@app.route('/insurance')
def insurance():
    return render_template('Insurance.html')

@app.route('/Homepage')
def Homepage():
    return render_template('Homepage.html')

@app.route('/final_booking/<int:doctor_id>', methods=['POST'])
def final_booking(doctor_id):
    patient_name = request.form['patient_name']
    patient_phone = request.form['patient_phone']
    patient_username = session.get('user')
    doctor_name = request.form['doctor_name']
    doctor_hospital = request.form['doctor_hospital']
    appointment_date = request.form['date']
    appointment_time = request.form['time']

    conn = get_db_connection()
    conn.execute('''INSERT INTO appointments 
                    (doctor_id, doctor_name, doctor_hospital, patient_name, patient_phone, patient_email, appointment_date, appointment_time) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                 (doctor_id, doctor_name, doctor_hospital, patient_name, patient_phone, patient_username, appointment_date, appointment_time))
    conn.commit()
    conn.close()

    return redirect(url_for('booking_successful'))

@app.route('/doctor_list')
def doctor_list():
    conn = get_db_connection()
    doctors = conn.execute('SELECT * FROM doctors').fetchall()
    conn.close()
    return render_template('doctor_list.html', doctors=doctors)

if __name__ == '__main__':
    app.run(debug=True)
