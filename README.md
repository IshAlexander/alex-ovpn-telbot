# alex-ovpn-telbot
Telegram bot for managing OpenVPN server build in docker container inside Raspberry PI or VM

##OpenVPN Management via Telegram Bot
This software is designed for the rapid deployment and management of OpenVPN using a Telegram bot interface. It simplifies the process of managing VPN users and monitoring the VPN server by packaging everything into two small Docker containers, requiring minimal configuration.
it is depend on docker from https://github.com/dockovpn/dockovpn.git

###Features
Easy Deployment: The entire setup is contained within two Docker containers, making it straightforward to deploy on various platforms, including Raspberry Pi and other ARM-based devices.

User Management: Add or remove VPN users directly through the Telegram bot. The bot provides a simple and intuitive interface for managing user access to your VPN.

Server Monitoring: Check the temperature of your VPN server and view your external IP address via the Telegram bot. This helps you monitor the health and status of your VPN server in real-time.

Secure Access: Users can securely connect to the VPN by receiving an OVPN file from the bot. The bot validates users with a password, ensuring only authorized users can access the VPN.

###Getting Started
Clone the repository on RPI and navigate to the project directory:

```
git clone https://github.com/IshAlexander/alex-ovpn-telbot.git
```

Get your telegram id from https://t.me/usinfbot and bot token from the botfather https://t.me/BotFather and use the values in the setup.sh script:

```

Start the setup.sh script to install the required dependencies and configure the Docker containers:

```
sudo ./setup.sh <rpi4|rpi5|without-compose> <ADMIN_USER_ID> <TELEGRAM_BOT_TOKEN>
```

For example, to deploy the bot on a Raspberry Pi 5 with the admin user ID 1111111111 the Telegram bot token 222222222:aaaaaaaaaaaaaaaaaaaaaa, run the following command:

```
sudo ./setup.sh rpi5 1111111111 222222222:aaaaaaaaaaaaaaaaaaaaaa
```

Don't forget about potr forwarding for vpn 1194 on your router to the RPI
