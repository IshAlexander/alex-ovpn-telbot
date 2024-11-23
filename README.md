# alex-ovpn-telbot

**Telegram bot for managing an OpenVPN server built in a Docker container inside Raspberry Pi or a Virtual Machine (VM).**

## OpenVPN Management via Telegram Bot

This software is designed for the rapid deployment and management of OpenVPN using a Telegram bot interface. It simplifies the process of managing VPN users and monitoring the VPN server by packaging everything into two small Docker containers, requiring minimal configuration. It depends on Docker, which can be found at [dockovpn](https://github.com/dockovpn/dockovpn.git).

### Features

- **Easy Deployment**: The entire setup is contained within two Docker containers, making it straightforward to deploy on various platforms, including Raspberry Pi and other ARM-based devices.

- **User Management**: Add or remove VPN users directly through the Telegram bot. The bot provides a simple and intuitive interface for managing user access to your VPN.

- **Server Monitoring**: Check the temperature of your VPN server and view your external IP address via the Telegram bot. This helps you monitor the health and status of your VPN server in real-time.

- **Secure Access**: Users can securely connect to the VPN by receiving an OVPN file from the bot. The bot validates users with a password, ensuring only authorized users can access the VPN.

### Getting Started

Docker should be installed on he RPI.

1. **Clone the repository on your Raspberry Pi** and navigate to the project directory:

   ```bash
   sudo apt install docker.io
   git clone https://github.com/IshAlexander/alex-ovpn-telbot.git
   cd alex-ovpn-telbot
   ```

2. **Get your Telegram ID** from [@usinfobot](https://t.me/usinfobot) and a bot token from [BotFather](https://t.me/BotFather). Use these values in the \`setup.sh\` script.

3. **Start the setup script** to install the required dependencies and configure the Docker containers:

   ```bash
   sudo ./setup.sh <rpi4|rpi5|without-compose> <ADMIN_USER_ID> <TELEGRAM_BOT_TOKEN>
   ```

   For example, to deploy the bot on a Raspberry Pi 5 with the admin user ID \`1111111111\` and the Telegram bot token \`222222222:aaaaaaaaaaaaaaaaaaaaaa\`, run the following command:

   ```bash
   sudo ./setup.sh rpi5 1111111111 222222222:aaaaaaaaaaaaaaaaaaaaaa
   ```

4. **Port Forwarding**: Don't forget to configure port forwarding for VPN port `1194` on your router to the Raspberry Pi.
