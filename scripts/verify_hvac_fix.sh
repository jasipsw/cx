#!/bin/bash
# Quick verification script for HVAC thermal power fix
# Checks if Celsius temperature fix eliminated 11x overcalculation

echo "=========================================="
echo "HVAC Load Bug Fix - Quick Verification"
echo "=========================================="
echo ""

# Check if fix is in production config
echo "1. Checking if fix is applied in production..."
if grep -q "delta_t_c = supply_c - return_c" /root/config/sensors/template/hvac-sensors.yaml 2>/dev/null; then
    echo "   ✅ Fix IS applied in /root/config"
elif grep -q "delta_t_c = supply_c - return_c" /home/user/cx/sensors/template/hvac-sensors.yaml 2>/dev/null; then
    echo "   ⚠️  Fix found in /home/user/cx but NOT in /root/config (production)"
    echo "   Action needed: Copy fix to /root/config and restart Home Assistant"
else
    echo "   ❌ Fix NOT found in either location"
    echo "   Action needed: Apply fix from git and restart Home Assistant"
fi
echo ""

# Instructions for manual verification
echo "2. Manual verification steps:"
echo ""
echo "   Go to Home Assistant → Developer Tools → States"
echo ""
echo "   When heat pump is RUNNING (check that power input >500W):"
echo ""
echo "   ┌─────────────────────────────────────────────────────────┐"
echo "   │ Find these two sensors and note their values:          │"
echo "   │                                                         │"
echo "   │ sensor.heat_pump_thermal_power_output    = _____ W     │"
echo "   │ sensor.hvac_thermal_power_used           = _____ W     │"
echo "   │                                                         │"
echo "   │ Calculate: HVAC ÷ Heat Pump = _____                    │"
echo "   │                                                         │"
echo "   │ Expected results:                                       │"
echo "   │  • Ratio 0.80-0.95: ✅ FIX WORKED!                     │"
echo "   │  • Ratio 2.0-11.0:  ❌ Fix not working yet             │"
echo "   └─────────────────────────────────────────────────────────┘"
echo ""

echo "3. Or check system efficiency sensor directly:"
echo ""
echo "   Search for: sensor.system_distribution_efficiency"
echo ""
echo "   Expected: 80-95%"
echo "   If >100%: Fix not working yet"
echo ""

echo "=========================================="
echo "Need help? See: VERIFICATION_RESULTS.md"
echo "=========================================="
