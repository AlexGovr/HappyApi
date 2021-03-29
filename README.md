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
# API reference
## POST /couriers
Creates new couriers
Request must contain json with a list of couriers' data
Each data element must provide unic courier_id, courier_type , regions and working hours field. All fields are requiried
Input fields:
    courier_id - integer
    courier_type - one of ["car", "bike", "foot"] strings
    regions - list of intergers
    working_hours - list of strings of format "HH:MM-HH:MM"
Returns list of courier_id
Example request:
```
POST /couriers
{
    "data": [
        {
            "courier_id": 1,
            "courier_type": "foot",
            "regions": [1, 12, 22],
            "working_hours": ["11:35-14:05", "09:00-11:00"]
        },
        {
            "courier_id": 2,
            "courier_type": "bike",
            "regions": [22],
            "working_hours": ["09:00-18:00"]
        },
        {
            "courier_id": 3,
            "courier_type": "car",
            "regions": [12, 22, 23, 33],
            "working_hours": []
        },
        ...
    ]
}
```
Success responce
```
HTTP 201 Created
{
    "couriers": [{"id": 1}, {"id": 2}, {"id": 3}]
}
```

## PATCH /couriers/$courier_id
Modifies spicified courier data
Request should contain json with a list of couriers' data fields to be modified
Example request:
```
PATCH /couriers/2
{
    "regions": [11, 33, 2]
}
```
Success responce
```
HTTP 200 OK
{
    "courier_id": 2,
    "courier_type": "foot",
    "regions": [11, 33, 2],
    "working_hours": ["09:00-18:00"]
}
```
## POST /orders
Creates new couriers
Request must contain json with a list of orders' data
Input fields:
    order_id - integer
    region - interger
    delivery_hours - list of strings of format "HH:MM-HH:MM"
Returns list of order_id
Example request:
```
POST /orders
{
    "data": [
        {
            "order_id": 1,
            "weight": 0.23,
            "region": 12,
            "delivery_hours": ["09:00-18:00"]
        },
        {
            "order_id": 2,
            "weight": 15,
            "region": 1,
            "delivery_hours": ["09:00-18:00"]
        },
        {
            "order_id": 3,
            "weight": 0.01,
            "region": 22,
            "delivery_hours": ["09:00-12:00", "16:00-21:30"]
        },
        ...
    ]
}
```
Success responce
```
HTTP 201 Created
{
    "orders": [{"id": 1}, {"id": 2}, {"id": 3}]
}
```
## POST /orders/assign
Takes courier_id and assings orders to this courier
Orders are selected to most effectively utilize courier payload
New orders are assigned to a courier only if he has no active orders
Example request:
```
POST /orders/assign
{
    "courier_id": 2
}
```
Success responce
```
HTTP 200 OK
{
    "orders": [{"id": 1}, {"id": 2}],
    "assign_time": "2021-01-10T09:32:14.42Z"
}
```
## POST /orders/complete
Sets specified order complete
Input fields:
    courier_id
    order_id
    complete_time
Example request:
```
POST /orders/complete
{
    "courier_id": 2,
    "order_id": 33,
    "complete_time": "2021-01-10T10:33:01.42Z"
}
```
Success responce
```
HTTP 200 OK
{
    "order_id": 33
}
```
## GET /couriers/$courier_id
Returns courier info including courier_id, courier_type, working_hours, regions and two additional fields:
    earnings - float
    rating - float
If courier has no completed orders rating will not be included in response
Example request:
```
GET /couriers/2
```
Success responce
```
HTTP 200 OK
{
    "courier_id": 2,
    "courier_type": "foot",
    "regions": [11, 33, 2],
    "working_hours": ["09:00-18:00"],
    "rating": 4.93,
    "earnings": 10000
}
```

# Testing
To test all API methods simply run
```
python manage.py runscript test.py
```

Happy API using!



P.s. for YandexSchool: I didn't managed to permanenly add ssh so run ```eval `ssh-agent -s` ``` and ```ssh-add /home/entrant/.ssh/id_ed``` to get access to the GitHub repository
