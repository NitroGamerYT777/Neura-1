import os
from flask import Flask, redirect, url_for

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.urandom(24), # More secure secret key
        DATABASE=os.path.join(app.instance_path, 'database.sqlite'),
    )

    @app.route('/')
    def home():
        # Redirect to create a new chat, which requires login
        return redirect(url_for('chat.create_chat'))

    from . import db, auth, chat
    db.init_app(app)

    app.register_blueprint(auth.auth)
    app.register_blueprint(chat.chat)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app