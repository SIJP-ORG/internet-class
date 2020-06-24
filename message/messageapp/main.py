import os
from flask import Flask, redirect, url_for
from flask.json import JSONEncoder
from datetime import date

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

# database init
from . import db
db.init_app(app)


# Import other files
from . import msg
app.add_url_rule('/msg/sendnew', view_func=msg.sendnew, methods=['POST'])
app.add_url_rule('/msg', view_func=msg.getall, methods=['GET'])

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, date):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

app.json_encoder = CustomJSONEncoder

# Root
@app.route('/')
def root():
    return 'installed'

# Test function
@app.route('/hello')
def hello():
    return 'Hello. I am alive.'

# Database init
@app.route('/init-db')
def init_db():
    """Clear the existing data and create new tables."""
    db.init_db()
    return 'Initialized the database.'

# For debugging server. From the parent folder,
# python -m messageapp.main
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

