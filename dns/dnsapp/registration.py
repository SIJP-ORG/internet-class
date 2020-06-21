import functools
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)

bp = Blueprint('registration', __name__, url_prefix='/registration')

@bp.route('/', methods=('GET', 'POST'))
def root():
    if request.method == 'GET':
        return render_template('registration/view.html')


