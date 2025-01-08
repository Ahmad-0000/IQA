#!/usr/bin/bash
# Configure Nginx web server to serve static content

echo "Create static files directory"
echo ===============================
mkdir -p /var/www/iqa
echo
echo "Copy web_dynamic content to static files directory"
echo ===============================
cp -r web_dynamic/* /var/www/iqa
echo
echo "Copy nginx configuration file"
echo ===============================
cp nginx.config /etc/nginx/sites-available/iqa
echo
echo "Create nginx symlink"
echo ===============================
ln -fs /etc/nginx/sites-available/iqa /etc/nginx/sites-enabled/iqa
echo
echo "Restart nginx"
echo ===============================
systemctl restart nginx
