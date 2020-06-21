import functools
import boto3
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

domainname = 'ninja.fish'

bp = Blueprint('registration', __name__, url_prefix='/registration')

@bp.route('/', methods=('GET', 'POST'))
def root():
    if request.method == 'GET':
        return render_template('registration/view.html')

    if request.method == 'POST':
        ipaddress = request.form['ipaddress']
        servername = request.form['servername']
        error = None

        if not ipaddress:
            error = 'You need to enter IP address. (IPアドレスをいれてください)'
        elif not servername:
            error = 'You need to enter a name. (なまえをいれてください)'
        
        if error is None:
            error = add_dns_resource(ipaddress, servername)
            pass
        
        if error is None:
            return render_template('registration/view.html')
            #return render_template('registration/success.html')
        
        flash(error)
        return render_template('registration/view.html')

def add_dns_resource(ipaddress, servername):
    '''Add a new record to DNS. Returning None for success. Error string for failure.'''
    zoneid = 'Z04921881CATTNOQUCZ18'
    fullname = '{0}.{1}'.format(servername, domainname)
    try:
        response = boto3.client('route53').change_resource_record_sets(
            HostedZoneId = zoneid,
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
        return None
    except Exception as e:
        return 'Error {0}'.format(str(e))

