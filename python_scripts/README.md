# Home Assistant Python Script: Device IP Mapping

This script runs directly within Home Assistant and creates a mapping of your devices (especially Leviton switches) to their IP addresses and MAC addresses.

## Features

- Runs entirely within Home Assistant - no external tools needed
- Automatically extracts IP addresses from device configuration URLs
- Finds MAC addresses from device connections
- Identifies Leviton and Matter devices
- Creates both text and CSV output files
- Accessible via web browser
- Sends notification when complete

## Setup

### Step 1: Enable Python Scripts

The `python_script` integration has already been added to your `configuration.yaml`:

```yaml
# Enable Python scripts
python_script:
```

### Step 2: Restart Home Assistant

After adding the python_script configuration, restart Home Assistant:
- Go to **Settings** → **System** → **Restart**
- Or use Developer Tools → YAML → Restart

### Step 3: Verify Installation

1. Go to **Developer Tools** → **Services**
2. Search for "python_script"
3. You should see `python_script.map_switch_ips` in the list

## Usage

### Method 1: Run from Developer Tools (Recommended)

1. Go to **Developer Tools** → **Services**
2. Search for and select: `python_script.map_switch_ips`
3. Leave Service Data empty: `{}`
4. Click **CALL SERVICE**
5. Wait a few seconds for the notification

### Method 2: Create a Button/Script

Add this to your `scripts.yaml`:

```yaml
map_device_ips:
  alias: "Map Device IPs"
  sequence:
    - service: python_script.map_switch_ips
      data: {}
  mode: single
  icon: mdi:ip-network
```

Then you can:
- Call it from Developer Tools → Services → `script.map_device_ips`
- Add a button to your dashboard
- Trigger it from an automation

### Method 3: Dashboard Button

Add to your Lovelace dashboard:

```yaml
type: button
name: Map Switch IPs
icon: mdi:ip-network
tap_action:
  action: call-service
  service: python_script.map_switch_ips
  data: {}
```

## Accessing Results

After running the script, you'll get a notification with links. The script creates two files:

### Text File (Human Readable)
- **Local path**: `/config/www/switch_ip_mapping.txt`
- **Web URL**: `https://your-ha-url:443/local/switch_ip_mapping.txt`

Example content:
```
================================================================================
DEVICE TO IP ADDRESS MAPPING
Generated: 2024-01-15 10:30:45
================================================================================

LEVITON DEVICES
--------------------------------------------------------------------------------

Kitchen Lights
  IP Address:   192.168.1.50
  MAC Address:  aa:bb:cc:dd:ee:ff
  Manufacturer: Leviton
  Model:        DW6HD-1BZ
  Config URL:   http://192.168.1.50

Living Room Switch
  IP Address:   192.168.1.51
  MAC Address:  11:22:33:44:55:66
  Manufacturer: Leviton
  Model:        DW6HD-1BZ
  Config URL:   http://192.168.1.51
```

### CSV File (Import to Network Tools)
- **Local path**: `/config/www/switch_ip_mapping.csv`
- **Web URL**: `https://your-ha-url:443/local/switch_ip_mapping.csv`

Example content:
```csv
Name,IP Address,MAC Address,Manufacturer,Model
"Kitchen Lights",192.168.1.50,aa:bb:cc:dd:ee:ff,"Leviton","DW6HD-1BZ"
"Living Room Switch",192.168.1.51,11:22:33:44:55:66,"Leviton","DW6HD-1BZ"
```

### Accessing Files

#### Option 1: Web Browser
Replace `your-ha-url` with your actual Home Assistant URL:
- `https://homeassistant.local:443/local/switch_ip_mapping.txt`
- `https://192.168.1.100:443/local/switch_ip_mapping.txt`

#### Option 2: File Browser
If you have File Editor or SSH access:
- Navigate to `/config/www/`
- Open `switch_ip_mapping.txt` or `switch_ip_mapping.csv`

#### Option 3: Download
Right-click the web URL and select "Save As" to download the file

## Using Results in Ubiquiti

Once you have the IP/MAC mapping:

### Method 1: Name Clients by IP
1. Open Ubiquiti Network Controller
2. Go to **Clients**
3. Find client by IP address
4. Click the client
5. Set **Alias** to match the Home Assistant device name

### Method 2: DHCP Reservations (Recommended)
1. Open Ubiquiti Network Controller
2. Go to **Settings** → **Networks** → **Edit** your LAN
3. Scroll to **DHCP** → **DHCP Server**
4. Add **Static DHCP Entries**:
   - MAC Address: (from mapping)
   - IP Address: (from mapping)
   - Hostname: (device name from HA)

Benefits:
- Devices keep same IP after restart
- Named in network logs
- Easier to manage firewall rules

### Method 3: DNS Records
1. Go to **Settings** → **Networks**
2. Edit your LAN network
3. Add **DNS** entries under Advanced
4. Map IP to hostname

## Troubleshooting

### No devices found
**Problem**: Script returns "No devices found with IP addresses"

**Solutions**:
1. Make sure Leviton WiFi integration is installed and configured
2. Check that devices have been discovered
3. Verify devices have configuration URLs with IPs

### Script not appearing in Services
**Problem**: `python_script.map_switch_ips` doesn't show in Developer Tools

**Solutions**:
1. Verify `python_script:` is in `configuration.yaml`
2. Restart Home Assistant completely
3. Check Home Assistant logs for python_script errors
4. Ensure the script file is in `/config/python_scripts/` directory

### Permission errors
**Problem**: "Error writing output file"

**Solutions**:
1. Ensure `/config/www/` directory exists
2. Check Home Assistant has write permissions
3. Try creating `/config/www/` manually via File Editor

### IP addresses show "Not found"
**Problem**: Devices are listed but IPs are "Not found"

**Possible reasons**:
1. Leviton integration doesn't expose configuration URLs
2. Devices use a different method to expose IPs
3. Devices are WiFi-based but don't report their IP to HA

**Debug steps**:
1. Go to **Settings** → **Devices & Services**
2. Click on a Leviton device
3. Check if there's a configuration URL or IP field
4. If not, the integration may not expose this info

### Can't access web URL
**Problem**: Can't open `https://your-ha-url/local/switch_ip_mapping.txt`

**Solutions**:
1. Replace `your-ha-url` with your actual HA address
2. Make sure you're using the correct port (443 in your case)
3. Try accessing from same network as HA first
4. Check if HTTPS is working correctly
5. Try downloading via File Editor instead

## Script Details

### What it does
1. Accesses the device registry in Home Assistant
2. Iterates through all registered devices
3. Filters for devices that are:
   - Leviton devices
   - Matter lights/switches
   - Any device with a configuration URL containing an IP
4. Extracts:
   - Device name (user-assigned or default)
   - IP address from configuration URL
   - MAC address from device connections
   - Manufacturer and model info
5. Sorts and groups devices by type
6. Writes formatted text and CSV files
7. Sends a notification when complete

### File locations
- **Script**: `/config/python_scripts/map_switch_ips.py`
- **Output text**: `/config/www/switch_ip_mapping.txt`
- **Output CSV**: `/config/www/switch_ip_mapping.csv`

### Supported devices
- Leviton WiFi switches (any model)
- Matter light switches
- Any device with a configuration URL containing an IP address

## Advanced Usage

### Running on Schedule

Create an automation to run daily:

```yaml
automation:
  - alias: "Daily Device IP Mapping"
    trigger:
      - platform: time
        at: "03:00:00"  # Run at 3 AM
    action:
      - service: python_script.map_switch_ips
        data: {}
```

### Notification on Completion

The script automatically creates a persistent notification. To customize:

Edit the `map_switch_ips.py` file and modify the notification section near the end.

### Filtering Different Device Types

To include/exclude different device types, edit the filter logic in `map_switch_ips.py` around this line:

```python
if ip_address or is_leviton or (is_matter and ("light" in name.lower() or "switch" in name.lower())):
```

## Support

If you encounter issues:
1. Check Home Assistant logs: **Settings** → **System** → **Logs**
2. Search for "python_script" or "map_switch_ips" errors
3. Verify all prerequisites are met
4. Try running from Developer Tools first before automation

## Related Files

- Main configuration: `configuration.yaml` (python_script enabled)
- This script: `python_scripts/map_switch_ips.py`
- Alternative external script: `scripts/map_matter_to_ip.py` (requires HA token)
