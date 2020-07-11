# DNS app

## Development cycle

- Copy files from this directory to ~/dns

- Debug mode (port 5001)
```
cd ~/dns
. venv/bin/activate
export FLASK_APP=dnsapp
export FLASK_ENV=development
flask run -h 0.0.0.0 -p 5001
```

- Restart Apache2 and monitor the log
```
sudo apachectl restart && tail -f /var/log/apache2/error.log
```

## Setup
- Create new IAM role
  - AmazonRoute53FullAccess
  - Role Name: DnsMachine
- Launch EC2 instance
  - Ubuntu Server 18.04 LTS, x86
  - t3a.nano
  - default VPC
  - IAM role: None
  - Terminate protection: on
  - SSD: 8GB
  - New security group: name = DevSecurityGroup
    - Port 80: all
    - Port 5001: only to home

- Install base software
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3-pip
pip3 install virtualenv
sudo apt-get install apache2 libapache2-mod-wsgi-py3
sudo a2enmod wsgi
```

- Configure application
```
cd ~/dns
virtualenv venv
. venv/bin/activate
pip3 install Flask
pip3 install boto3
pip3 install mojimoji
pip3 install filelock
sudo ln -sT ~/dns /var/www/html/dns
```
- edit /etc/apache2/sites-enabled/000-default.conf
```
        DocumentRoot /var/www/html

        WSGIDaemonProcess dnsapp threads=200
        WSGIScriptAlias / /var/www/html/dns/dnsapp.wsgi

        <Directory dns/>
                Order allow,deny
                Allow from all
        </Directory>

        Alias /static /var/www/html/dns/dnsapp/static
```
