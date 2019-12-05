# orbit_pilot

...currently notes to self. check all these commands before actioning, it has been assembled retrospectively

## dev / fish / venv

```
cd (mdfind -name 'Orbit-Webapp-Pilot')
source ./env/bin/activate.fish
set -x STATIC_ROOT 'xxx'
set -x MEDIA_ROOT 'xxx'
cd orbit_pilot/
python manage.py runserver 0:8000
```
 
## server / bash

```
ssh root@...

apt-get update && apt-get upgrade

adduser example_user
adduser example_user sudo

mkdir /home/orbit/.ssh
cp ~/.ssh/authorized_keys /home/orbit/.ssh/authorized_keys
chown -R orbit /home/orbit/.ssh
chmod -R 700 /home/orbit/.ssh && chmod 600 /home/orbit/.ssh/authorized_keys

sed -i.bak 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
```
...and the same for `AddressFamily inet`

```
ssh orbit@...

sudo apt-get install fail2ban

ufw default deny incoming
ufw allow ssh
ufw allow http/tcp
ufw --force enable
ufw status

pip3 install django==2.2.6
pip3 install django-form-utils
sudo apt-get install gunicorn3
sudo apt-get install nginx

cd /home/orbit/orbit_pilot

sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak
sudo cp provision/nginx.conf /etc/nginx/nginx.conf
sudo nginx -s reload

set -a; source .env; set +a
python3 manage.py collectstatic
gunicorn3 -b unix:/tmp/gunicorn.sock orbit_pilot.wsgi
```