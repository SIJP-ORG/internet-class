import os
from flask import Flask

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
)

# load the instance config, if it exists, when not testing
app.config.from_pyfile('config.py', silent=True)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

@app.route('/hello')
def hello():
    return 'Hello, World 2!'


# For debugging purpose.
# Run as python __init__.py
if __name__ == "__main__":
    app.run(host='0.0.0.0')
