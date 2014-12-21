# Apache configuration for reverse proxy to Annalist server on port 8000

Host is `annalist.net`

Virtual host for demo is `demo.annalist.net`

## Commands

    a2ensite demo-annalist.site
    a2enmod proxy
    a2enmod proxy_http
    apachectl configtest
    service apache2 restart

## Configuration files

### demo-annalist.site

Note that the `<VirtualHost *:80>` tag must match the `NameVirtualHost` directive in `ports.conf`.

File: `/etc/apache2/sites-available/demo-annalist.site`

```
# See: 000-default.host, ports.conf
# NameVirtualHost *:80
#
# See also: https://wiki.apache.org/httpd/CommonMisconfigurations

<VirtualHost *:80>
    ServerName  "demo.annalist.net"
    ServerAdmin gk-demo-annalist-net@ninebynine.org
    ErrorLog /var/log/apache2/demo-annalist-error.log
    CustomLog /var/log/apache2/demo-annalist-access.log combined

    <location />
        allow from all
    </location>

    # Redundant?:
    #DocumentRoot "/var/www"
    #
  #<Directory /var/www/>
  # Options Indexes FollowSymLinks MultiViews
  # AllowOverride None
  # Order allow,deny
  # allow from all
  #</Directory>

    ProxyPass        / http://demo.annalist.net:8000/
    ProxyPassReverse / http://demo.annalist.net:8000/
    ProxyPreserveHost On

</VirtualHost>
```

### ports.conf

Note that this file contains the `NameVirtualHost` and `Listen` directives, which should not appear in any other configuration file. 

File: `/etc/apache2/ports.conf`

```
# If you just change the port or add more ports here, you will likely also
# have to change the VirtualHost statement in
# /etc/apache2/sites-enabled/000-default
# This is also true if you have upgraded from before 2.2.9-3 (i.e. from
# Debian etch). See /usr/share/doc/apache2.2-common/NEWS.Debian.gz and
# README.Debian.gz

NameVirtualHost *:80
Listen 80

<IfModule mod_ssl.c>
    # If you add NameVirtualHost *:443 here, you will also have to change
    # the VirtualHost statement in /etc/apache2/sites-available/default-ssl
    # to <VirtualHost *:443>
    # Server Name Indication for SSL named virtual hosts is currently not
    # supported by MSIE on Windows XP.
    Listen 443
</IfModule>

<IfModule mod_gnutls.c>
    Listen 443
</IfModule>

```

### Default site

File: `/etc/apache2/sites-available/default`

```
# See: ports.conf
# NameVirtualHost *:80

<VirtualHost *:80>
        ServerName annalist.net
  ServerAdmin webmaster@localhost

  DocumentRoot /var/www
  <Directory />
    Options FollowSymLinks
    AllowOverride None
  </Directory>
  <Directory /var/www/>
    Options Indexes FollowSymLinks MultiViews
    AllowOverride None
    Order allow,deny
    allow from all
  </Directory>

  ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/
  <Directory "/usr/lib/cgi-bin">
    AllowOverride None
    Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch
    Order allow,deny
    Allow from all
  </Directory>

  ErrorLog ${APACHE_LOG_DIR}/error.log

  # Possible values include: debug, info, notice, warn, error, crit,
  # alert, emerg.
  LogLevel warn

  CustomLog ${APACHE_LOG_DIR}/access.log combined

    Alias /doc/ "/usr/share/doc/"
    <Directory "/usr/share/doc/">
        Options Indexes MultiViews FollowSymLinks
        AllowOverride None
        Order deny,allow
        Deny from all
        Allow from 127.0.0.0/255.0.0.0 ::1/128
    </Directory>

</VirtualHost>
```

