# Finding Matter Device MAC/IP Addresses

This directory contains three different methods to extract MAC addresses and IP addresses from your Leviton Matter switches so you can rename them in your Ubiquiti network.

## Method 1: Template Editor (Easiest - Start Here)

**Best for:** Quick one-time lookup

1. In Home Assistant, go to **Developer Tools → Template**
2. Open the file: `matter_device_network_info.yaml`
3. Copy the entire contents and paste it into the template editor
4. The results will display immediately in a table format
5. Copy the MAC addresses and match them in your UniFi Controller

## Method 2: Python Script (Most Detailed)

**Best for:** Access to device registry details

### Setup:
1. Enable python_script integration by adding this to `configuration.yaml`:
   ```yaml
   python_script:
   ```

2. Copy the script to your Home Assistant config directory:
   ```bash
   cp python_scripts/matter_network_info.py /config/python_scripts/
   ```

3. Restart Home Assistant

### Usage:
1. Go to **Developer Tools → Services**
2. Search for service: `python_script.matter_network_info`
3. Click "Call Service"
4. Check your notifications - a persistent notification will appear with all device information

## Method 3: Shell Script (API Method)

**Best for:** Command-line users or automation

### Setup:
1. Create a Long-Lived Access Token:
   - Go to your HA profile (click your name in sidebar)
   - Scroll to "Long-Lived Access Tokens"
   - Click "Create Token"
   - Copy the token

2. Edit `get_matter_devices.sh`:
   - Update `HA_URL` to your Home Assistant URL
   - Update `HA_TOKEN` with your token

3. Make executable:
   ```bash
   chmod +x scripts/get_matter_devices.sh
   ```

### Usage:
```bash
./scripts/get_matter_devices.sh
```

## What if MAC/IP addresses show as "Unknown"?

Matter devices over WiFi should expose MAC addresses through the `connections` field in the device registry. If they don't appear:

1. **Check individual device details:**
   - Go to Settings → Devices & Services → Matter
   - Click on a specific device
   - Look for any network information in the device details

2. **Use UniFi Controller to identify by activity:**
   - Open UniFi Controller → Clients
   - Filter by "Recently Active"
   - Turn OFF a specific light switch
   - Watch for a device to go offline
   - That's your switch! Note the MAC and turn the light back on

3. **Check by signal strength:**
   - Matter WiFi devices will show signal strength in UniFi
   - Use the physical location to narrow down which MAC belongs to which switch

## Matching in UniFi Controller

Once you have the MAC addresses:

1. Open UniFi Controller web interface
2. Go to **Clients** section
3. Click **Search** and paste a MAC address
4. When you find the device, click it
5. Click the **Settings (gear)** icon
6. Enter a name matching your Home Assistant device name
7. Click **Apply**
8. Repeat for each switch

## Tips

- Take screenshots of the output for reference while you work in UniFi
- Start with switches in known locations (bedroom, kitchen, etc.)
- Name them consistently: "Leviton - [Room] - [Location]"
- The physical location in HA should match the signal strength/AP in UniFi

## Troubleshooting

**Template method returns empty table:**
- Check if manufacturer contains "Leviton" - the filter looks for this string
- Try removing the manufacturer filter to see ALL light entities

**Python script doesn't work:**
- Make sure `python_script:` is in configuration.yaml
- Check Home Assistant logs for errors
- Ensure the file is in the correct directory

**Shell script fails:**
- Verify your HA_URL is correct (include http:// or https://)
- Verify your token is valid and properly copied
- Install `jq` if not available: `apt-get install jq`
