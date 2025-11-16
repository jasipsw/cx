"""
Home Assistant Python Script to map device names to IP addresses.

This script extracts IP addresses from devices (primarily Leviton switches)
and creates a mapping file that can be used to name devices in your network.

Usage:
  1. Enable python_script in configuration.yaml:
     python_script:

  2. Restart Home Assistant

  3. Call from Developer Tools > Services:
     Service: python_script.map_switch_ips
     Service Data: {}

The script will create a file at /config/www/switch_ip_mapping.txt
You can access it at: http://your-ha-url:8123/local/switch_ip_mapping.txt
"""

import re
from datetime import datetime

# Get device registry
device_registry = hass.data.get("device_registry")
if not device_registry:
    logger.error("Could not access device registry")
    hass.services.call(
        "persistent_notification",
        "create",
        {
            "title": "Switch IP Mapping Error",
            "message": "Could not access device registry",
        },
    )
else:
    devices = device_registry.devices

    # Collect device information
    device_info_list = []

    for device_id, device in devices.items():
        # Get device name
        name = device.name_by_user or device.name or "Unknown"

        # Skip devices without names or that don't look like switches/lights
        if name == "Unknown":
            continue

        # Extract IP address from configuration_url
        ip_address = None
        config_url = device.configuration_url
        if config_url:
            # Try to extract IP from URL
            ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', config_url)
            if ip_match:
                ip_address = ip_match.group(1)

        # Get MAC address from connections
        mac_address = None
        for conn_type, conn_value in device.connections:
            if conn_type == "mac":
                mac_address = conn_value
                break

        # Get manufacturer and model
        manufacturer = device.manufacturer or "Unknown"
        model = device.model or "Unknown"

        # Check if this is likely a Leviton device or has an IP
        is_leviton = "leviton" in manufacturer.lower()
        is_matter = any("matter" in str(entry) for entry in device.config_entries)

        # Only include devices that have IP addresses or are Leviton/Matter devices
        if ip_address or is_leviton or (is_matter and ("light" in name.lower() or "switch" in name.lower())):
            device_info_list.append({
                "name": name,
                "ip": ip_address or "Not found",
                "mac": mac_address or "Not found",
                "manufacturer": manufacturer,
                "model": model,
                "config_url": config_url or "Not found",
                "is_leviton": is_leviton,
                "is_matter": is_matter,
            })

    # Sort by name
    device_info_list.sort(key=lambda x: x["name"])

    # Create output content
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append("DEVICE TO IP ADDRESS MAPPING")
    output_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output_lines.append("=" * 80)
    output_lines.append("")

    if not device_info_list:
        output_lines.append("No devices found with IP addresses.")
        output_lines.append("")
        output_lines.append("This could mean:")
        output_lines.append("  1. Devices don't expose configuration URLs with IPs")
        output_lines.append("  2. No Leviton or Matter light/switch devices found")
        output_lines.append("  3. Devices need to be configured differently")
    else:
        # Group by type
        leviton_devices = [d for d in device_info_list if d["is_leviton"]]
        matter_devices = [d for d in device_info_list if d["is_matter"] and not d["is_leviton"]]
        other_devices = [d for d in device_info_list if not d["is_leviton"] and not d["is_matter"]]

        # Output Leviton devices
        if leviton_devices:
            output_lines.append("LEVITON DEVICES")
            output_lines.append("-" * 80)
            for dev in leviton_devices:
                output_lines.append(f"\n{dev['name']}")
                output_lines.append(f"  IP Address:   {dev['ip']}")
                output_lines.append(f"  MAC Address:  {dev['mac']}")
                output_lines.append(f"  Manufacturer: {dev['manufacturer']}")
                output_lines.append(f"  Model:        {dev['model']}")
                output_lines.append(f"  Config URL:   {dev['config_url']}")
            output_lines.append("")

        # Output Matter devices
        if matter_devices:
            output_lines.append("\nMATTER DEVICES (Lights/Switches)")
            output_lines.append("-" * 80)
            for dev in matter_devices:
                output_lines.append(f"\n{dev['name']}")
                output_lines.append(f"  IP Address:   {dev['ip']}")
                output_lines.append(f"  MAC Address:  {dev['mac']}")
                output_lines.append(f"  Manufacturer: {dev['manufacturer']}")
                output_lines.append(f"  Model:        {dev['model']}")
                output_lines.append(f"  Config URL:   {dev['config_url']}")
            output_lines.append("")

        # Output other devices with IPs
        if other_devices:
            output_lines.append("\nOTHER DEVICES")
            output_lines.append("-" * 80)
            for dev in other_devices:
                output_lines.append(f"\n{dev['name']}")
                output_lines.append(f"  IP Address:   {dev['ip']}")
                output_lines.append(f"  MAC Address:  {dev['mac']}")
                output_lines.append(f"  Manufacturer: {dev['manufacturer']}")
                output_lines.append(f"  Model:        {dev['model']}")
                output_lines.append(f"  Config URL:   {dev['config_url']}")
            output_lines.append("")

        # Add summary
        output_lines.append("")
        output_lines.append("=" * 80)
        output_lines.append("SUMMARY")
        output_lines.append("=" * 80)
        output_lines.append(f"Total Leviton devices: {len(leviton_devices)}")
        output_lines.append(f"Total Matter devices:  {len(matter_devices)}")
        output_lines.append(f"Total other devices:   {len(other_devices)}")
        output_lines.append(f"Devices with IPs:      {len([d for d in device_info_list if d['ip'] != 'Not found'])}")
        output_lines.append("")

        # Add CSV format for easy import
        output_lines.append("")
        output_lines.append("=" * 80)
        output_lines.append("CSV FORMAT (for import to network management)")
        output_lines.append("=" * 80)
        output_lines.append("Name,IP Address,MAC Address,Manufacturer,Model")
        for dev in device_info_list:
            output_lines.append(f'"{dev["name"]}",{dev["ip"]},{dev["mac"]},"{dev["manufacturer"]}","{dev["model"]}"')

    output_content = "\n".join(output_lines)

    # Write to www directory (accessible via web)
    try:
        # Ensure www directory exists
        import os
        www_dir = "/config/www"
        os.makedirs(www_dir, exist_ok=True)

        output_file = os.path.join(www_dir, "switch_ip_mapping.txt")
        with open(output_file, "w") as f:
            f.write(output_content)

        # Also write CSV file
        csv_file = os.path.join(www_dir, "switch_ip_mapping.csv")
        with open(csv_file, "w") as f:
            f.write("Name,IP Address,MAC Address,Manufacturer,Model\n")
            for dev in device_info_list:
                f.write(f'"{dev["name"]}",{dev["ip"]},{dev["mac"]},"{dev["manufacturer"]}","{dev["model"]}"\n')

        # Send notification
        device_count = len(device_info_list)
        ip_count = len([d for d in device_info_list if d["ip"] != "Not found"])

        message = f"""Device mapping complete!

Found {device_count} devices ({ip_count} with IP addresses)

Files created:
- /local/switch_ip_mapping.txt
- /local/switch_ip_mapping.csv

Access at:
- http://YOUR-HA-URL:8123/local/switch_ip_mapping.txt
- http://YOUR-HA-URL:8123/local/switch_ip_mapping.csv

Or check the files in your Home Assistant www folder."""

        hass.services.call(
            "persistent_notification",
            "create",
            {
                "title": "✅ Switch IP Mapping Complete",
                "message": message,
                "notification_id": "switch_ip_mapping_done",
            },
        )

        logger.info(f"Device mapping complete. Found {device_count} devices, {ip_count} with IPs")

    except Exception as e:
        error_msg = f"Error writing output file: {str(e)}"
        logger.error(error_msg)
        hass.services.call(
            "persistent_notification",
            "create",
            {
                "title": "Switch IP Mapping Error",
                "message": error_msg,
            },
        )
