import os
from flask import Flask, render_template, g, session
from uuid import uuid4
from .auth import login_required
from .chat import get_my_history


def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=f'{uuid4()}',
        DATABASE=os.path.join(app.instance_path, 'database.sqlite'),
    )
    


    @app.route('/')
    @login_required
    def home():
        g.random_room_id = str(f'{uuid4()}')
        return render_template('home.html', history=get_my_history)

    from . import db, auth,chat
    db.init_app(app)

    app.register_blueprint(auth.auth)
    app.register_blueprint(chat.chat)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app