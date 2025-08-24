#!/usr/bin/env python
"""
Test script to verify the order and usage of MPPT_MAC_ADDRESS and ENCRYPTION_KEY
"""
import os
import logging
from datetime import datetime

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class TestVictronInit:
    def __init__(self):
        logger.info("=== Starting VictronMPPTReader initialization test ===")
        
        # Test 1: Check environment variable access order
        logger.info("Step 1: Accessing MPPT_MAC_ADDRESS...")
        self.mac_address = os.getenv('MPPT_MAC_ADDRESS')
        logger.info(f"MPPT_MAC_ADDRESS = {self.mac_address}")
        
        logger.info("Step 2: Accessing ENCRYPTION_KEY...")
        self.encryption_key = os.getenv('ENCRYPTION_KEY')
        logger.info(f"ENCRYPTION_KEY = {self.encryption_key}")
        
        # Test 2: Show usage order in connection logic
        logger.info("=== Testing connection logic order ===")
        if self.mac_address and self.encryption_key:
            self.test_connection_logic()
        else:
            logger.warning("Environment variables not set - skipping connection logic test")
        
        # Test 3: Validation order
        logger.info("=== Testing validation order ===")
        self.test_validation()
    
    def test_connection_logic(self):
        """Test the order of MAC address and encryption key usage in connection"""
        logger.info("Step 3: Processing MAC address (comes first in connection logic)...")
        
        # Simulate the normalization process from main.py line 35
        normalized_mac = ':'.join(self.mac_address[i:i+2] for i in range(0, len(self.mac_address), 2)).lower()
        logger.info(f"Normalized MAC: {normalized_mac}")
        
        logger.info("Step 4: Creating device_keys with MAC as key and ENCRYPTION_KEY as value...")
        device_keys = {normalized_mac: self.encryption_key}
        logger.info(f"Device keys created: {device_keys}")
        
        logger.info("Result: MAC_ADDRESS is processed FIRST, then used as key for ENCRYPTION_KEY")
    
    def test_validation(self):
        """Test the validation order"""
        logger.info("Step 5: Testing validation order...")
        required_vars = ['MPPT_MAC_ADDRESS', 'ENCRYPTION_KEY', 'MQTT_USER', 'MQTT_PASSWORD']
        
        for i, var in enumerate(required_vars, 1):
            value = os.getenv(var)
            logger.info(f"Validation {i}: {var} = {value}")
        
        # Test the actual validation logic from main.py line 27
        mqtt_user = os.getenv('MQTT_USER') 
        mqtt_password = os.getenv('MQTT_PASSWORD')
        
        if not all([self.mac_address, self.encryption_key, mqtt_user, mqtt_password]):
            logger.error("Validation failed: Missing required environment variables")
        else:
            logger.info("Validation passed: All required variables present")

def test_with_sample_values():
    """Test with sample environment variables"""
    logger.info("\n" + "="*60)
    logger.info("TESTING WITH SAMPLE VALUES")
    logger.info("="*60)
    
    # Set sample values
    os.environ['MPPT_MAC_ADDRESS'] = 'AA:BB:CC:DD:EE:FF'
    os.environ['ENCRYPTION_KEY'] = 'sample_encryption_key_123'
    os.environ['MQTT_USER'] = 'test_user'
    os.environ['MQTT_PASSWORD'] = 'test_password'
    
    test_reader = TestVictronInit()

def test_without_values():
    """Test without environment variables"""
    logger.info("\n" + "="*60)
    logger.info("TESTING WITHOUT ENVIRONMENT VARIABLES")
    logger.info("="*60)
    
    # Clear environment variables
    for var in ['MPPT_MAC_ADDRESS', 'ENCRYPTION_KEY', 'MQTT_USER', 'MQTT_PASSWORD']:
        if var in os.environ:
            del os.environ[var]
    
    test_reader = TestVictronInit()

if __name__ == "__main__":
    print(f"Test started at: {datetime.now()}")
    
    # Test 1: Without values
    test_without_values()
    
    # Test 2: With sample values  
    test_with_sample_values()
    
    print(f"\nTest completed at: {datetime.now()}")
    print("\nSUMMARY:")
    print("1. MPPT_MAC_ADDRESS is accessed first (line 19 in main.py)")
    print("2. ENCRYPTION_KEY is accessed second (line 20 in main.py)")
    print("3. In connection logic: MAC_ADDRESS is processed first, then used as key for ENCRYPTION_KEY")
    print("4. Order: MAC_ADDRESS → ENCRYPTION_KEY")