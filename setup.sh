#!/bin/bash

usage()
{
  echo "Usage: sudo ./setup.sh <rpi4|rpi5|without-compose> <ADMIN_USER_ID> <TELEGRAM_BOT_TOKEN>"
}

# Check if the platform type is provided
if [ -z "$1" ]; then
  echo "Error: Platform type is not provided."
  usage
  exit 1
fi

PLATFORM_TYPE=$1

# Check if ADMIN_USER_ID is provided
if [ -z "$2" ]; then
  echo "Error: ADMIN_USER_ID is not provided. It is the ID of your Telegram account. You can get it from 'userinfobot' inside Telegram."
  usage
  exit 1
fi

ADMIN_USER_ID=$2

# Check if TELEGRAM_BOT_TOKEN is provided
if [ -z "$3" ]; then
  echo "Error: TELEGRAM_BOT_TOKEN is not provided."
  usage
  exit 1
fi

TELEGRAM_BOT_TOKEN=$3

# Set up OpenVPN directory and clone the repository
mkdir -p ./openvpn
cd ./openvpn
git clone https://github.com/dockovpn/dockovpn.git

cd dockovpn/
docker build -t openvpn:local .

cd ../../telegram_bot/
docker build -t telegram-bot:local .

cd ..

# Update ADMIN_USER_ID and TELEGRAM_BOT_TOKEN in docker-compose.yml
sed -i "s/ADMIN_USER_ID=0/ADMIN_USER_ID=$ADMIN_USER_ID/" docker-compose.yml
sed -i "s/TELEGRAM_BOT_TOKEN=/TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN/" docker-compose.yml

# Platform-specific Docker Compose installation
if [ "$PLATFORM_TYPE" == "rpi4" ]; then
  echo "Installing Docker Compose for RPi4..."
  curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-linux-armv7" -o /usr/local/bin/docker-compose
elif [ "$PLATFORM_TYPE" == "rpi5" ]; then
  echo "Installing Docker Compose for RPi5..."
  curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
elif [ "$PLATFORM_TYPE" == "without-compose" ]; then
  echo "Skipping Docker Compose installation as requested..."
else
  echo "Error: Invalid platform type. Use 'rpi4', 'rpi5', or 'without-compose'."
  exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null
then
    echo "Error: docker-compose could not be found. Please install Docker Compose or use the 'rpi4' or 'rpi5' option to install it automatically."
    exit 1
fi

# Apply executable permissions if Docker Compose was downloaded
if [ "$PLATFORM_TYPE" != "without-compose" ]; then
  chmod +x /usr/local/bin/docker-compose
fi

chmod +x telegram_bot/start_telegram_bot.sh

docker-compose up -d
