import functools
import time
import boto3
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

DOMAIN = 'ninja.fish'
ZONEID = 'Z04921881CATTNOQUCZ18'

bp = Blueprint('registration', __name__, url_prefix='/registration')

@bp.route('/', methods=('GET', 'POST'))
def root():
    if request.method == 'GET':
        return render_template('registration/view.html')

    if request.method == 'POST':
        ipaddress = request.form['ipaddress']
        servername = request.form['servername']
        fullname = '{0}.{1}'.format(servername, DOMAIN)
        error = None

        if not ipaddress:
            error = 'You need to enter IP address. (IPアドレスをいれてください)'
        elif not servername:
            error = 'You need to enter a name. (なまえをいれてください)'
        
        if error is None:
            error = add_dns_resource(ipaddress, fullname)
            pass
        
        if error is None:
            info = {'ipaddress': ipaddress, 'fullname': fullname}
            return render_template('registration/success.html', info = info)
        
        flash(error)
        return render_template('registration/view.html')

def add_dns_resource(ipaddress, fullname):
    '''Add a new record to DNS. Returning None for success. Error string for failure.'''
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

        # TODO: max retry and error out
        while True:
            time.sleep(5)
            changeResponse = r53.get_change(Id = changeId)
            if changeResponse['ChangeInfo']['Status'] == 'INSYNC':
                break

        return None
    except Exception as e:
        # TODO: convert user firendly message (e.g. already used)
        return 'Error {0}'.format(str(e))

