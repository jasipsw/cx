# Matter Device to IP Address Mapping

This script helps map Matter device names to their IP addresses by correlating data from the Leviton WiFi integration.

## Overview

When you have Matter devices (like Leviton smart switches) controlled through Home Assistant, the Matter integration doesn't directly expose the IP addresses. However, if you also have the Leviton WiFi integration configured, it may have this information. This script:

1. Queries the Home Assistant API to get all devices
2. Identifies devices from the Matter integration
3. Identifies devices from the Leviton WiFi integration
4. Maps devices based on name similarity
5. Extracts IP addresses, MAC addresses, and configuration URLs from the Leviton devices
6. Outputs a mapping you can use to name devices in your Ubiquiti network settings

## Prerequisites

1. **Home Assistant Long-Lived Access Token**
   - Go to your Home Assistant profile
   - Navigate to: Profile → Security → Long-Lived Access Tokens
   - Click "Create Token"
   - Give it a name (e.g., "Device Mapping Script")
   - Copy the token (you won't be able to see it again!)

2. **Python 3 with requests library**
   ```bash
   pip3 install requests
   ```

3. **Both integrations configured**
   - Matter integration with your Leviton switches
   - Leviton WiFi integration with the same switches

## Usage

### Step 1: Set environment variables

```bash
export HA_URL='https://your-homeassistant-url:443'
export HA_TOKEN='your-long-lived-access-token'
```

**Note:** Replace `your-homeassistant-url` with your actual Home Assistant URL. Examples:
- `https://homeassistant.local:443`
- `https://192.168.1.100:443`
- `https://your-domain.duckdns.org:443`

### Step 2: Run the script

```bash
cd /home/user/cx/scripts
python3 map_matter_to_ip.py
```

### Step 3: Review the output

The script will:
- Print a list of Matter devices mapped to their IP addresses
- Save the mapping to `matter_to_ip_mapping.json`

Example output:
```
================================================================================
MATTER DEVICE TO IP ADDRESS MAPPING
================================================================================

Kitchen Lights
  Leviton Name: Kitchen Lights
  IP Address:   192.168.1.50
  MAC Address:  AA:BB:CC:DD:EE:FF
  Config URL:   http://192.168.1.50
  Match Score:  100.00%

Living Room Switch
  Leviton Name: Living Room Light Switch
  IP Address:   192.168.1.51
  MAC Address:  11:22:33:44:55:66
  Config URL:   http://192.168.1.51
  Match Score:  85.50%
```

## Troubleshooting

### No matches found

If the script reports "No matches found," this could mean:

1. **Device names don't match closely enough**
   - The script uses fuzzy string matching (60% similarity threshold)
   - Try renaming devices in one integration to match the other more closely

2. **Integration detection issue**
   - The script looks for 'matter' and 'leviton' in device metadata
   - You may need to adjust the detection logic if your setup differs

3. **IP address not available**
   - The Leviton integration may not expose IP addresses in the expected way
   - Check if the integration provides a `configuration_url` field

### Debugging

To see all devices and their raw data, you can modify the script to print debug information. Add this after `mapper.load_data()`:

```python
# Debug: Print all Matter devices
print("\n=== MATTER DEVICES ===")
for dev in mapper.get_matter_devices():
    print(json.dumps(mapper.get_device_info(dev), indent=2))

# Debug: Print all Leviton devices
print("\n=== LEVITON DEVICES ===")
for dev in mapper.get_leviton_devices():
    print(json.dumps(mapper.get_device_info(dev), indent=2))
```

### Alternative: Direct API inspection

If the script doesn't work as expected, you can manually inspect the API responses:

```bash
# Get all devices
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  https://your-ha-url/api/config/device_registry/list \
  | python3 -m json.tool > all_devices.json

# Get all entities
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  https://your-ha-url/api/config/entity_registry/list \
  | python3 -m json.tool > all_entities.json
```

Then search through `all_devices.json` for your Leviton devices and look for IP-related fields.

## Using the Results

Once you have the IP-to-device mapping:

1. **In Ubiquiti Network Controller:**
   - Go to Clients
   - Find the client by IP or MAC address
   - Click on the client
   - Set the alias/name to match your Home Assistant device name

2. **Alternative: DHCP Reservations**
   - Create DHCP reservations for each device's MAC address
   - Assign the same IP address it currently has
   - Set the hostname to match the Home Assistant device name

3. **DNS Records (Optional)**
   - Create local DNS records for each device
   - Makes it easier to access devices by name

## Notes

- The script uses fuzzy string matching, so device names don't need to match exactly
- A match score above 60% is considered valid (adjust in the code if needed)
- The script disables SSL verification for self-signed certificates
- Results are saved to `matter_to_ip_mapping.json` for easy reference
