#!/bin/bash
# Matter Device Network Information Extractor
# This script queries Home Assistant API for Matter device information

# Configuration - Update these values
HA_URL="http://homeassistant.local:8123"
HA_TOKEN="YOUR_LONG_LIVED_ACCESS_TOKEN_HERE"

echo "========================================="
echo "Matter/Leviton Device Network Information"
echo "========================================="
echo ""

# Get all devices from device registry
curl -s -X GET \
  -H "Authorization: Bearer ${HA_TOKEN}" \
  -H "Content-Type: application/json" \
  "${HA_URL}/api/config/device_registry/list" | \
  jq -r '.[] | select(.manufacturer | ascii_downcase | contains("leviton") or contains("matter")) |
  {
    name: .name,
    manufacturer: .manufacturer,
    model: .model,
    mac: (.connections[] | select(.[0] == "mac") | .[1]),
    ip: (.connections[] | select(.[0] == "ip") | .[1]),
    id: .id
  } |
  [.name, .manufacturer, .model, .mac // "Unknown", .ip // "Unknown"] |
  @tsv' | \
  column -t -s $'\t' -N "DEVICE NAME,MANUFACTURER,MODEL,MAC ADDRESS,IP ADDRESS"

echo ""
echo "========================================="
echo "Next Steps:"
echo "1. Copy MAC addresses from above"
echo "2. Open UniFi Controller → Clients"
echo "3. Search for each MAC address"
echo "4. Rename client to match device name"
echo "========================================="
