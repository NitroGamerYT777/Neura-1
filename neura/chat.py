import functools
from flask import (
    Blueprint, flash, g, get_flashed_messages, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug import exceptions

from uuid import uuid4
from neura.db import get_db

chat = Blueprint('chat', __name__, url_prefix='/chat')

def get_ai_response(user_message):
    import requests
    url = "https://gemini-6y6e.onrender.com/api/chat"  # Your API endpoint
    payload = {"message": user_message}  # Data to send

    try:
        response = requests.post(url, json=payload, timeout=10)  # Send request
        response.raise_for_status()  # Raise error for bad status codes (4xx, 5xx)
        
        data = response.json()  # Convert response to JSON
        return data.get("response")  # Extract AI's response

    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None


@chat.route('/new') # it is like creating room
def create_chat():
    db = get_db()
    id = f'{uuid4()}'
    db.execute("INSERT INTO chat (id, summary_title, owner) VALUES (?, ?, ?)", (id, "Empty chat", session.get('user_id')))
    db.commit()
    
    return redirect(url_for('chat.chat_view', chat_id=id))
from flask import jsonify

@chat.route('/<chat_id>', methods=('GET', 'POST'))
def chat_view(chat_id):
    db = get_db()

    check_url = db.execute("SELECT EXISTS(SELECT 1 FROM chat WHERE id = ?)", (chat_id,)).fetchone()[0]

    if not check_url:
        raise OSError()

    owner_id = db.execute('SELECT owner FROM chat WHERE id = ?', (chat_id,)).fetchone()

    if not owner_id or owner_id['owner'] != session.get('user_id'):
        return exceptions.Forbidden()

    if request.method == 'POST':
        user_query = request.form['query']

        db.execute('INSERT INTO query (msg, owner, chat, is_user) VALUES (?, ?, ?, ?)',
                   (user_query, session.get('user_id'), chat_id, True))
        db.execute('INSERT INTO query (msg, owner, chat, is_user) VALUES (?, ?, ?, ?)',
                   (get_ai_response(user_query), session.get('user_id'), chat_id, False))
        db.commit()


    queries = db.execute('SELECT * FROM query WHERE chat = ?', (chat_id,)).fetchall()

    return render_template('chat/chat_home.html', chat_id=chat_id, queries=queries)

def get_my_history():
    db = get_db()
    return db.execute("SELECT * FROM chat WHERE owner = ?", (session.get('user_id'), ))


@chat.route('/<chat_id>/delete', methods=['POST', 'GET'])
def delete_chat(chat_id):
    db = get_db()
    check_url = db.execute("SELECT EXISTS(SELECT 1 FROM chat WHERE id = ?)", (chat_id, )).fetchone()[0]
    if not check_url:
        return exceptions.NotFound()
    if not db.execute('SELECT * FROM chat WHERE id = ?', (chat_id, )).fetchone()['owner'] == session.get('user_id'):
        return exceptions.Forbidden()
    
    db.execute('DELETE FROM chat WHERE id = ?', (chat_id, ))
    db.commit()
    flash('Chat has been deleted', 'success')
    return redirect(url_for('home'))
