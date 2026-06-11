from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ.get("SECRET_KEY")
print("starting flask")
# --- MySQL Connection ---
db_config = {
    'host':     os.environ.get('DB_HOST', 'localhost'),
    'user':     os.environ.get('DB_USER', 'flaskuser'),           # your DB user
    'password': os.environ.get('DB_PASSWORD', 'Mehnaz13@MYSQL.'),   # your DB password
    'database': os.environ.get('DB_NAME', 'blood_system')         # or 'bloodbank'
}
db = mysql.connector.connect(**db_config)
cursor = db.cursor(dictionary=True)

# --- Helper Functions ---
def get_user_by_email(email):
    cursor.execute("SELECT * FROM Users WHERE email=%s", (email,))
    return cursor.fetchone()

def create_user(name, email, password, role):
    pw_hash = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO Users (name,email,password_hash,role) VALUES (%s,%s,%s,%s)",
        (name, email, pw_hash, role)
    )
    db.commit()

# --- Routes ---

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', role=session.get('role'))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        create_user(
            request.form['name'],
            request.form['email'],
            request.form['password'],
            request.form['role']
        )
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = get_user_by_email(request.form['email'])
        if user and check_password_hash(user['password_hash'], request.form['password']):
            session['user_id'] = user['user_id']
            session['role']    = user['role']
            return redirect(url_for('index'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- Donor Routes ---

@app.route('/donor_profile', methods=['GET','POST'])
def donor_profile():
    if session.get('role') != 'Donor':
        return redirect(url_for('login'))
    if request.method == 'POST':
        cursor.execute(
            "INSERT INTO Donors (user_id,blood_group,city,last_donation_date) "
            "VALUES (%s,%s,%s,%s)",
            (
                session['user_id'],
                request.form['blood_group'],
                request.form['city'],
                request.form['last_donation_date']
            )
        )
        db.commit()
        return redirect(url_for('index'))
    return render_template('donor_profile.html')
@app.route('/log_donation', methods=['GET','POST'])
def log_donation():
    if session.get('role') != 'Donor':
        return redirect(url_for('login'))
    # ensure donor_profile exists
    cursor.execute("SELECT donor_id FROM Donors WHERE user_id=%s", (session['user_id'],))
    donor = cursor.fetchone()
    if not donor:
        return redirect(url_for('donor_profile'))

    if request.method == 'POST':
        cursor.execute(
            "INSERT INTO Donations (donor_id,hospital_id,donation_date,units_donated) "
            "VALUES (%s,%s,%s,%s)",
            (
              donor['donor_id'],
              request.form['hospital_id'],
              request.form['donation_date'],
              request.form['units_donated']
            )
        )
        db.commit()
        return redirect(url_for('donation_history'))

    # For the form, fetch list of hospitals:
    cursor.execute("SELECT hospital_id, hospital_name FROM Hospitals")
    hospitals = cursor.fetchall()
    return render_template('log_donation.html', hospitals=hospitals)
from datetime import date

@app.route('/donate_request', methods=['POST'])
def donate_request():
    # Only donors can fulfill a request
    if session.get('role') != 'Donor':
        return redirect(url_for('login'))

    req_id = request.form['request_id']

    # 1) Optionally log the donation (uncomment if you want to record it):
    #   Fetch donor_id and request details
    cursor.execute(
        "SELECT donor_id FROM Donors WHERE user_id=%s",
        (session['user_id'],)
    )
    donor = cursor.fetchone()
    cursor.execute(
        "SELECT hospital_id, units_required FROM BloodRequests WHERE request_id=%s",
        (req_id,)
    )
    req = cursor.fetchone()
    if donor and req:
        cursor.execute(
            """
            INSERT INTO Donations
              (donor_id, hospital_id, donation_date, units_donated)
            VALUES (%s, %s, %s, %s)
            """,
            (donor['donor_id'], req['hospital_id'], date.today(), req['units_required'])
        )

    # 2) Update the request status to Fulfilled
    cursor.execute(
        "UPDATE BloodRequests SET status='Fulfilled' WHERE request_id=%s",
        (req_id,)
    )

    db.commit()
    # Back to the search page (you could redirect elsewhere)
    return redirect(url_for('search_requests'))
@app.route('/search_requests', methods=['GET','POST'])
def search_requests():
    # only donors can search requests
    if session.get('role') != 'Donor':
        return redirect(url_for('login'))

    results = []
    if request.method == 'POST':
        bg   = request.form['blood_group']
        city = request.form['city']
        cursor.execute(
            """
            SELECT 
              br.request_id,
              h.hospital_name,
              h.city,
              br.blood_group,
              br.units_required,
              br.request_date
            FROM BloodRequests br
            JOIN Hospitals h ON br.hospital_id = h.hospital_id
            WHERE br.blood_group = %s
              AND h.city       = %s
              AND br.status    = 'Pending'
            """,
            (bg, city)
        )
        results = cursor.fetchall()

    return render_template('search_requests.html', results=results)
@app.route('/search_donors', methods=['GET','POST'])
def search_donors():
    if session.get('role') != 'Donor':
        return redirect(url_for('login'))
    donors = []
    if request.method == 'POST':
        cursor.execute(
            "SELECT U.name, D.blood_group, D.city "
            "FROM Donors D JOIN Users U ON D.user_id=U.user_id "
            "WHERE D.blood_group=%s AND D.city=%s",
            (request.form['blood_group'], request.form['city'])
        )
        donors = cursor.fetchall()
    return render_template('search_donors.html', donors=donors)
# --- Hospital Profile (new) ---
@app.route('/hospital_profile', methods=['GET','POST'])
def hospital_profile():
    if session.get('role') != 'Hospital':
        return redirect(url_for('login'))
    
    # Check if they already have a profile
    cursor.execute(
        "SELECT * FROM Hospitals WHERE user_id=%s",
        (session['user_id'],)
    )
    existing = cursor.fetchone()
    
    if request.method == 'POST':
        if existing:
            # Update existing profile
            cursor.execute(
                "UPDATE Hospitals SET hospital_name=%s, city=%s, contact_number=%s "
                "WHERE user_id=%s",
                (
                    request.form['hospital_name'],
                    request.form['city'],
                    request.form['contact_number'],
                    session['user_id']
                )
            )
        else:
            # Create new profile
            cursor.execute(
                "INSERT INTO Hospitals (user_id,hospital_name,city,contact_number) "
                "VALUES (%s,%s,%s,%s)",
                (
                    session['user_id'],
                    request.form['hospital_name'],
                    request.form['city'],
                    request.form['contact_number']
                )
            )
        db.commit()
        return redirect(url_for('index'))  # Redirect to dashboard after saving

    # Pass existing data to template for pre-filling the form
    return render_template('hospital_profile.html', hospital=existing)
@app.route('/donation_history')
def donation_history():
    if session.get('role') != 'Donor':
        return redirect(url_for('login'))
    cursor.execute(
        "SELECT Do.donation_date, Do.units_donated, H.hospital_name "
        "FROM Donations Do "
        "JOIN Donors D ON Do.donor_id=D.donor_id "
        "JOIN Hospitals H ON Do.hospital_id=H.hospital_id "
        "WHERE D.user_id=%s",
        (session['user_id'],)
    )
    records = cursor.fetchall()
    return render_template('donation_history.html', records=records)

# --- Hospital Routes ---

@app.route('/create_request', methods=['GET','POST'])
def create_request():
    if session.get('role') != 'Hospital':
        return redirect(url_for('login'))
    if request.method == 'POST':
        today = date.today()
        cursor.execute(
            "INSERT INTO BloodRequests (hospital_id,blood_group,units_required,request_date) "
            "VALUES ((SELECT hospital_id FROM Hospitals WHERE user_id=%s),%s,%s,%s)",
            (
                session['user_id'],
                request.form['blood_group'],
                request.form['units_required'],
                today
            )
        )
        db.commit()
        return redirect(url_for('view_requests'))
    return render_template('create_request.html')

@app.route('/view_requests', methods=['GET','POST'])
def view_requests():
    if session.get('role') != 'Hospital':
        return redirect(url_for('login'))
    # If the hospital is updating status
    if request.method == 'POST':
        cursor.execute(
            "UPDATE BloodRequests "
            "SET status=%s "
            "WHERE request_id=%s "
            "  AND hospital_id=(SELECT hospital_id FROM Hospitals WHERE user_id=%s)",
            (
                request.form['status'],
                request.form['request_id'],
                session['user_id']
            )
        )
        db.commit()
    # Fetch current requests
    cursor.execute(
        "SELECT * FROM BloodRequests "
        "WHERE hospital_id=(SELECT hospital_id FROM Hospitals WHERE user_id=%s)",
        (session['user_id'],)
    )
    requests = cursor.fetchall()
    return render_template('view_requests.html', requests=requests)

# --- Admin Routes ---

@app.route('/admin_requests', methods=['GET','POST'])
def admin_requests():
    if session.get('role') != 'Admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        cursor.execute(
            "UPDATE BloodRequests SET status=%s WHERE request_id=%s",
            (request.form['status'], request.form['request_id'])
        )
        db.commit()
    cursor.execute(
        "SELECT br.*, h.hospital_name "
        "FROM BloodRequests br "
        "JOIN Hospitals h ON br.hospital_id=h.hospital_id"
    )
    requests = cursor.fetchall()
    return render_template('admin_requests.html', requests=requests)

@app.route('/reports')
def reports():
    if session.get('role') != 'Admin':
        return redirect(url_for('login'))
    cursor.execute(
        "SELECT blood_group, COUNT(*) AS pending_count "
        "FROM BloodRequests WHERE status='Pending' "
        "GROUP BY blood_group"
    )
    report_data = cursor.fetchall()
    return render_template('reports.html', report=report_data)

@app.route('/ping')
def ping():
    return 'pong'

if __name__ == '__main__':
    app.run(debug=True)