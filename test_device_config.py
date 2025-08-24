#!/usr/bin/env python
"""
Test script to understand proper MAC address and encryption key configuration
for Victron device discovery
"""
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_mac_address_formats():
    """Test different MAC address formats and how they're processed"""
    
    test_cases = [
        # Common MAC address formats
        "AABBCCDDEEFF",           # No separators (12 hex chars)
        "AA:BB:CC:DD:EE:FF",     # Colon separated
        "AA-BB-CC-DD-EE-FF",     # Dash separated  
        "aa:bb:cc:dd:ee:ff",     # Lowercase with colons
        "aabbccddeeff",           # Lowercase no separators
    ]
    
    logger.info("=== Testing MAC Address Format Processing ===")
    
    for i, mac_input in enumerate(test_cases, 1):
        logger.info(f"\nTest {i}: Input MAC = '{mac_input}'")
        
        try:
            # Simulate the normalization from main.py:35
            # Remove any existing separators first
            clean_mac = mac_input.replace(':', '').replace('-', '')
            
            # Add colons every 2 characters and convert to lowercase
            normalized_mac = ':'.join(clean_mac[i:i+2] for i in range(0, len(clean_mac), 2)).lower()
            logger.info(f"         Normalized = '{normalized_mac}'")
            
            # Show how it would be used in device_keys
            encryption_key = "your_encryption_key_here"
            device_keys = {normalized_mac: encryption_key}
            logger.info(f"         Device keys = {device_keys}")
            
        except Exception as e:
            logger.error(f"         Error processing: {e}")

def test_device_matching():
    """Test how device matching works in the discovery process"""
    
    logger.info("\n" + "="*60)
    logger.info("TESTING DEVICE MATCHING LOGIC")
    logger.info("="*60)
    
    # Simulate discovered device addresses (what comes from BLE scan)
    discovered_devices = [
        "AA:BB:CC:DD:EE:FF",  # Standard BLE format
        "aa:bb:cc:dd:ee:ff",  # Lowercase
        "AA-BB-CC-DD-EE-FF",  # Some devices might use dashes
    ]
    
    # Your configured MAC address (environment variable)
    configured_macs = [
        "AABBCCDDEEFF",           # No separators
        "AA:BB:CC:DD:EE:FF",     # With colons
        "aa:bb:cc:dd:ee:ff",     # Lowercase with colons
    ]
    
    for discovered in discovered_devices:
        logger.info(f"\nDiscovered device: {discovered}")
        
        for configured in configured_macs:
            logger.info(f"  Testing against configured: {configured}")
            
            # Simulate the matching logic from main.py:46-47
            device_mac = discovered.replace(':', '').lower()
            target_mac = configured.replace(':', '').lower()
            
            match = device_mac == target_mac
            logger.info(f"    Device MAC normalized: {device_mac}")
            logger.info(f"    Target MAC normalized: {target_mac}")
            logger.info(f"    Match: {match}")

def show_recommended_config():
    """Show the recommended configuration format"""
    
    logger.info("\n" + "="*60)
    logger.info("RECOMMENDED CONFIGURATION")
    logger.info("="*60)
    
    logger.info("\nFor your .env file or environment variables:")
    logger.info("MPPT_MAC_ADDRESS=AA:BB:CC:DD:EE:FF    # Use colon-separated format")
    logger.info("ENCRYPTION_KEY=your_32_char_hex_key    # Your device's encryption key")
    
    logger.info("\nAlternative formats that will work:")
    logger.info("MPPT_MAC_ADDRESS=AABBCCDDEEFF          # No separators")
    logger.info("MPPT_MAC_ADDRESS=aa:bb:cc:dd:ee:ff     # Lowercase with colons")
    
    logger.info("\nHow to find your device's MAC and encryption key:")
    logger.info("1. MAC Address: Use 'bluetoothctl' or a BLE scanner app")
    logger.info("2. Encryption Key: Found in VictronConnect app settings")
    logger.info("   - Open VictronConnect")
    logger.info("   - Connect to your MPPT")
    logger.info("   - Go to Settings > Product Info > Instant readout via Bluetooth")
    logger.info("   - The key is shown as a 32-character hex string")

def simulate_scanner_setup():
    """Simulate how the Scanner expects the device_keys format"""
    
    logger.info("\n" + "="*60)
    logger.info("SCANNER DEVICE_KEYS FORMAT")
    logger.info("="*60)
    
    # Example configuration
    mac_address = "AA:BB:CC:DD:EE:FF"  # Your MPPT MAC
    encryption_key = "0123456789abcdef0123456789abcdef"  # Your encryption key
    
    logger.info(f"Your configuration:")
    logger.info(f"MPPT_MAC_ADDRESS = {mac_address}")
    logger.info(f"ENCRYPTION_KEY = {encryption_key}")
    
    # Show the processing
    logger.info(f"\nProcessing for Scanner:")
    normalized_mac = ':'.join(mac_address.replace(':', '').replace('-', '')[i:i+2] for i in range(0, len(mac_address.replace(':', '').replace('-', '')), 2)).lower()
    logger.info(f"1. Normalized MAC = {normalized_mac}")
    
    device_keys = {normalized_mac: encryption_key}
    logger.info(f"2. Device keys for Scanner = {device_keys}")
    logger.info(f"3. Scanner(device_keys) expects exactly this format")

if __name__ == "__main__":
    test_mac_address_formats()
    test_device_matching() 
    show_recommended_config()
    simulate_scanner_setup()