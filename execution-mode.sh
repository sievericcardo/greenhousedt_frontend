#!/bin/bash

# Check if we are root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit
fi

dialog --menu "Choose operating mode" 12 45 25 1 "demo" 2 "greenhouse"

# if the user chose 1 set mode=demo, if 2 set mode=prod
if [ "$?" = "1" ]; then
  sed -i 's/MODE=.*/MODE=demo/g' .env
else
  sed -i 's/MODE=.*/MODE=prod/g' .env
fi

