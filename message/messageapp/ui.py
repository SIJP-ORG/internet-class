from flask import render_template, request, session, redirect, url_for
import requests
import urllib.request
import dns.resolver
import re
import random
from . import messageapi


def root():
    '''
    Main UI to accept the request.
    '''
    (hostname, publicip) = get_self()
    param = {
        'source_hostname': hostname,
        'source_ipaddress': publicip,
        'target_hostname': '',
        'target_ipaddress': '',
        'message': '',
        'image': url_for('static', filename='start.gif'),
    }

    return render_template('main.html', param=param)


def send():
    '''
    Main send logic at the time of POST.
    '''
    hostname = request.host
    destination = request.form['destination']
    message = request.form['message']
    error = None
    target_ipaddress = ''

    # sanitize host name
    destination = re.sub(r'^(http://)?(https://)?([^/]+).*$', r'\3', destination.strip())

    if not destination:
        error = "ホストネームをいれてください"
    elif not message:
        error = "メッセージをいれてください"

    if not error:
        try:
            withoutport = re.sub(r'([^:]*):.*', r'\1', destination)
            answers = dns.resolver.query(withoutport, 'A')
            target_ipaddress = answers[0].to_text()
        except dns.resolver.NXDOMAIN:
            error = "Host name {0} is not found. (ホストネーム {0} はみつかりません)".format(withoutport)
        except Exception as e:
            error = "Error: {0}".format(e)

    if not error:
        data = {
            'sender': hostname,
            'body': message,
        }
        res = requests.post('http://{0}/messages/new'.format(destination), json=data)
        if res.status_code != 200:
            error = "The message was not sent correctly. (メッセージはただしくおくられませんでした) " + res.reason

    session['target_hostname'] = destination
    session['target_ipaddress'] = target_ipaddress
    session['message'] = message

    if error:
        session['error'] = error
        return redirect(url_for('error'))
    else:
        return redirect(url_for('success'))


def success():
    '''
    Result UI at a success.
    '''
    (hostname, publicip) = get_self()
    param = {
        'input_disabled': 'disabled',
        'show_result': True,
        'source_hostname': hostname,
        'source_ipaddress': publicip,
        'target_hostname': session['target_hostname'],
        'target_ipaddress': session['target_ipaddress'],
        'message': session['message'],
        # Random parameter needs to be added, otherwise FF will not render it at the second load.
        'image': url_for('static', filename='send.gif') + '?x=' + str(random.randint(1,10000)),
    }

    return render_template('main.html', param=param)


def error():
    '''
    Result UI at a failure.
    '''
    (hostname, publicip) = get_self()
    param = {
        'input_disabled': 'disabled',
        'show_error': True,
        'source_hostname': hostname,
        'source_ipaddress': publicip,
        'target_hostname': session['target_hostname'],
        'target_ipaddress': session['target_ipaddress'],
        'message': session['message'],
        'error': session['error'],
        'image': url_for('static', filename='start.gif'),
    }

    return render_template('main.html', param=param)


def get_self():
    '''
    Extract hostname from 'request' and retrieve EC2 public IP address.
    '''
    hostname = request.host
    publicip = urllib.request.urlopen("http://169.254.169.254/latest/meta-data/public-ipv4").read().decode('ascii')
    return (hostname, publicip)

def table():
    '''
    Show received messages as a table
    '''
    data = messageapi.get_last100_messages()

    # Message for the first time access.
    if len(data) == 0:
        data.append({
            'ip': '',
            'hostname': '',
            'body': 'No messages. (メッセージはありません)'
        })

    return render_template('messages.html', data=data)
