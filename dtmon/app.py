from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    """
    Displays a simple login page for DTMon.
    """
    # In a real application, you would get the username/password
    # from a form submitted by the user.  This is just a basic example.
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """
    Handles the login form submission (very basic example).
    """
    username = request.form.get('username')
    password = request.form.get('password')

    # In a real application, you would validate the username and password
    # against a database or other secure storage.  This is NOT secure.
    if username == 'admin' and password == 'password':
        return f"<h1>Login successful, {username}!</h1>"  #  Don't put HTML in the Python, but ok for now.
    else:
        return "<h1 style='color:red'>Login failed. Invalid credentials.</h1>" #  Don't put HTML in the Python, but ok for now.

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
