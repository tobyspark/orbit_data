echo "***"
echo "*** Provision ORBIT Web App"
echo "***"

# Assumes run as root
# Assumes orbit user already created

# As root...
if [ $EUID -ne 0 ]; then
    echo "This script part must be run as root"
    exit 1
fi


# Install web app system stack from OS repository
yum -y install nginx
yum -y install python3
yum -y install uwsgi
yum -y install uwsgi-plugin-python36
yum -y install git

# Create web app data storage directory
if [ ! -x /orbit-data/pilot/media ]; then
    mkdir /orbit-data/pilot
    mkdir /orbit-data/pilot/media
    chown -R orbit:orbit /orbit-data/pilot
fi

# NGINX setup
#   First, remove server blocks from master nginx.conf
#   this is based on nginx.conf as found, fragile.
#   original conf file should be preserved as nginx.conf.bak
if grep --regex='^    server {' /etc/nginx/nginx.conf; then
    sed -i.bak -e '/^    server {/,$d' /etc/nginx/nginx.conf # strip everything from server onwards
    echo "}" >> /etc/nginx/nginx.conf # add closing bracket back in
fi
#   Second, create desired server block in conf.d
#   Note the socket is hard-coded here, .env has not been read
cat /home/orbit/orbit_webapp/provision/orbit_nginx.conf \
| sed "s/kDOMAIN/$HOSTNAME/g" \
| sed "s,kSOCKET,127.0.0.1:29000,g" \
| sed 's,kSTATIC,/orbit-data/pilot/static/,g' \
> /etc/nginx/conf.d/$HOSTNAME.conf

# uwsgi setup
if [ ! -x /etc/uwsgi/apps-available ]; then
    mkdir /etc/uwsgi
    mkdir /etc/uwsgi/apps-available
fi
cat /home/orbit/orbit_webapp/provision/orbit_uwsgi.ini \
| sed "s,kSOCKET,127.0.0.1:29000,g" \
> /etc/uwsgi/apps-available/$HOSTNAME.ini

# ...systemd setup
cp /home/orbit/orbit_webapp/provision/uwsgi.service /etc/systemd/system/uwsgi.service

# As orbit...
sudo -i -u orbit bash << EOF
if [ "\$USER" != 'orbit' ]; then # escape variable for heredoc
    echo "This script part must be run as orbit"
    exit 1
fi

# Source web app environmental variables
# Note: this is created manually, using template.env
set -a; source /home/orbit/orbit_webapp/.env; set +a

# Create Python virtualenv for web app
if [ ! -x /home/orbit/env/orbit_webapp ]; then
    mkdir /home/orbit/env
    python3 -m venv /home/orbit/env/orbit_webapp
fi

# Activate virtualenv
source /home/orbit/env/orbit_webapp/bin/activate

# Install web app Python dependencies
pip install -r /home/orbit/orbit_webapp/provision/requirements.txt

# Temporary workaround
# > Django 2.2
# > The minimum supported version of SQLite is increased from 3.7.15 to 3.8.3.
# ...so either i. recompile python or ii. downgrade django or iii. setup postgres
# expediency wins for the pilot
pip uninstall -y django
pip install django==2.1.*

# Collect static files from Django apps into directory nginx will serve from
python /home/orbit/orbit_webapp/manage.py collectstatic --no-input

# Possibly not necessary, need a clean machine to check
chown -R orbit:orbit $STATIC_ROOT
chown -R orbit:orbit $MEDIA_ROOT
chmod -R go-w $STATIC_ROOT
chmod -R go-w $MEDIA_ROOT

# As root...
EOF
if [ $EUID -ne 0 ]; then
    echo "This script part must be run as root"
    exit 1
fi

# Start services, now
systemctl start nginx
systemctl start uwsgi

# Enable services, to resume on boot
systemctl enable nginx
systemctl enable uwsgi

