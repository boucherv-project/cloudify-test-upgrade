#!/bin/bash -e

ctx logger debug "${COMMAND}"


sudo mkdir /var/www
sudo cp /home/vagrant/cloudify/blueprints/cloudify-test-upgrade/resources/html/* /var/www/
sudo chown -R nginx:nginx /var/www
sudo chmod -R 777 /var/www

sudo cp /home/vagrant/cloudify/blueprints/cloudify-test-upgrade/resources/test.conf /etc/nginx/conf.d/test.conf
sudo service nginx restart


