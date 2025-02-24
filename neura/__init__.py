import os
from flask import Flask, render_template, g, session, redirect, url_for
from .db import get_db
from .auth import login_required
from .chat import get_my_history, chat_view


def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='aoishdosiaoashdasoi',
        DATABASE=os.path.join(app.instance_path, 'database.sqlite'),
    )
    


    @app.route('/')
    @login_required
    def home():
        # g.random_room_id = str(f'{uuid4()}')
        return redirect(url_for('chat.create_chat'))


        

    from . import db, auth,chat
    db.init_app(app)

    app.register_blueprint(auth.auth)
    app.register_blueprint(chat.chat)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app