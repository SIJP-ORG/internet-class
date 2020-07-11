# message app

## Development cycle

- Copy files from this directory to ~/message

- Debug mode (port 5001)
```
cd ~/message
. venv/bin/activate
export FLASK_APP=messageapp
export FLASK_ENV=development
flask run -h 0.0.0.0 -p 5001
```

- Restart Apache2 and monitor the log
```
sudo apachectl restart && tail -f /var/log/apache2/error.log
```

## Setup
- Launch EC2 instance
  - Ubuntu Server 18.04 LTS, x86
  - t3a.nano
  - default VPC
  - IAM role: None
  - Terminate protection: on
  - SSD: 8GB
  - New security group: name = messenger
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
cd ~/message
virtualenv venv
. venv/bin/activate
pip3 install Flask mojimoji requests pprint dnspython
sudo ln -sT ~/message /var/www/html/message
```
- edit /etc/apache2/sites-enabled/000-default.conf
```
        DocumentRoot /var/www/html

        WSGIDaemonProcess messageapp threads=5
        WSGIScriptAlias / /var/www/html/message/messageapp.wsgi

        <Directory message/>
                Order allow,deny
                Allow from all
        </Directory>

        Alias /static /var/www/html/message/messageapp/static
```
