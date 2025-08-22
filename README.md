# Victron MPPT MQTT Publisher

This application reads data from a Victron MPPT 150/45 solar charge controller via Bluetooth and publishes it to an MQTT broker for Home Assistant integration.

## Features

- Connects to Victron MPPT 150/45 via Bluetooth Low Energy
- Reads comprehensive solar panel and battery data
- Publishes data to MQTT with Home Assistant auto-discovery
- Automatic reconnection and error handling
- Configurable via environment variables

## Prerequisites

- Python 3.13+
- Victron MPPT 150/45 with Bluetooth enabled
- MQTT broker (Home Assistant compatible)
- Bluetooth adapter on your system

## Installation

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Configure environment variables by running the setup script:
   ```bash
   ./setup_env.sh
   ```
   
   Or manually add to `~/.zshenv`:
   ```bash
   export MPPT_MAC_ADDRESS='XX:XX:XX:XX:XX:XX'  # Your MPPT's MAC address
   export ENCRYPTION_KEY='your_encryption_key'    # Your MPPT's encryption key
   export MQTT_USER='your_mqtt_username'          # MQTT broker username
   export MQTT_PASSWORD='your_mqtt_password'      # MQTT broker password
   ```

3. Load environment variables:
   ```bash
   source ~/.zshenv
   ```

## Usage

Run the application:
```bash
python main.py
```

The application will:
1. Connect to your MPPT 150/45 via Bluetooth
2. Connect to your MQTT broker at homeassistant.fritz.box
3. Read data every 30 seconds
4. Publish individual metrics to `victron/mppt150_45/{metric}`
5. Publish complete data to `victron/mppt150_45/all`

## Published Data

The following metrics are published:
- `battery_voltage` - Battery voltage (V)
- `battery_current` - Battery current (A)
- `pv_voltage` - Solar panel voltage (V)
- `pv_current` - Solar panel current (A)
- `pv_power` - Solar panel power (W)
- `yield_today` - Energy yield today (kWh)
- `yield_yesterday` - Energy yield yesterday (kWh)
- `yield_total` - Total energy yield (kWh)
- `charge_state` - Charge controller state
- `load_current` - Load current (A)
- `device_state` - Device operational state
- `timestamp` - Data timestamp

## MQTT Topics

- Individual metrics: `victron/mppt150_45/{metric_name}`
- Complete data: `victron/mppt150_45/all`

All messages are published with retain flag for persistence.

## Troubleshooting

1. **Cannot connect to MPPT**: Ensure Bluetooth is enabled and the MAC address is correct
2. **MQTT connection fails**: Check network connectivity and credentials
3. **No data received**: Verify the encryption key is correct
4. **Permission denied**: Make sure your user has Bluetooth permissions

## Finding Your MPPT Information

To find your MPPT's MAC address and encryption key:
1. Use the Victron Connect app on your phone
2. Connect to your MPPT device
3. MAC address is visible in device information
4. Encryption key can be found in device settings