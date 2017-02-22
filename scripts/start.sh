#!/bin/bash -e

ctx logger info "STARTED"

echo '<h3> start: client </h3>' | sudo tee --append /var/www/update.html
