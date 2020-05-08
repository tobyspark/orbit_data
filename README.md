# ORBIT Data

A web-app to collate and administrate a dataset. Comprises REST API for data upload from native clients, and Admin interface for verification and export of the data. 

Built with Python using the Django framework. Provisioning for a CentOS VPS.

## Version history

v1.0 
- As per ORBIT Camera iOS app v1.0
- Phase one study launch May 2020


# Notes to self, to sort...

In / Out times - We found we needed them in the pilot, but that was pre-instructions. So they're there in the data model, but currently ignored on export. will need ffmpeg or similar installed


## dev / fish

```
cd (mdfind -name 'Orbit-Webapp-Pilot')
source ./env/bin/activate.fish
set -x STATIC_ROOT /Volumes/ORBIT\ Data/static
set -x MEDIA_ROOT /Volumes/ORBIT\ Data/media
set -x PII_KEY_PUBLIC (cat /Volumes/ORBIT\ Keys/orbit-pii-public.pem | string split0)
set -x PII_KEY_PRIVATE (cat /Volumes/ORBIT\ Keys/orbit-pii-private.pem  | string split0)
cd orbit/
python manage.py runserver 0:8000
```

Note fish-ism `| string split0` to handle multiline var, otherwise converts newlines to list, i.e. spaces


For HTTPS only ngrok –
```
./ngrok http --bind-tls=true 8000
```

## production / bash

To provision the City CentOS server –

1. Get SSL cert and add to `orbit_nginx.conf` e.g.
   ```
   server {
       listen 443 ssl;
       ssl_certificate /etc/nginx/ssl/smcse-orbit00_city_ac_uk.crt;
       ssl_certificate_key /etc/nginx/ssl/smcse-orbit00_city_ac_uk.key;
   ```
1. As root, create orbit user  
   ```
   adduser orbit
   passwd orbit
   ```
2. As orbit, create SSH key for log-in to GitHub  
   ```
   mkdir .ssh
   nano .ssh/id_rsa
   nano .ssh/id_rsa.pub
   chmod -R go-rwx .ssh
   ```
3. Load SSH key  
   ```
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_rsa
   ```
4. Clone repo  
   ```
   git clone git@github.com:tobyspark/orbit_webapp.git
   ```
5. As root, run provision script  
   ```
   /home/orbit/orbit_webapp/provision/provision.bash
   ```
   