# orbit

...currently notes to self. check all these commands before actioning, it has been assembled retrospectively

## dev / fish

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

## production / bash

To provision the City CentOS server –
 
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
   