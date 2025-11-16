#!/usr/bin/env python3
"""
Script to map Matter device names to IP addresses using Leviton WiFi integration data.

This script queries the Home Assistant API to:
1. Get all devices from the Matter integration
2. Get all devices from the Leviton WiFi integration (which includes IP addresses)
3. Map devices between integrations based on name similarity
4. Output a mapping of device names to IP addresses

Usage:
    python3 map_matter_to_ip.py

Requirements:
    - Set HA_URL environment variable (e.g., https://homeassistant.local:443)
    - Set HA_TOKEN environment variable (long-lived access token from HA)
"""

import os
import sys
import json
import requests
from typing import Dict, List, Optional
from urllib.parse import urljoin
from difflib import SequenceMatcher


def similar(a: str, b: str) -> float:
    """Calculate similarity ratio between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


class HomeAssistantClient:
    """Client for interacting with Home Assistant API."""

    def __init__(self, url: str, token: str):
        self.url = url.rstrip('/')
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        # Disable SSL verification warnings if using self-signed cert
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _get(self, endpoint: str) -> dict:
        """Make GET request to HA API."""
        url = urljoin(self.url, endpoint)
        try:
            response = self.session.get(url, verify=False)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error calling {endpoint}: {e}", file=sys.stderr)
            return {}

    def get_devices(self) -> List[dict]:
        """Get all devices from Home Assistant."""
        return self._get('/api/config/device_registry/list') or []

    def get_entities(self) -> List[dict]:
        """Get all entities from Home Assistant."""
        return self._get('/api/config/entity_registry/list') or []

    def get_states(self) -> List[dict]:
        """Get all entity states from Home Assistant."""
        return self._get('/api/states') or []


class DeviceMapper:
    """Maps Matter devices to their IP addresses via Leviton integration."""

    def __init__(self, client: HomeAssistantClient):
        self.client = client
        self.devices = []
        self.entities = []
        self.states = []

    def load_data(self):
        """Load all necessary data from Home Assistant."""
        print("Loading devices from Home Assistant...")
        self.devices = self.client.get_devices()
        print(f"Found {len(self.devices)} devices")

        print("Loading entities from Home Assistant...")
        self.entities = self.client.get_entities()
        print(f"Found {len(self.entities)} entities")

        print("Loading entity states from Home Assistant...")
        self.states = self.client.get_states()
        print(f"Found {len(self.states)} states")

    def get_matter_devices(self) -> List[dict]:
        """Get all devices from Matter integration."""
        matter_devices = []
        for device in self.devices:
            # Check if device is from Matter integration
            for config_entry in device.get('config_entries', []):
                # Get the integration domain for this config entry
                # Matter integration typically uses 'matter' as domain
                if any('matter' in str(v).lower() for v in device.values()):
                    matter_devices.append(device)
                    break
        return matter_devices

    def get_leviton_devices(self) -> List[dict]:
        """Get all devices from Leviton WiFi integration."""
        leviton_devices = []
        for device in self.devices:
            # Check if device is from Leviton integration
            if any('leviton' in str(v).lower() for v in device.values()):
                leviton_devices.append(device)
        return leviton_devices

    def get_device_info(self, device: dict) -> dict:
        """Extract useful information from a device."""
        info = {
            'id': device.get('id'),
            'name': device.get('name', 'Unknown'),
            'name_by_user': device.get('name_by_user'),
            'model': device.get('model'),
            'manufacturer': device.get('manufacturer'),
            'config_entries': device.get('config_entries', []),
        }

        # Try to extract IP address from various fields
        connections = device.get('connections', [])
        for conn_type, conn_value in connections:
            if conn_type == 'mac':
                info['mac'] = conn_value
            elif conn_type == 'upnp':
                info['upnp'] = conn_value

        # Get IP from configuration URL if available
        config_url = device.get('configuration_url')
        if config_url:
            info['config_url'] = config_url
            # Try to extract IP from URL
            import re
            ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', config_url)
            if ip_match:
                info['ip'] = ip_match.group(1)

        return info

    def find_entity_by_device_id(self, device_id: str) -> Optional[dict]:
        """Find an entity belonging to a device."""
        for entity in self.entities:
            if entity.get('device_id') == device_id:
                return entity
        return None

    def get_display_name(self, device_info: dict) -> str:
        """Get the best display name for a device."""
        return device_info.get('name_by_user') or device_info.get('name', 'Unknown')

    def map_devices(self) -> Dict[str, dict]:
        """Map Matter device names to IP addresses."""
        matter_devices = self.get_matter_devices()
        leviton_devices = self.get_leviton_devices()

        print(f"\nFound {len(matter_devices)} Matter devices")
        print(f"Found {len(leviton_devices)} Leviton devices")

        # Extract info from all devices
        matter_info = [self.get_device_info(d) for d in matter_devices]
        leviton_info = [self.get_device_info(d) for d in leviton_devices]

        # Create mapping
        mapping = {}

        for matter_dev in matter_info:
            matter_name = self.get_display_name(matter_dev)

            # Try to find matching Leviton device
            best_match = None
            best_score = 0.0

            for leviton_dev in leviton_info:
                leviton_name = self.get_display_name(leviton_dev)
                score = similar(matter_name, leviton_name)

                if score > best_score:
                    best_score = score
                    best_match = leviton_dev

            # Only consider it a match if similarity is high enough
            if best_match and best_score > 0.6:
                mapping[matter_name] = {
                    'matter_device': matter_dev,
                    'leviton_device': best_match,
                    'leviton_name': self.get_display_name(best_match),
                    'ip': best_match.get('ip', 'Not found'),
                    'mac': best_match.get('mac', 'Not found'),
                    'config_url': best_match.get('config_url', 'Not found'),
                    'similarity_score': best_score,
                }

        return mapping


def main():
    """Main function."""
    # Get configuration from environment
    ha_url = os.environ.get('HA_URL')
    ha_token = os.environ.get('HA_TOKEN')

    if not ha_url:
        print("Error: HA_URL environment variable not set", file=sys.stderr)
        print("Example: export HA_URL='https://homeassistant.local:443'", file=sys.stderr)
        return 1

    if not ha_token:
        print("Error: HA_TOKEN environment variable not set", file=sys.stderr)
        print("Create a long-lived access token in Home Assistant:", file=sys.stderr)
        print("  Profile -> Security -> Long-Lived Access Tokens", file=sys.stderr)
        return 1

    # Create client and mapper
    client = HomeAssistantClient(ha_url, ha_token)
    mapper = DeviceMapper(client)

    # Load data and create mapping
    mapper.load_data()
    mapping = mapper.map_devices()

    # Print results
    print("\n" + "="*80)
    print("MATTER DEVICE TO IP ADDRESS MAPPING")
    print("="*80)

    if not mapping:
        print("\nNo matches found between Matter and Leviton devices.")
        print("This could mean:")
        print("  1. Device names don't match closely enough")
        print("  2. Devices are not from the expected integrations")
        print("  3. Leviton devices don't expose IP addresses in the expected way")
        return 0

    for matter_name, info in sorted(mapping.items()):
        print(f"\n{matter_name}")
        print(f"  Leviton Name: {info['leviton_name']}")
        print(f"  IP Address:   {info['ip']}")
        print(f"  MAC Address:  {info['mac']}")
        print(f"  Config URL:   {info['config_url']}")
        print(f"  Match Score:  {info['similarity_score']:.2%}")

    # Also save to JSON file
    output_file = 'matter_to_ip_mapping.json'
    with open(output_file, 'w') as f:
        # Convert to simpler format for JSON
        simple_mapping = {
            name: {
                'leviton_name': info['leviton_name'],
                'ip': info['ip'],
                'mac': info['mac'],
                'config_url': info['config_url'],
                'match_score': info['similarity_score'],
            }
            for name, info in mapping.items()
        }
        json.dump(simple_mapping, f, indent=2)

    print(f"\n\nMapping saved to: {output_file}")
    print("="*80)

    return 0


if __name__ == '__main__':
    sys.exit(main())
