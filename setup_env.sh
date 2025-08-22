#!/bin/bash

# Setup script for Victron MPPT MQTT Publisher
# This script helps configure the required environment variables

echo "Victron MPPT MQTT Publisher - Environment Setup"
echo "================================================"
echo ""

# Check if ~/.zshenv exists
if [ ! -f ~/.zshenv ]; then
    echo "Creating ~/.zshenv file..."
    touch ~/.zshenv
fi

echo "Please provide the following information:"
echo ""

# Get MPPT MAC address
echo -n "Enter your MPPT 150/45 MAC address (format: XX:XX:XX:XX:XX:XX): "
read MPPT_MAC

# Get encryption key
echo -n "Enter your MPPT encryption key: "
read -s ENCRYPTION_KEY
echo ""

# Get MQTT credentials
echo -n "Enter your MQTT username: "
read MQTT_USER

echo -n "Enter your MQTT password: "
read -s MQTT_PASSWORD
echo ""

# Write to ~/.zshenv
echo "" >> ~/.zshenv
echo "# Victron MPPT MQTT Publisher Configuration" >> ~/.zshenv
echo "export MPPT_MAC_ADDRESS='$MPPT_MAC'" >> ~/.zshenv
echo "export ENCRYPTION_KEY='$ENCRYPTION_KEY'" >> ~/.zshenv
echo "export MQTT_USER='$MQTT_USER'" >> ~/.zshenv
echo "export MQTT_PASSWORD='$MQTT_PASSWORD'" >> ~/.zshenv

echo ""
echo "Environment variables have been added to ~/.zshenv"
echo "Please run 'source ~/.zshenv' or restart your terminal to load the variables."
echo ""
echo "To test the configuration, you can run:"
echo "python main.py"