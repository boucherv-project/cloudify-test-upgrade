#!/bin/bash -e

ctx logger debug "${COMMAND}"

sleep 50

echo '<h3> update : client </h3>' | sudo tee --append /var/www/update.html
