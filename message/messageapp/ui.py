from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
import requests
from . import msg
from flask_table import Table, Col
import dns.resolver
import re

def root():
    param = {
        'desthost': '',
        'destip': '',
        'message': '',
        'image': url_for('static', filename='start.gif'),
    }

    return render_template('main.html', param=param)

def send():
    destination = request.form['destination']
    message = request.form['message']
    error = None
    destip = ''

    # sanitize host name
    destination = re.sub(r'^(http://)?(https://)?([^/]+).*$', r'\3', destination.strip())

    if not destination:
        error = "ホストネームがただしくありません"
    elif not message:
        error = "メッセージをいれてください"

    if not error:
        try:
            withoutport = re.sub(r'([^:]*):.*', r'\1', destination)
            answers = dns.resolver.query(withoutport, 'A')
            destip = answers[0].to_text()
        except dns.resolver.NXDOMAIN:
            error = "Host name {0} is not found. (ホストネーム {0} はみつかりません)".format(withoutport)
        except Exception as e:
            error = "Error: {0}".format(e)

    if not error:
        data = {
            'msg': message,
        }
        res = requests.post('http://{0}/msg/sendnew'.format(destination), json=data)
        if res.status_code != 200:
            error = "The message was not sent correctly. (メッセージはただしくおくられませんでした) " + res.reason

    session['desthost'] = destination
    session['destip'] = destip
    session['message'] = message

    if error:
        session['error'] = error
        return redirect(url_for('error'))
    else:
        return redirect(url_for('success'))

def success():
    param = {
        'input_disabled': 'disabled',
        'show_result': True,
        'desthost': session['desthost'],
        'destip': session['destip'],
        'message': session['message'],
        'image': url_for('static', filename='send.gif'),
    }

    return render_template('main.html', param=param)

def error():
    '''UI for any failure.'''
    param = {
        'input_disabled': 'disabled',
        'show_error': True,
        'desthost': session['desthost'],
        'destip': session['destip'],
        'message': session['message'],
        'error': session['error'],
        'image': url_for('static', filename='start.gif'),
    }

    return render_template('main.html', param=param)

def table():
    '''Show received messages as a table'''
    data = msg.get_messages()
    table = MessageTable(data)
    return render_template('messages.html', table=table)

class MessageTable(Table):
    ip = Col('IP address (IPアドレス)')
    hostname = Col('Hostname (ホストネーム)')
    body = Col('Message (メッセージ)')
