#!/bin/bash -e

ctx logger debug "${COMMAND}"

echo '<h3> update : client </h3>' | sudo tee --append /var/www/update.html