import functools
import time
import boto3
from flask import redirect, render_template, request, session, url_for

DOMAIN = 'ninja.fish'
ZONEID = 'Z04921881CATTNOQUCZ18'

def show_main():
    '''
    Show main UI initialized.
    '''
    session.clear()

    param = {
        'domain': DOMAIN,
    }
    return render_template('registration/view.html', param=param)

def show_error():
    '''
    Show main UI with error message.
    '''
    param = {
        'ipaddress': session['ipaddress'],
        'hostname': session['hostname'],
        'domain': DOMAIN,
        'error': session['error'],
    }
    return render_template('registration/view.html', param=param)

def show_success():
    '''
    Show success UI which includes the link to 
    '''
    info = {
        'ipaddress': session['ipaddress'],
        'fullname': session['fullname']
    }
    return render_template('registration/success.html', info=info)


def register():
    '''
    Handle DNS registration request (POST).
    '''
    ipaddress = request.form['ipaddress']
    hostname = request.form['hostname']
    fullname = '{0}.{1}'.format(hostname, DOMAIN)
    error = None

    if not ipaddress:
        error = "Enter IP address. (IPアドレスをいれてください)"
    elif not hostname:
        error = "Enter a name. (なまえをいれてください)"

    if error is None:
        error = add_dns_resource(ipaddress, fullname)
        pass
    
    if error:
        session['error'] = error
        session['ipaddress'] = ipaddress
        session['hostname'] = hostname
        return redirect(url_for('show_error'))
    else:
        session['ipaddress'] = ipaddress
        session['fullname'] = fullname
        return redirect(url_for('show_success'))


def add_dns_resource(ipaddress, fullname):
    '''
    Add a new record to DNS.
    Returning None for success. Error string for failure.
    '''
    try:
        r53 = boto3.client('route53')

        createResponse = r53.change_resource_record_sets(
            HostedZoneId = ZONEID,
            ChangeBatch = {
                'Changes': [{
                    'Action': 'CREATE',
                    'ResourceRecordSet': {
                        'Type': 'A',
                        'TTL': 60,
                        'Name': fullname,
                        'ResourceRecords': [{'Value': ipaddress}]
                    }
                }]
            })
        changeId = createResponse['ChangeInfo']['Id']

        # Max wait = 120 sec (5 * 24)
        for waitcount in range (0, 24):
            time.sleep(5)
            changeResponse = r53.get_change(Id = changeId)
            if changeResponse['ChangeInfo']['Status'] == 'INSYNC':
                return None

        return 'Timeout. Please retry. (じかんぎれです。やりなおしてください)'

    except Exception as e:
        # TODO: convert user firendly message (e.g. already used)
        return 'Error {0}'.format(str(e))

