import os
import sqlite3
import time
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash

app = Flask(__name__)



@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You are logged in')
            return redirect(url_for('/'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You are logged out')
    return redirect(url_for('/home'))


@app.route('/viewbill')
def viewbill():
    db = get_db()
    cur = db.execute('SELECT * FROM CHARGE')
    charges = cur.fetchall()
    return render_template('viewbill.html', charges=charges)


@app.route('/pastpayments')
def pastpayments():
    db = get_db()
    cur = db.execute('SELECT * FROM PAYMENT')
    payments = cur.fetchall()
    return render_template('pastpayments.html', payments=payments)


@app.route('/payment')
def payment():
    return render_template('payment.html')

@app.route('/registration2', methods=['POST'])
def reply():
    students=request.form['student']
    return render_template('registration2.html', student=students)



@app.route('/register')
def register():
    db = get_db()
    cur = db.execute('SELECT * FROM STUDENT')
    students = cur.fetchall()
    return render_template('register.html', selected='register', students=students)


@app.route('/add', methods=['GET', 'POST'])
def add():
    id = request.form['id']
    fname = request.form['fname']
    lname = request.form['lname']
    address = request.form['address']
    phone = request.form['phone']
    email = request.form['email']

    db = get_db();
    db.execute('INSERT INTO STUDENT VALUES (?, ?, ?, ? ,?, ?)', [id, fname, lname, address, phone,email])
    db.commit()
    return redirect(url_for('register'))


@app.route('/home')
def index():
    db = get_db()
    cur = db.execute('SELECT * FROM STUDENT')
    students = cur.fetchall()
    cur = db.execute('SELECT * FROM CHARGE')
    charges = cur.fetchall()
    cur = db.execute('SELECT * FROM AID')
    aids = cur.fetchall()
    cur = db.execute('SELECT * FROM PAYMENT')
    payments = cur.fetchall()
    return render_template('index.html', students=students, charges=charges, aids=aids, payments=payments)


@app.route('/userprofile')
def users():
    db = get_db()
    cur = db.execute('SELECT * FROM STUDENT')
    students = cur.fetchall()
    return render_template('userprofile.html', students=students)


# @app.route('/viewbill')
# def vbill():
#   return render_template('viewbill.html')

@app.route('/paybill')
def paybill():
    db = get_db()
    cur = db.execute('SELECT * FROM CHARGE')
    charges = cur.fetchall()
    cur = db.execute('SELECT * FROM STUDENT')
    students = cur.fetchall()
    return render_template('paybill.html', charges=charges, students=students)


# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def init_db():
    db = get_db()
    with app.open_resource('tables.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print 'Initialized the database.'


if __name__ == '__main__':
    app.run()
