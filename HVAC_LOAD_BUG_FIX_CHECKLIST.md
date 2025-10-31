# HVAC Load Bug Fix - Diagnostic Checklist

## Issue Fixed: Fahrenheit/Celsius Temperature Unit Bug
**Date:** 2025-10-31
**Commit:** 34ea9d0

---

## What Was Wrong

The `sensor.hvac_thermal_power_used` was calculating thermal power using:
- **Temperature delta in Fahrenheit** (18°F for a 10°C difference)
- **Formula expecting Celsius** (Q = ṁ × Cp × ΔT requires Celsius)
- **Result:** 1.8x overcalculation (80% too high)

---

## Post-Restart Checklist

### ✅ Step 1: Verify New Sensors Exist
Navigate to: **Developer Tools → States**

Search for and verify these new sensors exist:
- [ ] `sensor.hvac_buffer_tank_delta_t_celsius` (NEW)
- [ ] `sensor.system_distribution_losses` (NEW)
- [ ] `sensor.system_distribution_efficiency` (NEW)
- [ ] `sensor.system_loss_analysis` (NEW)

---

### ✅ Step 2: Check Instantaneous Values (While Heat Pump Running)

Wait for heat pump to be actively running (>500W), then check:

| Sensor | Expected Range | Your Value | Status |
|--------|----------------|------------|--------|
| `sensor.heat_pump_thermal_power_output` | 2,000-8,000 W | _______ W | ☐ OK |
| `sensor.hvac_thermal_power_used` | 1,600-7,500 W | _______ W | ☐ OK |
| `sensor.system_distribution_efficiency` | 80-95% | _______ % | ☐ OK |
| `sensor.system_distribution_losses` | 200-1,000 W | _______ W | ☐ OK |

**Critical Test:** HVAC load should be LESS than HP output
- HP Output: _______ W
- HVAC Load: _______ W
- HVAC < HP? ☐ YES ☐ NO

If NO, continue to Step 3.

---

### ✅ Step 3: Verify Temperature Sensors

| Sensor | Expected | Your Value | Unit | Status |
|--------|----------|------------|------|--------|
| `sensor.heat_pump_outlet_temperature` | 80-120°F | _______ °F | Fahrenheit | ☐ OK |
| `sensor.hvac_buffer_tank_supply_temperature` | 80-120°F | _______ °F | Fahrenheit | ☐ OK |
| `sensor.heat_pump_delta_t` | 5-12°F | _______ °F | Fahrenheit | ☐ OK |
| `sensor.hvac_buffer_tank_delta_t` | 5-12°F | _______ °F | Fahrenheit | ☐ OK |
| `sensor.hvac_buffer_tank_delta_t_celsius` | 3-7°C | _______ °C | **Celsius** | ☐ OK |

**Test:** Delta T in Celsius should be ~55% of Delta T in Fahrenheit
- Delta T (°F): _______ °F
- Delta T (°C): _______ °C
- Ratio: _______ (should be ~0.55)

---

### ✅ Step 4: Compare Flow Sensors

| Sensor | Expected Range | Your Value | Status |
|--------|----------------|------------|--------|
| `sensor.cx50_pump_flow_lpm` | 10-40 LPM | _______ LPM | ☐ OK |
| `sensor.hydronic_flow_flow_rate` | 10-40 LPM | _______ LPM | ☐ OK |

**Test:** Flow sensors should be within 20% of each other
- HP Flow: _______ LPM
- Buffer Flow: _______ LPM
- Difference: _______ % (should be <20%)

If difference >20%, investigate which sensor is correct.

---

### ✅ Step 5: View Dashboard

Navigate to: **Energy Analysis → Technical Details**

Find the card: **System Distribution Analysis**

Screenshot or note:
- System Efficiency: _______ %
- Distribution Losses: _______ W
- Status: _______________________

---

## Expected Results After Fix

### Before Fix (OLD - WRONG):
```
Example scenario:
- HP Delta T: 10°C
- Buffer Delta T: 18°F (same 10°C difference)
- Bug: HVAC calc used 18 instead of 10
- HVAC Power = 1.8x too high
```

### After Fix (NEW - CORRECT):
```
Example scenario:
- HP Delta T: 10°C
- Buffer Delta T: 10°C (from NEW celsius sensor)
- Both use 10°C in calculation
- HVAC Power = correct value
```

**Expected change:**
- HVAC Thermal Power Used should **decrease by ~44%**
- System efficiency should show **80-95%** (realistic)
- HVAC load should **never exceed** HP output

---

## If Problem Persists

If HVAC load is still higher than HP output after fix:

### Check 1: Source Sensors
```bash
# In Home Assistant, check these Shelly sensor values:
sensor.shellyplus1_c4d8d5543fc0_temperature        (supply, in Celsius)
sensor.shellyplus1_c4d8d5543fc0_temperature_3      (return, in Celsius)

# Verify they're in Celsius (typically 35-50°C range when running)
# If showing 90-120, they might already be in Fahrenheit (would need different fix)
```

### Check 2: Flow Sensor Accuracy
```bash
# Compare flow readings:
sensor.cx50_pump_flow_lpm           (from heat pump Modbus)
sensor.hydronic_flow_flow_rate      (from separate flow meter)

# If one is 5-10x different, that sensor is faulty
```

### Check 3: Sensor History Gaps
```bash
# In History view, check both sensors for:
- Frequent "unavailable" or "unknown" states
- Sudden spikes or drops
- Long periods of zero when system was running

# Integration sensors can accumulate errors if source data has gaps
```

---

## Daily Energy Totals Issue

If the **instantaneous power** values look correct but **daily totals** are still off:

### Possible Cause: Integration Sensor Configuration

Check what sensors are feeding your daily energy totals:
1. Find the utility meter or integration sensor source
2. Verify both are using the same integration method
3. Check for different scan intervals or sampling rates

Example issue:
```
CX Thermal Output: Uses integration sensor with 15-second scan interval
HVAC Load:        Uses integration sensor with 60-second scan interval
Result:           Different accumulation rates = different daily totals
```

**Solution:** Ensure both use identical integration methods and scan intervals.

---

## Support

For further troubleshooting:
1. Check logs: Settings → System → Logs
2. Search for: "hvac_thermal_power_used" or "template"
3. Look for template errors or unavailable sensor warnings

Document your findings and we can investigate further!

---

## Summary

**Most Likely Outcome:**
✅ HVAC load drops to 80-95% of HP output
✅ System efficiency shows realistic 85-92%
✅ Daily totals now match within 10-15%

**If Still Wrong:**
- Flow sensor discrepancy (check Step 4)
- Shelly sensors reporting wrong units (check Shelly device settings)
- Integration method mismatch (for daily totals)
