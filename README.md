# HappyApi
REST API service for delivery web-application

# Installation
1. Install nginx, postgresql and all needed linux items we need for development:

```sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx```

2. Create postgresql database and user:

```sudo -u postgres psql
CREATE DATABASE myproject;
CREATE USER myprojectuser WITH PASSWORD 'password';
```
set configs recommended by Django documentation:
```
ALTER ROLE myprojectuser SET client_encoding TO 'utf8';
ALTER ROLE myprojectuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE myprojectuser SET timezone TO 'UTC';
```
grant user access:
```
GRANT ALL PRIVILEGES ON DATABASE myproject TO myprojectuser;
```
3. Clone the repository and create python virtual environment within it, e.g. via virtualenv
```
cd HappyApi
pip3 install virtualenv
virtualenv env
```
4. Activate your virtual environment and install all required python packages
```
source env/bin/activate
pip install Django gunicorn django-extensions djangorestframework psycopg2-binary requests
```
5. Copy secret.py and deploy.py from config/example to config/
Edit secret key, database configs and allowed hosts according to your configuration
6. Migrate the initial database schema to your PG database
```
python manage.py makemigrations
python manage.py migrate
```
7. Create superuser
```
python manage.py createsuperuser
```
# Deployment using nginx and gunicorn
1. Create systemd socket for gunicorn in /etc/systemd/system/gunicorn.socket
and put the following contents in it:
```
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```
2. Create systemd service file for gunicorn in /etc/systemd/system/gunicorn.service:
```
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=sammy
Group=www-data
WorkingDirectory=/home/sammy/myprojectdir
ExecStart=/home/sammy/myprojectdir/myprojectenv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          myproject.wsgi:application

[Install]
WantedBy=multi-user.target
```
3. Start and enable the gunicorn socket
```
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
```
4. Configure Nginx to Proxy Pass to Gunicorn
Create /etc/nginx/sites-available/<yourprojectname> file with contents:

```
server {
    listen 80;
    server_name server_domain_or_IP;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/sammy/myprojectdir;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```
5. Enable the file by linking it to the sites-enabled directory
```
sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled
```
6. Open up firewall for nginx
```
sudo ufw allow 'Nginx Full'
```
7. Restart and check gunicorn and ngix processes
```
sudo systemct restart gunicorn
sudo systemct restart nginx
sudo systemct status gunicorn
sudo systemct status nginx
```
8. Collect static to use django admin panel
```
python manage.py collectstatic
```
