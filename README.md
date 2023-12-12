# GreenHouseDT Frontend

The frontend for the GreenHouseDT is a Flask application developed in Python to give the user a dashboard to present the changes that the Digital Twin can undergo, as well as the possibility to show the structural self-adaptation by updating the asset model.

## Installation

To install the whole frontend, the following packages are required (the following code show how to install on a Debian-based Operating System)

```bash
sudo apt update
sudo apt install -y wget curl git python3 python3-pip python3-venv apache2 libapache2-mod-wsgi-py3 dialog
```

### Python configuration

To work under the Apache2 folder, it is recommended to clone this repository under `/var/www` folder (in this example, the folder `greenhousedt.local` will be used). Inside the folder the following file needs to be created:

- WSGI file that will be used by `Apache` to run the server
- `.env` file containing the information needed by the application

The following configuration is the example one for the `.env` file

```env
URL=<url for ActiveMQ example localhost>
USER=<username for ActiveMQ>
PASS=<password for ActiveMQ>
MODE=demo
INFLUXDB_URL=<InfluxDB url, example: http://localhost:8086>
INFLUXDB_ORG=<Influx Org>
INFLUXDB_TOKEN_DEMO=<Influx token>
INFLUXDB_TOKEN_PROD=<Influx token>
INFLUXDB_BUCKET_DEMO=<Influx Bucket for demo, example: GreenHouseDemo>
INFLUXDB_BUCKET_PROD=<Influx Bucket for greenhouse, example: GreenHouse>
```

for the wsgi file the configuration would be the following

```python
import sys
import os
from pathlib import Path

sys.path.insert(0, "/var/www/greenhousedt.local")
sys.path.insert(0, "/var/www/greenhousedt/lib/python3.10/site-packages")
sys.path.insert(0, "/var/www/greenhousedt.local/.env")
sys.path.insert(0, "/model/model.txt")

from app import app as application
```

To ensure to have the correct python dependencies execute the following

```bash
cd /var/www
python3 -m venv greenhousedt
source greenhousedt/bin/activate
pip install -r greenhousedt.local/requirements.txt
chown -R www-data: /var/www
```

### Apache configuration

For Apache, the file under `/etc/apache2/sites-available/greenhousedt.conf` needs to be created and the following must be used as configuration

```bash
<VirtualHost *:80>
    Servername greenhousedt.local
    ServerAlias localhost
    ServerAlias 127.0.0.1
    ServerAdmin webmaster@localhost
    DocumentRoot /var/www/greenhousedt.local

    LogLevel info

    WSGIDaemonProcess greenhousedt.local python-path=/var/www/greenhousedt/lib/python3.10/site-packages
    WSGIScriptAlias / /var/www/greenhousedt.local/greenhousedt.local.wsgi
    WSGIProcessGroup greenhousedt.local

    Alias /static /var/www/greenhousedt.local/static

    <Directory /var/www/greenhousedt.local/static>
        <IfVersion >= 2.4>
            Require all granted
        </IfVersion>
        <IfVersion < 2.4>
            Order allow,deny
            Allow from all
        </IfVersion>
    </Directory>

    <Directory /var/www/greenhousedt.local>
        <IfVersion >= 2.4>
            Require all granted
        </IfVersion>
        <IfVersion < 2.4>
            Order allow,deny
            Allow from all
        </IfVersion>

        WSGIProcessGroup greenhousedt.local
        WSGIApplicationGroup %{GLOBAL}
        WSGIScriptReloading On
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

To ensure the website to be accessible, the following element must be added to the host file with 

```bash
sudo sh -c "echo '127.0.0.1 greenhousedt.local' >> /etc/hosts"
```

Finally, the soft link for the apache configuration and the restart of Apache can be done with the following commands

```bash
sudo ln -s /etc/apache2/sites-available/greenhousedt.conf /etc/apache2/sites-enabled/greenhousedt.local.conf
sudo mv /etc/apache2/sites-available/000-default.conf /etc/apache2/sites-available/000-default.conf.bak
sudo systemctl daemon-reload
sudo systemctl restart apache2
sudo systemctl enable apache2
```

#### Read the model file

To ensure that the model file is present and readable by the application the following configuration has to be done (we consider the user of the Operating System to be `lab`)

```bash
sudo mkdir /model
sudo touch /model/model.txt
sudo groupadd web
sudo chown -R :web /model
sudo chmod -R 755 /model
sudo usermod -a -G web www-data
sudo usermod -a -G web lab
```

### Add data to the InfluxDB

To add data we can use the `influx` cli (provided it was installed during the setup of the Simulation Driver). The following command can be used to automate the process (considering the user to be `lab`)

```bash
sudo mv /var/www/greenhousedt.local/basic_data.csv /home/lab
sudo chown lab: /home/lab/basic_data.csv
su - lab -c 'influx write --bucket <GreenHouseDemo> --org <MyOrg> --token <MyToken> -f /home/lab/basic_data.csv'
rm /home/lab/basic_data.csv
```

Finally, the script to change parameters need to be saved under the user folder

```bash
sudo mv /var/www/greenhousedt.local/execution_mode.sh /home/lab/change_parameters.sh
sudo chown lab: /home/lab/Desktop/change_parameters.sh
```

Once the simulation driver will be operating, the output will be present under the webpage `http://greenhousedt.local`
