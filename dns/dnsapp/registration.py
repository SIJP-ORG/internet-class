from flask import redirect, render_template, request, session, url_for, current_app
import boto3
from botocore.exceptions import ClientError
import json
import functools
import time
import socket
import re
import mojimoji
import os
from filelock import Timeout, FileLock

DOMAIN = 'ninja.fish'
ZONEID = 'Z04921881CATTNOQUCZ18'
IPLIST = [
    '34.222.191.238',
    '44.230.202.157',
    '34.222.182.54',
    '34.223.54.74',
    '34.222.209.36',
    '100.20.64.172',
    '44.226.204.24',
    '34.222.197.57',
    '44.234.115.47',
    '34.223.93.27',
    '44.234.57.186',
    '44.234.40.47',
    '44.234.110.143',
    '44.234.63.51',
    '44.234.8.207',
    '44.226.206.92',
    '44.234.111.55',
    '44.234.71.108',
    '44.234.104.71',
    '44.226.204.97',
    '44.234.89.129',
    '34.223.114.221',
    '34.223.66.195',
    '44.226.205.34',
    '44.234.34.137',
    '34.223.111.145',
    '44.234.43.63',
    '44.234.63.214',
    '44.234.35.237',
    '44.233.249.27',
    '44.234.59.174',
    '44.234.35.210',
    '44.226.204.111',
    '44.234.56.244',
    '44.234.120.28',
    '44.233.146.250',
    '44.234.87.146',
    '34.223.40.179',
    '44.234.87.118',
    '44.234.8.95',
    '44.234.89.136',
    '44.232.183.2',
    '44.234.59.104',
    '34.223.109.127',
    '34.223.100.4',
    '44.234.46.209',
    '44.234.32.241',
    '44.230.198.188',
    '44.234.57.62',
    '44.234.87.195',
    '44.229.15.67',
    '44.233.220.85',
    '44.226.199.149',
    '34.222.208.139',
    '44.234.125.54',
    '44.234.65.47',
    '44.234.84.161',
    '44.230.202.139',
    '34.222.208.179',
    '44.234.105.194',
    '44.226.207.226',
    '44.234.112.9',
    '34.223.88.19',
    '44.234.89.40',
    '44.234.72.77',
    '44.233.249.118',
    '44.234.125.243',
    '44.234.122.73',
    '44.234.126.246',
    '34.223.105.45',
    '34.223.52.90',
    '44.234.65.176',
    '34.222.193.189',
    '34.223.93.50',
    '44.230.211.30',
    '44.230.202.29',
    '34.223.54.137',
    '44.233.116.48',
    '44.234.126.178',
    '34.222.201.18',
    '34.222.199.132',
    '34.223.114.186',
    '44.234.47.41',
    '34.222.177.211',
    '44.234.87.191',
    '44.233.249.11',
    '34.223.109.173',
    '44.234.119.43',
    '34.222.209.29',
    '34.222.180.147',
    '34.223.109.141',
    '44.234.110.10',
    '34.223.105.185',
    '34.223.53.52',
    '44.230.202.51',
    '44.229.11.176',
    '44.234.40.237',
    '34.222.204.230',
    '44.234.42.45',
    '34.222.190.165',
    '100.20.122.48',
    '44.234.58.139',
    '44.229.34.178',
    '34.223.106.231',
    '44.233.153.143',
    '44.234.114.187',
    '44.234.121.74',
    '44.234.126.7',
    '34.222.191.238',
    '44.230.202.157',
    '34.222.182.54',
    '34.223.54.74',
    '34.222.211.245',
    '34.222.182.3',
    '44.234.64.108',
    '34.223.113.134',
    '44.234.112.122',
    '44.234.125.212',
    '34.222.181.140',
    '44.234.84.116',
    '44.234.85.207',
    '44.234.20.196',
    '44.234.60.106',
    '44.234.19.176',
    '44.234.57.4',
    '44.233.116.24',
    '34.223.50.29',
    '44.226.199.226',
    '44.234.118.173',
    '44.229.34.0',
    '44.226.206.50',
    '34.223.91.122',
    '44.234.86.180',
    '34.222.201.88',
    '34.222.203.208',
    '34.223.108.242',
    '44.233.153.185',
    '44.234.51.189',
    '100.20.65.63',
    '34.223.102.255',
    '44.226.198.78',
    '100.20.64.27',
    '44.234.118.205',
    '34.223.113.171',
    '44.234.25.205',
    '44.234.8.89',
    '44.234.42.101',
    '44.234.119.162',
    '44.234.86.90',
    '44.234.89.219',
    '34.222.192.187',
    '44.233.198.49',
    '52.13.125.248',
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
        changeId = None

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
                if not changeId:
                    time.sleep(10)
                    continue  # retry
                break
            except ClientError as e:
                if 'it already exists' in str(e):
                    return 'This name is already used. (このなまえは、すでにつかわれています)'
                elif e.response['Error']['Code'] == 'Throttling' or e.response['Error']['Code'] == 'PriorRequestNotComplete':
                    time.sleep(10)
                    continue  # retry
                else:
                    raise

        if not changeId:
            return 'Failed to register. Please retry. (とうろくにしっぱいしました。やりなおしてください)'

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
    return render_template('hosts.html', data=get_hosts())


def get_hosts():
    '''
    Return the list of dictionary where keys are 'fullname' and 'ipaddress', sorted by full name.
    Read the list of hosts from cache file if available.
    If cache is 5 sec or older, get the data from Route 53 API.
    '''
    lock_file = os.path.join(current_app.instance_path, 'hosts.lock')
    cache_file = os.path.join(current_app.instance_path, 'hosts.cache')

    # Extremely simple lock -- only one request may read and update the cache at one time.
    with FileLock(lock_file, timeout=15):
        fread = None
        try:
            fread = open(cache_file, 'rt')
        except FileNotFoundError:
            pass
        if fread:
            with fread:
                cached_data = json.load(fread)
                cached_time = float(cached_data['timestamp'])
                if time.time() - cached_time < 5.0:
                    #print('*** cache hit')
                    return cached_data['data']

        #print('*** hosts.cache expired (or missing)')
        data = get_hosts_from_api()

        with open(cache_file, 'wt') as fwrite:
            json.dump({
                'timestamp': time.time(),
                'data': data,
            }, fwrite)
        return data


def get_hosts_from_api():
    '''
    Get the list of hosts from Route 53 API
    '''
    result = []
    r53 = boto3.session.Session().client('route53')

    listResponse = r53.list_resource_record_sets(
        HostedZoneId = ZONEID,
        MaxItems = '150')

    for entry in listResponse['ResourceRecordSets']:
        name = entry['Name'][:-1]  # drop last dot
        value = entry['ResourceRecords'][0]['Value']
        if entry['Type'] == 'A' and name not in ['name.'+DOMAIN, 'template.'+DOMAIN]:
            result.append({
                'fullname': name,
                'ipaddress': value,
            })

    result.sort(key=fullname_func)
    return result

def fullname_func(item):
    return item['fullname']
