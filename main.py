#!/usr/bin/env python
import asyncio
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from victron_ble.devices import Device
from victron_ble.scanner import Scanner
import paho.mqtt.client as mqtt

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class VictronMPPTReader:
    def __init__(self):
        # Note: MPPT_MAC_ADDRESS should be the device identifier (e.g., from victron-ble command)
        # Format: "763aeff5-1334-e64a-ab30-a0f478s20fe1" (not a standard BLE MAC address)
        self.mac_address = os.getenv('MPPT_MAC_ADDRESS')
        self.encryption_key = os.getenv('ENCRYPTION_KEY')
        self.mqtt_host = os.getenv("MQTT_HOST")
        self.mqtt_user = os.getenv('MQTT_USER')
        self.mqtt_password = os.getenv('MQTT_PASSWORD')
        self.device: Optional[Device] = None
        self.mqtt_client: Optional[mqtt.Client] = None
        
        if not all([self.mac_address, self.encryption_key, self.mqtt_user, self.mqtt_password]):
            raise ValueError("Missing required environment variables")
    
    async def connect_to_mppt(self) -> bool:
        try:
            logger.info(f"Connecting to MPPT at {self.mac_address}")
            
            # Create scanner with device keys - format as proper BLE MAC address
            # Convert device identifier to BLE MAC format (DA:6F:E9:6F:94:CE)
            formatted_mac = ':'.join(self.mac_address[i:i+2] for i in range(0, len(self.mac_address), 2)).upper()
            device_keys = {formatted_mac: self.encryption_key}
            logger.info(f"Using device key: {formatted_mac} -> {self.encryption_key[:8]}...")
            scanner = Scanner(device_keys)
            
            # Set up a flag to track if device is found
            self.device_found = False
            
            # Override the callback to capture our device
            def custom_callback(ble_device, raw_data):
                logger.info(f"Discovered device: {ble_device.address}")
                # Try to get device using the scanner (it will match against our device_keys)
                try:
                    device = scanner.get_device(ble_device, raw_data)
                    if device:
                        logger.info(f"Found matching device: {ble_device.address}")
                        self.device = device
                        self.raw_data = raw_data  # Store raw data for parsing
                        self.device_found = True
                except Exception as e:
                    logger.debug(f"Device {ble_device.address} not matching: {e}")
            
            scanner.callback = custom_callback
            
            # Start scanning
            await scanner.start()
            
            # Wait a bit for device discovery
            import asyncio
            await asyncio.sleep(5)
            
            # Stop scanning
            await scanner.stop()
            
            if self.device and self.device_found:
                logger.info("Successfully connected to MPPT")
                return True
            else:
                logger.error("Failed to find or connect to MPPT device")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to MPPT: {e}")
            return False
    
    def setup_mqtt(self):
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqtt_client.username_pw_set(self.mqtt_user, self.mqtt_password)
        
        def on_connect(client, userdata, flags, rc, properties):
            if rc == 0:
                logger.info("Connected to MQTT broker")
            else:
                logger.error(f"Failed to connect to MQTT broker: {rc}")
        
        def on_disconnect(client, userdata, flags, rc, properties):
            logger.info("Disconnected from MQTT broker")
        
        self.mqtt_client.on_connect = on_connect
        self.mqtt_client.on_disconnect = on_disconnect
        
        try:
            self.mqtt_client.connect(self.mqtt_host, 1883, 60)
            self.mqtt_client.loop_start()
        except Exception as e:
            logger.error(f"Error connecting to MQTT: {e}")
            raise
    
    async def read_mppt_data(self) -> Optional[Dict[str, Any]]:
        if not self.device or not hasattr(self, 'raw_data'):
            logger.error("No device connection or raw data available")
            return None
        
        try:
            # Parse the raw advertisement data
            parsed_data = self.device.parse(self.raw_data)
            if parsed_data:
                logger.info("Successfully read MPPT data")
                logger.debug(f"Parsed data type: {type(parsed_data)}")
                logger.debug(f"Parsed data attributes: {[attr for attr in dir(parsed_data) if not attr.startswith('_')]}")
                
                # Convert the parsed data object to dictionary
                data_dict = {}
                for attr_name in dir(parsed_data):
                    if not attr_name.startswith('_'):
                        attr_value = getattr(parsed_data, attr_name)
                        if callable(attr_value) and attr_name.startswith('get_'):
                            # Call the getter method to get the actual value
                            try:
                                value = attr_value()
                                field_name = attr_name[4:]  # Remove 'get_' prefix
                                # Convert enum values to strings for JSON serialization
                                if hasattr(value, 'name'):
                                    value = value.name  # Use enum name (e.g., 'FLOAT' instead of OperationMode.FLOAT)
                                elif hasattr(value, 'value'):
                                    value = value.value  # Use enum value if no name
                                data_dict[field_name] = value
                                logger.debug(f"  {field_name}: {value}")
                            except Exception as e:
                                logger.debug(f"  Error calling {attr_name}: {e}")
                        elif not callable(attr_value):
                            # Include non-callable attributes
                            data_dict[attr_name] = attr_value
                            logger.debug(f"  {attr_name}: {attr_value}")
                
                return {
                    'timestamp': datetime.now().isoformat(),
                    **data_dict  # Include all parsed data fields
                }
            return None
        except Exception as e:
            logger.error(f"Error reading MPPT data: {e}")
            return None
    
    def publish_to_mqtt(self, data: Dict[str, Any]):
        if not self.mqtt_client or not data:
            return
        
        base_topic = "victron/mppt150_45"
        
        for key, value in data.items():
            if value is not None:
                topic = f"{base_topic}/{key}"
                payload = json.dumps(value) if not isinstance(value, (int, float, str)) else str(value)
                
                try:
                    result = self.mqtt_client.publish(topic, payload, retain=True)
                    if result.rc == mqtt.MQTT_ERR_SUCCESS:
                        logger.debug(f"Published {key}: {payload}")
                    else:
                        logger.warning(f"Failed to publish {key}")
                except Exception as e:
                    logger.error(f"Error publishing {key}: {e}")
        
        full_data_topic = f"{base_topic}/all"
        full_payload = json.dumps(data)
        try:
            self.mqtt_client.publish(full_data_topic, full_payload, retain=True)
            logger.info("Published complete data to MQTT")
        except Exception as e:
            logger.error(f"Error publishing full data: {e}")
    
    async def run(self):
        logger.info("Starting Victron MPPT MQTT Publisher")
        
        self.setup_mqtt()
        
        connected = await self.connect_to_mppt()
        if not connected:
            logger.error("Could not connect to MPPT device")
            return
        
        try:
            while True:
                data = await self.read_mppt_data()
                if data:
                    self.publish_to_mqtt(data)
                else:
                    logger.warning("No data received from MPPT")
                
                await asyncio.sleep(30)
                
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            if self.mqtt_client:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()


async def main():
    try:
        reader = VictronMPPTReader()
        await reader.run()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please set the following environment variables:")
        logger.error("- MPPT_MAC_ADDRESS (device identifier, e.g., '763aeff5-1334-e64a-ab30-a0f478s20fe1')")
        logger.error("- ENCRYPTION_KEY (32-character hex key)")
        logger.error("- MQTT_USER")
        logger.error("- MQTT_PASSWORD")
    except Exception as e:
        logger.error(f"Application error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
