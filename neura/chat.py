import functools
from flask import (
    Blueprint, flash, g, get_flashed_messages, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug import exceptions

from uuid import uuid4
from neura.db import get_db
from .auth import login_required
import webbrowser
from googlesearch import search
import os
import glob
import subprocess

chat = Blueprint('chat', __name__, url_prefix='/chat')

def get_ai_response(user_message = None):
    import requests
    url = "https://gemini-6y6e.onrender.com/api/chat"  # Your API endpoint
    if not user_message:
        payload = {"newChat": True}
    else:
        payload = {"message": user_message}  

    try:
        response = requests.post(url, json=payload, timeout=10)  # Send request
        response.raise_for_status()  # Raise error for bad status codes (4xx, 5xx)
        
        data = response.json()  # Convert response to JSON
        return data.get("response")  # Extract AI's response

    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

@login_required
@chat.route('/new') # it is like creating room
def create_chat():
    db = get_db()
    id = f'{uuid4()}'
    get_ai_response()
    db.execute("INSERT INTO chat (id, summary_title, owner) VALUES (?, ?, ?)", (id, "Empty chat", session.get('user_id')))
    db.commit()    
    return redirect(url_for('chat.chat_view', chat_id=id))
@chat.route('/preview')
def preview():
    None
from flask import jsonify

@login_required
@chat.route('/<chat_id>', methods=('GET', 'POST'))
def chat_view(chat_id):
    print(get_unique_date())
    db = get_db()

    check_url = db.execute("SELECT EXISTS(SELECT 1 FROM chat WHERE id = ?)", (chat_id,)).fetchone()[0]

    if not check_url:
        raise OSError()

    owner_id = db.execute('SELECT owner FROM chat WHERE id = ?', (chat_id,)).fetchone()

    if not owner_id or owner_id['owner'] != session.get('user_id'):
        return exceptions.Forbidden()

    if request.method == 'POST':
        user_query = request.form['query']
        
        # Insert the user's message into the database
        db.execute('INSERT INTO query (msg, owner, chat, is_user) VALUES (?, ?, ?, ?)',
                   (user_query ,session.get('user_id'), chat_id, True))
        # @chat.route('/search', methods=['POST'])
        def find_website_url(site_name, num_results=1):
            query = f"{site_name} official site"
            results = search(query, num_results=num_results)
            return list(results)

        def search_google(user_query ):
            query = user_query.replace("/search ", "").strip()
            url = find_website_url(query)
            webbrowser.open_new(url)
        def find_and_open_file(user_query, search_dirs=["C:/", "D:/", "E:/"]):
            file_name = user_query.replace("/open ", "").strip()
            for directory in search_dirs:
                for root, _, files in os.walk(directory):
                    if file_name in files:
                        file_path = os.path.join(root, file_name)
                        subprocess.run(["start", "", file_path], shell=True)
                        return file_path
            return None
        def register(user_query):
            None
        def my_dict():
            None
        


        # Get the AI response
        ai_response = get_ai_response(user_query)
        summary_title = get_ai_response('Summary this query, do not forget your response should be less than 20')
        db.execute('INSERT INTO query (msg, owner, chat, is_user) VALUES (?, ?, ?, ?)',
                   (ai_response, session.get('user_id'), chat_id, False))
        db.execute("UPDATE chat SET summary_title = ? WHERE id = ?", (summary_title, chat_id, )).fetchone()

        db.commit()

        # Fetch the updated list of queries/messages for this chat room
        queries = db.execute('SELECT * FROM query WHERE chat = ?', (chat_id,)).fetchall()

        # Return a JSON response to the client with both user and AI queries
        return jsonify({
            'success': True,
            'message': user_query,
            'ai_message': ai_response,
            'queries': [dict(q) for q in queries]  # Convert rows to a dictionary to send as JSON
        })

    # If it's a GET request, just render the page with the queries
    queries = db.execute('SELECT * FROM query WHERE chat = ?', (chat_id,)).fetchall()
    import markdown
    return render_template('chat/chat_home.html', chat_id=chat_id, queries=queries, history=get_my_history, dates=get_unique_date())

def get_my_history():
    db = get_db()
    return db.execute("SELECT * FROM chat WHERE owner = ? ORDER BY created_at DESC", (session.get('user_id'), ))

@login_required
@chat.route('/<chat_id>/delete', methods=['POST'])
def delete_chat(chat_id):
    db = get_db()
    check_url = db.execute("SELECT EXISTS(SELECT 1 FROM chat WHERE id = ?)", (chat_id,)).fetchone()[0]
    
    if not check_url:
        return jsonify({'success': False, 'message': 'Chat not found'}), 404
    
    # Check if the logged-in user is the owner
    chat_owner = db.execute('SELECT owner FROM chat WHERE id = ?', (chat_id,)).fetchone()
    if not chat_owner or chat_owner['owner'] != session.get('user_id'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    # Proceed to delete the chat
    db.execute('DELETE FROM chat WHERE id = ?', (chat_id,))
    db.commit()

    return jsonify({'success': True, 'message': 'Chat has been deleted'})



def get_unique_date():
    db = get_db()
    dates = db.execute('SELECT DISTINCT created_at FROM chat').fetchall()

    return dates