import psycopg2
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['DATABASE_URL'] = 'postgresql://dtmon:dtmonpass@localhost:5432/dtmon'
app.secret_key = "your_super_secret_key" # Add a secret key.

# Register the teardown function
app.teardown_appcontext(db.close_db)
# Register the initdb command
app.cli.command('initdb')(db.init_db)

# Initialize Flask-Migrate
migrate = Migrate(app, db) # db is your SQLAlchemy instance

@app.route('/')
def index():
    """
    Displays a simple login page for DTMon.
    """
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """
    Handles the login form submission.
    """
    username = request.form.get('username')
    password = request.form.get('password')
    error = None

    user = db.get_user(username) # Use the get_user function from db.py

    if user is None:
        error = 'Incorrect username.'
    elif not check_password_hash(user['password_hash'], password):
        error = 'Incorrect password.'

    if error:
        flash(error, 'error') # Use flash for error message
        return render_template('index.html')  # Stay on the login page
    else:
        session['user_id'] = user['user_id']
        session['username'] = user['username'] # Store username in session.
        session['user_role'] = user['role']
        return redirect(url_for('dashboard')) # Redirect to dashboard

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return render_template('dashboard.html', username=session['username'], role=session['user_role'])
    else:
        return redirect(url_for('index'))
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
