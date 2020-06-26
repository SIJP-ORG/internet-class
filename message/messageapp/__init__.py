import os
from flask import Flask, redirect, url_for

from . import db, msg, custom_json_encoder, ui


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
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

    # define routes
    app.add_url_rule('/', view_func=ui.root, methods=['GET', 'POST'])
    app.add_url_rule('/table', view_func=ui.table, methods=['GET'])
    app.add_url_rule('/msg/sendnew', view_func=msg.sendnew, methods=['POST'])
    app.add_url_rule('/msg', view_func=msg.getall, methods=['GET'])   
    app.add_url_rule('/init-db', view_func=db.init_db, methods=['GET'])

    # Test function
    @app.route('/hello')
    def hello():
        return 'Hello. I am alive.'

    return app

