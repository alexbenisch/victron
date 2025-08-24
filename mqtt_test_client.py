#!/usr/bin/env python3
"""
MQTT Test Client for Victron MPPT Data
Tests MQTT authentication and subscribes to MPPT topics
"""
import os
import json
import logging
import time
from datetime import datetime
import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MQTTTestClient:
    def __init__(self):
        # Load environment variables
        self.mqtt_host = os.getenv("MQTT_HOST", "localhost")
        self.mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
        self.mqtt_user = os.getenv('MQTT_USER')
        self.mqtt_password = os.getenv('MQTT_PASSWORD')
        self.device_id = os.getenv('MPPT_MAC_ADDRESS', 'unknown')
        
        # MQTT client
        self.client = None
        self.connected = False
        self.message_count = 0
        
        # Topics to subscribe to
        self.base_topic = "victron/mppt150_45"
        self.topics = [
            f"{self.base_topic}/+",      # All individual values
            f"{self.base_topic}/all",    # Complete data
            "victron/+",                 # Any victron device
            "$SYS/broker/version",       # Broker info
        ]
        
        if not all([self.mqtt_user, self.mqtt_password]):
            raise ValueError("Missing MQTT_USER or MQTT_PASSWORD environment variables")
        
        logger.info(f"MQTT Test Client Configuration:")
        logger.info(f"  Host: {self.mqtt_host}:{self.mqtt_port}")
        logger.info(f"  User: {self.mqtt_user}")
        logger.info(f"  Device ID: {self.device_id}")
        logger.info(f"  Base Topic: {self.base_topic}")
    
    def on_connect(self, client, userdata, flags, rc, properties=None):
        """Callback for MQTT connection"""
        if rc == 0:
            self.connected = True
            logger.info("✓ Successfully connected to MQTT broker")
            logger.info(f"  Connection flags: {flags}")
            
            # Subscribe to topics
            logger.info("Subscribing to topics:")
            for topic in self.topics:
                result, mid = client.subscribe(topic)
                if result == mqtt.MQTT_ERR_SUCCESS:
                    logger.info(f"  ✓ Subscribed to: {topic}")
                else:
                    logger.error(f"  ✗ Failed to subscribe to: {topic}")
        else:
            self.connected = False
            error_messages = {
                1: "Connection refused - incorrect protocol version",
                2: "Connection refused - invalid client identifier",
                3: "Connection refused - server unavailable",
                4: "Connection refused - bad username or password",
                5: "Connection refused - not authorized"
            }
            error_msg = error_messages.get(rc, f"Connection refused - unknown error ({rc})")
            logger.error(f"✗ MQTT connection failed: {error_msg}")
    
    def on_disconnect(self, client, userdata, flags, rc, properties=None):
        """Callback for MQTT disconnection"""
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected MQTT disconnection (code: {rc})")
        else:
            logger.info("MQTT disconnected")
    
    def on_message(self, client, userdata, msg):
        """Callback for received MQTT messages"""
        self.message_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        try:
            # Try to decode as JSON
            if msg.topic.endswith('/all'):
                payload = json.loads(msg.payload.decode())
                logger.info(f"[{timestamp}] 📦 COMPLETE DATA from {msg.topic}:")
                for key, value in payload.items():
                    logger.info(f"    {key}: {value}")
            else:
                payload = msg.payload.decode()
                logger.info(f"[{timestamp}] 📨 {msg.topic}: {payload}")
                
        except json.JSONDecodeError:
            payload = msg.payload.decode()
            logger.info(f"[{timestamp}] 📨 {msg.topic}: {payload}")
        except Exception as e:
            logger.error(f"[{timestamp}] ❌ Error processing message: {e}")
            logger.error(f"    Topic: {msg.topic}")
            logger.error(f"    Payload: {msg.payload}")
    
    def on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
        """Callback for subscription confirmation"""
        logger.debug(f"Subscription confirmed (mid: {mid}, QoS: {granted_qos})")
    
    def test_connection(self):
        """Test MQTT connection and authentication"""
        logger.info("="*60)
        logger.info("TESTING MQTT CONNECTION")
        logger.info("="*60)
        
        try:
            # Create client
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"victron_test_{int(time.time())}")
            
            # Set credentials
            self.client.username_pw_set(self.mqtt_user, self.mqtt_password)
            
            # Set callbacks
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message
            self.client.on_subscribe = self.on_subscribe
            
            # Connect
            logger.info(f"Connecting to {self.mqtt_host}:{self.mqtt_port}...")
            self.client.connect(self.mqtt_host, self.mqtt_port, 60)
            
            # Start loop
            self.client.loop_start()
            
            # Wait for connection
            timeout = 10
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if not self.connected:
                logger.error("❌ Connection timeout")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            return False
    
    def test_publish(self):
        """Test publishing a message"""
        if not self.connected:
            logger.error("Not connected to MQTT broker")
            return
            
        logger.info("\n" + "="*60)
        logger.info("TESTING MQTT PUBLISH")
        logger.info("="*60)
        
        test_topic = f"{self.base_topic}/test"
        test_message = {
            "timestamp": datetime.now().isoformat(),
            "test": True,
            "device_id": self.device_id,
            "message": "MQTT test from victron client"
        }
        
        try:
            result = self.client.publish(test_topic, json.dumps(test_message), retain=True)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"✓ Test message published to {test_topic}")
            else:
                logger.error(f"✗ Failed to publish test message (rc: {result.rc})")
        except Exception as e:
            logger.error(f"❌ Publish error: {e}")
    
    def monitor(self, duration=30):
        """Monitor MQTT messages for specified duration"""
        if not self.connected:
            logger.error("Not connected to MQTT broker")
            return
            
        logger.info("\n" + "="*60)
        logger.info(f"MONITORING MQTT MESSAGES FOR {duration} SECONDS")
        logger.info("="*60)
        logger.info("Waiting for messages from Victron MPPT...")
        logger.info("(Run your main.py script in another terminal)")
        
        start_time = time.time()
        last_count = 0
        
        try:
            while (time.time() - start_time) < duration:
                time.sleep(1)
                
                # Show periodic status
                elapsed = int(time.time() - start_time)
                if self.message_count != last_count:
                    logger.info(f"📊 Messages received: {self.message_count} (after {elapsed}s)")
                    last_count = self.message_count
                elif elapsed % 10 == 0 and elapsed > 0:
                    logger.info(f"⏱️  Still monitoring... {elapsed}s elapsed, {self.message_count} messages received")
                    
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        
        logger.info(f"\n📈 MONITORING COMPLETE:")
        logger.info(f"  Duration: {int(time.time() - start_time)}s")
        logger.info(f"  Messages: {self.message_count}")
        logger.info(f"  Rate: {self.message_count/(time.time() - start_time):.2f} msg/s")
    
    def cleanup(self):
        """Clean up MQTT connection"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("MQTT client disconnected")

def main():
    """Main test function"""
    print(f"Victron MQTT Test Client - {datetime.now()}")
    print("="*60)
    
    try:
        # Create test client
        mqtt_test = MQTTTestClient()
        
        # Test connection
        if not mqtt_test.test_connection():
            logger.error("MQTT connection test failed")
            return 1
        
        # Test publish
        mqtt_test.test_publish()
        
        # Monitor messages
        mqtt_test.monitor(duration=60)  # Monitor for 1 minute
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please set MQTT_USER and MQTT_PASSWORD environment variables")
        return 1
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Test error: {e}")
        return 1
    finally:
        if 'mqtt_test' in locals():
            mqtt_test.cleanup()
    
    return 0

if __name__ == "__main__":
    exit(main())