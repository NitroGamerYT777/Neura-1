import functools
from flask import (
    Blueprint, flash, g, get_flashed_messages, redirect, render_template, request, session, url_for, make_response
)
from werkzeug.security import check_password_hash, generate_password_hash
from neura.db import get_db

auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/register', methods=('GET', 'POST'))
def register():
    if g.user:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif len(password) < 8:
            error = 'Password must be at least 8 characters long.'
        elif len(username) > 25:
            error = 'Username must be less than 25 characters long.'

        if error is None:
            user = db.execute("SELECT id FROM user WHERE username = ?", (username,)).fetchone()
            if user is not None:
                error = f"User {username} is already registered."
            else:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
                # Log the user in automatically after registration
                user = db.execute("SELECT id FROM user WHERE username = ?", (username,)).fetchone()
                session.clear()
                session['user_id'] = user['id']
                flash("Account created successfully!", "success")
                return redirect(url_for("home"))

        flash(error, "danger")

    return render_template('auth/register.html')

@auth.route('/login', methods=('GET', 'POST'))
def login():
    if g.user:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            flash("Logged in successfully!", "success")
            return redirect(url_for('home'))

        flash(error, 'danger')

    return render_template('auth/login.html')

@auth.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@auth.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("You must be logged in to access this page.", "danger")
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view