from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
import requests
from . import msg
from flask_table import Table, Col

def root():
    if request.method == 'GET':
        return render_template('main.html')

    if request.method == 'POST':
        destination = request.form['destination']
        message = request.form['message']
        error = None

        # TODO -- shorter timeout
        res = requests.post(
            'http://{0}/msg/sendnew'.format(destination),
            json={'msg': message} )

        if res.status_code == 200:
            result_message = 'The message was sent successfully.'
        else:

            result_message = 'The message was not sent correctly. ' + res.reason
            flash(result_message)

        result = {'msg': result_message}
        return render_template('main.html', result = result)

class MessageTable(Table):
    sender = Col('Sender (おくったひと)')
    body = Col('Message (メッセージ)')

def table():
    data = msg.get_messages()
    table = MessageTable(data)
    return render_template('messages.html', table=table)
