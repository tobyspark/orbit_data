# orbit

...currently notes to self. check all these commands before actioning, it has been assembled retrospectively

## dev / fish / venv

```
cd (mdfind -name 'Orbit-Webapp-Pilot')
source ./env/bin/activate.fish
set -x STATIC_ROOT (mdfind -name 'ORBITscratch')/static
set -x MEDIA_ROOT (mdfind -name 'ORBITscratch')/media
set -x PII_KEY_PRIVATE (cat (mdfind -name 'ORBITscratch')/keys/private.pem | string split0)
set -x PII_KEY_PUBLIC (cat (mdfind -name 'ORBITscratch')/keys/public.pem | string split0)
cd orbit/
python manage.py runserver 0:8000
```

Note fish-ism `| string split0` to handle multiline var, otherwise converts newlines to list, i.e. spaces

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
pip3 install django-parsley
pip3 install djangorestframework
pip3 install jinja2
pip3 install pycryptodomex
sudo apt-get install gunicorn3
sudo apt-get install nginx

cd /home/orbit/orbit

sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak
sudo cp provision/nginx.conf /etc/nginx/nginx.conf
sudo nginx -s reload

set -a; source .env; set +a
python3 manage.py collectstatic
gunicorn3 -b unix:/tmp/gunicorn.sock orbit.wsgi
```