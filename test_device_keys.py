#!/usr/bin/env python
"""
Test script to determine the correct device_keys format for victron-ble Scanner
"""
import os
import sys
import logging

# Add the venv to path
sys.path.insert(0, '/home/alex/victron/.venv/lib/python3.12/site-packages')

try:
    from victron_ble.scanner import Scanner
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    def test_device_keys_formats():
        """Test different device_keys formats"""
        
        # Your example command format
        cmd_format = "763aeff5-1334-e64a-ab30-a0f478s20fe1@0df4d0395b7d1a876c0c33ecb9e70dcd"
        
        if '@' in cmd_format:
            mac_part, key_part = cmd_format.split('@', 1)
            print(f"Original MAC from command: {mac_part}")
            print(f"Original KEY from command: {key_part}")
            
            # Test different MAC normalizations
            formats_to_test = [
                ("Original with dashes", mac_part),
                ("Dashes to colons", mac_part.replace('-', ':')),
                ("No separators uppercase", mac_part.replace('-', '').upper()),
                ("No separators lowercase", mac_part.replace('-', '').lower()),
                ("Colons lowercase", mac_part.replace('-', ':').lower()),
            ]
            
            print("\nTesting device_keys formats:")
            for desc, mac_format in formats_to_test:
                device_keys = {mac_format: key_part}
                print(f"\n{desc}:")
                print(f"  device_keys = {device_keys}")
                
                try:
                    scanner = Scanner(device_keys)
                    print(f"  ✓ Scanner created successfully")
                    
                    # Check if the scanner has our device
                    print(f"  Scanner.device_keys = {scanner.device_keys}")
                    
                except Exception as e:
                    print(f"  ✗ Error creating scanner: {e}")
    
    def test_current_main_py_format():
        """Test the format currently used in main.py"""
        print("\n" + "="*60)
        print("TESTING CURRENT main.py FORMAT")
        print("="*60)
        
        # Simulate what main.py does
        mac_address = "763aeff5-1334-e64a-ab30-a0f478s20fe1"  # Your MAC
        encryption_key = "0df4d0395b7d1a876c0c33ecb9e70dcd"   # Your key
        
        print(f"Input MAC_ADDRESS: {mac_address}")
        print(f"Input ENCRYPTION_KEY: {encryption_key}")
        
        # main.py normalization (line 35-36)
        try:
            clean_mac = mac_address.replace(':', '').replace('-', '')
            normalized_mac = ':'.join(clean_mac[i:i+2] for i in range(0, len(clean_mac), 2)).lower()
            print(f"main.py normalized MAC: {normalized_mac}")
            
            device_keys = {normalized_mac: encryption_key}
            print(f"main.py device_keys: {device_keys}")
            
            scanner = Scanner(device_keys)
            print("✓ Scanner created with main.py format")
            
        except Exception as e:
            print(f"✗ Error with main.py format: {e}")
    
    def find_correct_format():
        """Try to determine what format works"""
        print("\n" + "="*60)
        print("FINDING CORRECT FORMAT")
        print("="*60)
        
        # Your actual device info
        mac = "763aeff5-1334-e64a-ab30-a0f478s20fe1"
        key = "0df4d0395b7d1a876c0c33ecb9e70dcd"
        
        # Fix the 's' in MAC (should be hex)
        corrected_mac = mac.replace('s', '8')  # Assuming 's' should be '8'
        print(f"Corrected MAC (s->8): {corrected_mac}")
        
        formats = [
            mac,
            corrected_mac,
            mac.replace('-', ':'),
            corrected_mac.replace('-', ':'),
            mac.replace('-', '').lower(),
            corrected_mac.replace('-', '').lower(),
        ]
        
        for test_mac in formats:
            try:
                device_keys = {test_mac: key}
                scanner = Scanner(device_keys)
                print(f"✓ Works: {test_mac}")
            except Exception as e:
                print(f"✗ Failed: {test_mac} - {e}")
    
    if __name__ == "__main__":
        test_device_keys_formats()
        test_current_main_py_format()
        find_correct_format()
        
except ImportError as e:
    print(f"Cannot import victron_ble: {e}")
    print("Run with activated virtual environment")