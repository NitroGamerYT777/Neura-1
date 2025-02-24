import functools
from flask import (
    Blueprint, flash, g, get_flashed_messages, redirect, render_template, request, session, url_for, make_response
)
from werkzeug.security import check_password_hash, generate_password_hash
from neura.db import get_db

auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/register', methods=('GET', 'POST'))
def register():
    
    if g.user is not None:
        return redirect(url_for('home'))

    flash_messages = get_flashed_messages(with_categories=True)

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        db = get_db()
        error = None

        if not (username and password and len(password) > 8 and len(username) < 25):
            error = 'You did something wrong, check it!'

        user = db.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()
        if error is None:
            if user is None:
                    db.execute(
                        "INSERT INTO user (username, password) VALUES (?, ?)",(username, generate_password_hash(password)),)
                    db.commit()
                    session["user_id"] = db.execute("SELECT id FROM user WHERE username = ?", (username,)).fetchone()["id"]
                    flash("Account created successfully!", "success")
                    
                    return redirect(url_for("home"))
            else:
                if check_password_hash(user["password"], password):
                    session.clear()
                    session["user_id"] = user["id"]
                    flash("Logged in successfully!", "success")
                    return redirect(url_for("home"))           
        else:
            flash(error, "danger")
    
    return render_template('auth/register.html', flash_messages=flash_messages)


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
    flash("You have been logged out.", "danger")
    return redirect(url_for('home'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("You must be logged in to access this page.", "danger")
            return redirect(url_for('auth.register'))

        return view(**kwargs)

    return wrapped_view

@auth.before_request
def redirect_logged_out_users():
    if g.user is None and request.endpoint != 'auth.register' and request.endpoint != 'auth.login':
        return redirect(url_for('auth.register')) 


# @auth.before_request
# def prevent_cache():
#     """Prevent browser from caching authenticated pages."""
#     if g.user is None:
#         # Only apply for pages that need authentication
#         response = make_response()
#         response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
#         response.headers['Pragma'] = 'no-cache'
#         response.headers['Expires'] = '0'
#         return response