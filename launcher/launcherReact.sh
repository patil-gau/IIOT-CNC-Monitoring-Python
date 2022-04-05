#!/bin/sh
# launcher1.sh
# navigate to home directory, then to this directory, then execute python $

cd /
cd /home/pi/Desktop/raspi/iiotpython_main
sudo serve -s build -l 4200
cd /
