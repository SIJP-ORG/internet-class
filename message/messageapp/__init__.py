import os
from flask import Flask, redirect, url_for, request

from . import db, messageapi, custom_json_encoder, ui
import urllib.request

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='O2B6RfJhphOkjWGthbdqsQ',
        DATABASE=os.path.join(app.instance_path, 'messageapp.sqlite'),
        SEND_FILE_MAX_AGE_DEFAULT=0,
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register custom json encode
    app.json_encoder = custom_json_encoder.CustomJSONEncoder

    # intiialize database module
    db.init_app(app)

    # UI
    app.add_url_rule('/', view_func=ui.root, methods=['GET'])
    app.add_url_rule('/send', view_func=ui.send, methods=['POST'])
    app.add_url_rule('/result', view_func=ui.success, methods=['GET'])
    app.add_url_rule('/error', view_func=ui.error, methods=['GET'])
    app.add_url_rule('/table', view_func=ui.table, methods=['GET'])
    # util UI
    app.add_url_rule('/init-db', view_func=db.init_db, methods=['GET'])

    # API
    app.add_url_rule('/messages/new', view_func=messageapi.send_new, methods=['POST'])
    # dev only
    app.add_url_rule('/messages', view_func=messageapi.get_messages, methods=['GET'])

    # Test function
    @app.route('/hello')
    def hello():
        return 'Hello. I am alive.'

    return app

