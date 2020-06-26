from flask.json import JSONEncoder
from datetime import date

class CustomJSONEncoder(JSONEncoder):
    '''Custom class to use ISO format in returning JSON response'''
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
