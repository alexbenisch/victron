#!/bin/bash

# Victron MPPT Service Installation Script

set -e

SERVICE_NAME="victron-mppt"
SERVICE_FILE="$SERVICE_NAME.service"
SYSTEM_SERVICE_DIR="/etc/systemd/system"

echo "Installing Victron MPPT systemd service..."

# Check if running as root for system service installation
if [[ $EUID -ne 0 ]]; then
   echo "This script needs to be run with sudo for system service installation"
   echo "Usage: sudo ./install-service.sh"
   exit 1
fi

# Copy service file to systemd directory
echo "Copying service file to $SYSTEM_SERVICE_DIR..."
cp "$SERVICE_FILE" "$SYSTEM_SERVICE_DIR/"

# Create environment file
ENV_FILE="/etc/default/$SERVICE_NAME"
echo "Creating environment file at $ENV_FILE..."

cat > "$ENV_FILE" << EOF
# Victron MPPT Environment Variables
# Edit these values with your actual configuration

MPPT_MAC_ADDRESS=da6fe96f94ce
ENCRYPTION_KEY=your_encryption_key_here
MQTT_USER=your_mqtt_username
MQTT_PASSWORD=your_mqtt_password
EOF

echo "Environment file created. Please edit $ENV_FILE with your actual values:"
echo "  sudo nano $ENV_FILE"

# Update the service file to use the environment file
sed -i '/# Environment variables/,/# Environment=MQTT_PASSWORD/c\
# Load environment variables from file\
EnvironmentFile=/etc/default/victron-mppt' "$SYSTEM_SERVICE_DIR/$SERVICE_FILE"

# Reload systemd
echo "Reloading systemd daemon..."
systemctl daemon-reload

echo ""
echo "Service installed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit environment variables: sudo nano $ENV_FILE"
echo "2. Enable the service: sudo systemctl enable $SERVICE_NAME"
echo "3. Start the service: sudo systemctl start $SERVICE_NAME"
echo "4. Check status: sudo systemctl status $SERVICE_NAME"
echo "5. View logs: sudo journalctl -u $SERVICE_NAME -f"