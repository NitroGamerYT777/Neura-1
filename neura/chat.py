import functools
from flask import (
    Blueprint, flash, g, get_flashed_messages, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug import exceptions

from uuid import uuid4
from neura.db import get_db
from .auth import login_required


chat = Blueprint('chat', __name__, url_prefix='/chat')

def get_ai_response(user_message = None):
    # Note: The external API at https://gemini-6y6e.onrender.com/api/chat seems to be down.
    # This function is correct, but will likely fail until the external service is restored.
    import requests
    url = "https://gemini-6y6e.onrender.com/api/chat"  # Your API endpoint
    if not user_message:
        payload = {"newChat": True}
    else:
        payload = {"message": user_message}  

    try:
        # Using verify=False is a temporary workaround for potential SSL issues, not recommended for production.
        response = requests.post(url, json=payload, timeout=30, verify=False)
        response.raise_for_status()
        data = response.json()
        return data.get("response")

    except requests.exceptions.RequestException as e:
        import traceback
        print("--- API Request Error ---")
        traceback.print_exc()
        print("-----------------------")
        return "Sorry, I'm having trouble connecting to the AI service right now. Please try again later."

@login_required
@chat.route('/new')
def create_chat():
    db = get_db()
    id = f'{uuid4()}'
    db.execute("INSERT INTO chat (id, summary_title, owner) VALUES (?, ?, ?)",
               (id, "Empty chat", session.get('user_id')))
    db.commit()    
    return redirect(url_for('chat.chat_view', chat_id=id))

@login_required
@chat.route('/<chat_id>', methods=('GET', 'POST'))
def chat_view(chat_id):
    db = get_db()

    # Verify chat exists and user is the owner
    chat_info = db.execute("SELECT * FROM chat WHERE id = ? AND owner = ?",
                           (chat_id, session.get('user_id'))).fetchone()

    if not chat_info:
        return exceptions.NotFound()

    if request.method == 'POST':
        user_query = request.form.get('query')
        if not user_query:
            return jsonify({'success': False, 'message': 'Empty query'}), 400

        # Insert the user's message into the database
        db.execute('INSERT INTO query (msg, owner, chat, is_user) VALUES (?, ?, ?, ?)',
                   (user_query, session.get('user_id'), chat_id, True))
        db.commit()

        # Get the AI response
        ai_response = get_ai_response(user_query)
        db.execute('INSERT INTO query (msg, owner, chat, is_user) VALUES (?, ?, ?, ?)',
                   (ai_response, session.get('user_id'), chat_id, False))

        # Check if chat summary needs to be updated
        if chat_info['summary_title'] == 'Empty chat':
            summary_prompt = f"Summarize the following in 5 words or less: '{user_query}'"
            summary_title = get_ai_response(summary_prompt)
            if summary_title:
                db.execute("UPDATE chat SET summary_title = ? WHERE id = ?", (summary_title, chat_id))

        db.commit()

        # Fetch the updated list of queries/messages for this chat room
        queries = db.execute('SELECT * FROM query WHERE chat = ? ORDER BY id', (chat_id,)).fetchall()

        # Return a JSON response
        return jsonify({
            'success': True,
            'queries': [dict(q) for q in queries]
        })

    # For a GET request, render the page with chat history
    queries = db.execute('SELECT * FROM query WHERE chat = ? ORDER BY id', (chat_id,)).fetchall()
    history = get_my_history()
    dates = get_unique_date()

    return render_template('chat/chat_home.html', chat_id=chat_id, queries=queries, history=history, dates=dates)

def get_my_history():
    db = get_db()
    return db.execute("SELECT * FROM chat WHERE owner = ? ORDER BY created_at DESC", (session.get('user_id'), )).fetchall()

@login_required
@chat.route('/<chat_id>/delete', methods=['POST'])
def delete_chat(chat_id):
    db = get_db()
    
    # Check if the logged-in user is the owner
    chat_owner = db.execute('SELECT owner FROM chat WHERE id = ?', (chat_id,)).fetchone()
    if not chat_owner or chat_owner['owner'] != session.get('user_id'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    # Proceed to delete the chat
    db.execute('DELETE FROM chat WHERE id = ?', (chat_id,))
    db.execute('DELETE FROM query WHERE chat = ?', (chat_id,)) # Also delete associated queries
    db.commit()

    return jsonify({'success': True, 'message': 'Chat has been deleted'})

def get_unique_date():
    db = get_db()
    # Fetch distinct dates only for the current user's chats
    dates = db.execute("SELECT DISTINCT DATE(created_at) as chat_date FROM chat WHERE owner = ? ORDER BY chat_date DESC",
                       (session.get('user_id'),)).fetchall()
    return dates