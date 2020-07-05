from flask import redirect, render_template, request, session, url_for
import boto3
from botocore.exceptions import ClientError
import functools
import time
import socket
import re
import mojimoji

DOMAIN = 'ninja.fish'
ZONEID = 'Z04921881CATTNOQUCZ18'
IPLIST = [
    '34.222.205.148',
    '44.234.84.244',
    '100.20.65.5',
    '44.234.23.149',
    '10.1.1.1']

REQUEST_RETRY = 3
SYNC_WAIT_SEC = 10
SYNC_RETRY = 12  # max wait = 120 sec

def show_main():
    '''
    Show main UI initialized.
    '''
    session.clear()

    param = {
        'domain': DOMAIN,
    }
    return render_template('view.html', param=param)

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
    return render_template('view.html', param=param)

def show_success():
    '''
    Show success UI which includes the link to 
    '''
    info = {
        'ipaddress': session['ipaddress'],
        'fullname': session['fullname']
    }
    return render_template('success.html', info=info)


def register():
    '''
    Handle DNS registration request (POST).
    '''
    ipaddress = mojimoji.zen_to_han(request.form['ipaddress'].strip())
    hostname = mojimoji.zen_to_han(request.form['hostname'].strip())
    fullname = '{0}.{1}'.format(hostname, DOMAIN)
    error = None

    if not ipaddress:
        error = "Enter IP address. (IPアドレスを いれてください)"
    elif not is_valid_ipv4_address(ipaddress):
        error = "Invalid IP address format. (IPアドレスの フォーマットが まちがっています)"
    elif not hostname:
        error = "Enter a name. (なまえを いれてください)"
    elif not is_valid_hostname(hostname):
        error = "Invalid hostname. Use only alphabets, numbers, and hyphen. (なまえの フォーマットが まちがっています。アルファベット、すうじ、ハイフンだけが つかえます)"
    elif not ipaddress in IPLIST:
        error = "This IP address is not ours. (このIPアドレスは、わたくしたちの ものでは ありません)"

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
        r53 = boto3.session.Session().client('route53')

        # Create entry
        for waitcount in range (0, REQUEST_RETRY):
            try:
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
                break
            except ClientError as e:
                if 'it already exists' in str(e):
                    return 'This name is already used. (このなまえは、すでにつかわれています)'
                elif e.response['Error']['Code'] == 'Throttling' or e.response['Error']['Code'] == 'PriorRequestNotComplete':
                    time.sleep(10)
                    continue  # retry
                else:
                    raise

        # Wait until completion
        for waitcount in range (0, SYNC_RETRY):
            time.sleep(SYNC_WAIT_SEC)
            try:
                changeResponse = r53.get_change(Id = changeId)
                if changeResponse['ChangeInfo']['Status'] == 'INSYNC':
                    return None # success
            except ClientError as e:
                if e.response['Error']['Code'] == 'Throttling':
                    continue  # retry
                else:
                    raise
        return 'Timeout. Please retry. (じかんぎれです。やりなおしてください)'

    except ClientError as e:
        return 'Error (エラー): {0}: {1}'.format(e.response['Error']['Code'], e)
    except Exception as e:
        return 'Error (エラー): {0}: {1}'.format(str(type(e)), e)

def is_valid_ipv4_address(address):
    '''
    ref. https://stackoverflow.com/a/4017219
    '''
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False

    return True

def is_valid_hostname(hostname):
    return re.match('^[0-9a-zA-Z\-]+$', hostname) is not None


def get_hosts_table():
    '''
    Return table of all registered hosts
    '''
    result = []
    r53 = boto3.session.Session().client('route53')

    listResponse = r53.list_resource_record_sets(
        HostedZoneId = ZONEID,
        MaxItems = '150')

    for entry in listResponse['ResourceRecordSets']:
        name = entry['Name'][:-1]  # drop last dot
        value = entry['ResourceRecords'][0]['Value']
        if entry['Type'] == 'A' and entry['Name'] not in ['dns.'+DOMAIN, 'name.'+DOMAIN]:
            result.append({
                'fullname': name,
                'ipaddress': value,
            })

    result.sort(key=fullname_func)
 
    return render_template('hosts.html', data=result)

def fullname_func(item):
    return item['fullname']
