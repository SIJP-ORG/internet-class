import os
from flask import Flask, redirect, url_for, request
from . import registration

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='O2B6RfJhphOkjWGthbdqsQ',
        SEND_FILE_MAX_AGE_DEFAULT=0,
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # UI
    app.add_url_rule('/', view_func=registration.show_main, methods=['GET'])
    app.add_url_rule('/error', view_func=registration.show_error, methods=['GET'])
    app.add_url_rule('/success', view_func=registration.show_success, methods=['GET'])
    app.add_url_rule('/register', view_func=registration.register, methods=['POST'])
    app.add_url_rule('/hosts', view_func=registration.get_hosts_table, methods=['GET'])

    # Test function
    @app.route('/hello')
    def hello():
        return 'Hello. I am alive.'

    return app
