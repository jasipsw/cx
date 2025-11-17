"""
Matter Device Network Information Extractor
This script queries all Matter devices and extracts MAC/IP addresses

Usage:
1. Copy this file to: config/python_scripts/matter_network_info.py
2. Enable python_script integration in configuration.yaml:
   python_script:
3. Restart Home Assistant
4. Call service: python_script.matter_network_info
5. Check the persistent notification for results
"""

# Get device registry
device_registry = hass.helpers.device_registry.async_get(hass)
entity_registry = hass.helpers.entity_registry.async_get(hass)

results = []

# Iterate through all devices
for device in device_registry.devices.values():
    # Check if device is Matter/Leviton
    manufacturer = device.manufacturer or ""
    if 'leviton' in manufacturer.lower() or 'matter' in manufacturer.lower():

        # Get entities for this device
        entities = entity_registry.entities.get_entries_for_device_id(device.id)
        light_entities = [e.entity_id for e in entities if e.entity_id.startswith('light.')]

        # Try to extract network info from identifiers
        mac_address = "Unknown"
        ip_address = "Unknown"

        # Check identifiers for MAC
        for identifier_type, identifier_value in device.identifiers:
            if 'mac' in str(identifier_type).lower():
                mac_address = identifier_value
            elif 'ip' in str(identifier_type).lower():
                ip_address = identifier_value

        # Check connections for MAC
        for connection_type, connection_value in device.connections:
            if connection_type == 'mac':
                mac_address = connection_value
            elif connection_type == 'ip':
                ip_address = connection_value

        # Store result
        results.append({
            'name': device.name,
            'manufacturer': manufacturer,
            'model': device.model or "Unknown",
            'mac': mac_address,
            'ip': ip_address,
            'entities': ', '.join(light_entities[:3]),  # First 3 entities
            'device_id': device.id
        })

# Format results as markdown table
output = "# Matter/Leviton Switches Network Info\n\n"
output += "| Device Name | Manufacturer | Model | MAC Address | IP Address | Entities |\n"
output += "|------------|-------------|-------|-------------|------------|----------|\n"

for device in results:
    output += f"| {device['name']} | {device['manufacturer']} | {device['model']} | "
    output += f"{device['mac']} | {device['ip']} | {device['entities']} |\n"

output += f"\n**Total Devices:** {len(results)}\n\n"
output += "**Instructions:**\n"
output += "1. Match MAC addresses with devices in UniFi Controller\n"
output += "2. Rename clients in UniFi to match device names\n"

# Create persistent notification
hass.services.call('persistent_notification', 'create', {
    'title': 'Matter Device Network Information',
    'message': output,
    'notification_id': 'matter_network_info'
})

logger.info(f"Found {len(results)} Matter/Leviton devices")
