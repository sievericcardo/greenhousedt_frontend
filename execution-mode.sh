#!/bin/bash

# Check if we are root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit
fi

# Check if we are on macos or linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  # Linux
  operating_system="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
  # Mac OSX
  operating_system="macos"
else
  # Unknown.
  echo "Unknown OS"
  exit
fi

change_operating_mode () {
  dialog --menu "Choose operating mode" 12 45 25 1 "demo" 2 "greenhouse"

  # if the user chose 1 set mode=demo, if 2 set mode=prod
  if [ "$?" = "1" ]; then
    if [ "$operating_system" = "linux" ]; then
      sed -i 's/MODE=.*/MODE=demo/g' .env
    else
      sed -i '' 's/MODE=.*/MODE=demo/g' .env
    fi
  else
    if [ "$operating_system" = "linux" ]; then
      sed -i 's/MODE=.*/MODE=prod/g' .env
    else
      sed -i '' 's/MODE=.*/MODE=prod/g' .env
    fi
  fi
}

change_message_broker () {
  username=""
  password=""

  # open fd
  exec 3>&1

  # Store data to $VALUES variable
  VALUES=$(dialog --ok-label "Submit" \
    --backtitle "Change ActiveMQ credentials" \
    --title "Credentials" \
    --form "Enter new credentials" \
  15 50 0 \
    "Username:" 1 1 "$username" 1 10 10 0 \
    "Password:" 2 1 "$password" 2 10 15 0 \
  2>&1 1>&3)

  # close fd
  exec 3>&-

  # split the form results into username and password
  username=$(echo "$VALUES" | head -1)
  password=$(echo "$VALUES" | tail -1)

  if [ "$operating_system" = "linux" ]; then
    sed -i "s/USER=.*/USER=$username/g" .env
    sed -i "s/PASSWORD=.*/PASSWORD=$password/g" .env
  else
    sed -i "" "s/USER=.*/USER=$username/g" .env
    sed -i "" "s/PASSWORD=.*/PASSWORD=$password/g" .env
  fi
}


while true; do
  selection=$(dialog --menu "Menu" 22 45 45 1 "Change operating mode" 2 "Change ActiveMQ credentials" 3>&1 1>&2 2>&3 3>&-)

  if [ "$selection" = "1" ]; then
    change_operating_mode
  elif [ "$selection" = "2" ]; then
    change_message_broker
  else
    break
  fi
done
