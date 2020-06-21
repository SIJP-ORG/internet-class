import os
from flask import Flask, redirect, url_for

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    SEND_FILE_MAX_AGE_DEFAULT=0,
)

# load the instance config, if it exists
app.config.from_pyfile('config.py', silent=True)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# Add registration blueprint
from . import registration
app.register_blueprint(registration.bp)

# Root
@app.route('/')
def root():
    return redirect(url_for('registration.root'))

# Test function
@app.route('/hello')
def hello():
    return 'Hello. I am alive.'

# For debugging server. Run 'python __init__.py'
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
