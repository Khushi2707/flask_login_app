from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = 'secret'

# Database connection function to Cloud SQL
def get_db_connection():
    # Get the Cloud SQL instance connection name from environment variables
    cloud_sql_connection_name = os.getenv('DB_HOST')  # Set in app.yaml
    user = os.getenv('DB_USER')  # Your database username
    password = os.getenv('DB_PASSWORD')  # Your database password
    database = os.getenv('DB_NAME')  # Your database name

    # Connect to Cloud SQL
    conn = mysql.connector.connect(
        host=f'/cloudsql/{cloud_sql_connection_name}',
        user=user,
        password=password,
        database=database
    )
    return conn

# Initialize database function to create table if not exists
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()  # Initialize DB when the app starts

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (user, pwd))
        result = cursor.fetchone()
        conn.close()
        if result:
            session['username'] = user
            return redirect(url_for('profile'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (user, pwd))
            conn.commit()
        except mysql.connector.IntegrityError:
            return "Username already exists"
        conn.close()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/profile')
def profile():
    if 'username' in session:
        return render_template('profile.html', username=session['username'])
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
