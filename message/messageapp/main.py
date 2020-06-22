import os
from flask import Flask, redirect, url_for

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    SEND_FILE_MAX_AGE_DEFAULT=0,
)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass


# Root
@app.route('/')
def root():
    return 'installed'

# Test function
@app.route('/hello')
def hello():
    return 'Hello. I am alive.'

# For debugging server. From the parent folder,
# python -m messageapp.main
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
