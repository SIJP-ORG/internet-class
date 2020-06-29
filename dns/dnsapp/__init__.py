import os
from flask import Flask, redirect, url_for, request
from . import registration


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='O2B6RfJhphOkjWGthbdqsQ',
        SEND_FILE_MAX_AGE_DEFAULT=0,
    )

    # UI
    app.add_url_rule('/', view_func=registration.root, methods=['GET'])

    # Test function
    @app.route('/hello')
    def hello():
        return 'Hello. I am alive.'

    return app
