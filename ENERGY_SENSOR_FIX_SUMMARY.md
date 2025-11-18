# Energy Balance Sensor Fix Summary

## Issue Identified

The thermal power sensors (`buffer_tank_thermal_power_input` and `dhw_tank_thermal_power_input`) had availability conditions that marked them as **unavailable** when the heat pump was not running:

```yaml
availability: >-
  {{ ... and is_state('binary_sensor.heat_pump_running', 'on') }}
```

### Why This Was a Problem

1. If Home Assistant starts up when the HP is off, these sensors might not get created in the entity registry
2. Integration sensors (`buffer_tank_energy_input`, `dhw_tank_energy_input`) require their source sensors to always be available
3. Utility meters can't track sensors that disappear when HP turns off
4. Energy accumulation would be broken across HP on/off cycles

## Fix Applied

### Changed in `sensors/template/thermal_power_sensors.yaml`

**Before:**
- Availability condition included HP running check
- Sensors became unavailable when HP was off

**After:**
- Availability condition only checks if source sensors exist (temps, flow, G2 position)
- HP running check moved into the state calculation logic
- Sensors now return `0` when HP is off or G2 valve is directing elsewhere
- Sensors remain available at all times

### Code Changes

For both `buffer_tank_thermal_power_input` and `dhw_tank_thermal_power_input`:

1. Removed `and is_state('binary_sensor.heat_pump_running', 'on')` from availability
2. Added HP running check in state template: `{% set hp_running = is_state('binary_sensor.heat_pump_running', 'on') %}`
3. Updated logic: `{% if hp_running and g2_position == 'Buffer Tank' %}`
4. Updated comments to reflect that sensor returns 0 when HP off OR valve directing elsewhere

## Next Steps

### 1. Restart Home Assistant

The sensor definitions have changed, so a full restart is needed:

```bash
# In Home Assistant:
Settings → System → Restart
```

### 2. Verify Sensors Were Created

After restart, check Developer Tools → States for these entities:

**Thermal Power Sensors (should exist and show 0 or a value):**
- `sensor.buffer_tank_thermal_power_input`
- `sensor.dhw_tank_thermal_power_input`

**Integration Sensors (should exist):**
- `sensor.buffer_tank_energy_input`
- `sensor.dhw_tank_energy_input`

**Utility Meters (should exist):**
- `sensor.buffer_tank_energy_input_hourly`
- `sensor.buffer_tank_energy_input_daily`
- `sensor.buffer_tank_energy_input_monthly`
- `sensor.dhw_tank_energy_input_hourly`
- `sensor.dhw_tank_energy_input_daily`
- `sensor.dhw_tank_energy_input_monthly`

### 3. Check Dashboard

The Sensor Verification dashboard should now show the new Energy Balance Tracking section with all sensors visible.

### 4. Allow Data Accumulation

The system needs to run for several hours to accumulate meaningful energy data:

- **Hourly meters**: Wait 1-2 hours
- **Daily meters**: Wait 24 hours
- **Energy balance analysis**: Wait until you have data from both heating and DHW cycles

## Expected Behavior After Fix

### When HP is OFF
- Thermal power sensors: Available, showing `0 W`
- Integration sensors: Available, not accumulating (no new energy)
- Utility meters: Available, maintaining previous totals

### When HP is ON - Heating Mode (G2 → Buffer)
- `buffer_tank_thermal_power_input`: Shows power value (e.g., 5000 W)
- `dhw_tank_thermal_power_input`: Shows `0 W`
- `buffer_tank_energy_input`: Accumulating
- `dhw_tank_energy_input`: Not accumulating

### When HP is ON - DHW Mode (G2 → DHW)
- `buffer_tank_thermal_power_input`: Shows `0 W`
- `dhw_tank_thermal_power_input`: Shows power value (e.g., 6000 W)
- `buffer_tank_energy_input`: Not accumulating
- `dhw_tank_energy_input`: Accumulating

## Validation

Once data has accumulated, check the Energy Balance Analysis in the dashboard:

```
HP Thermal Output (Daily) = Buffer Input (Daily) + DHW Input (Daily) + Piping Losses
```

**Expected piping losses:** 5-10% of HP output
**⚠️ If losses > 10%:** May indicate insulation issues or sensor calibration problems

## Commit Details

**Branch:** `claude/fix-energy-sensors-01MPVDgqCffnuW1bmq31LWs3`
**Commit:** 618a470
**Files Changed:** `sensors/template/thermal_power_sensors.yaml`

---

## Troubleshooting

### If sensors still don't appear after restart:

1. Check Home Assistant logs for errors:
   - Settings → System → Logs
   - Search for "thermal_power" or "buffer_tank"

2. Verify source sensors exist:
   - `sensor.supply_from_heat_pump` (or `sensor.buffer_supply_from_heat_pump`)
   - `sensor.buffer_return_to_heat_pump`
   - `sensor.dhw_supply_from_heat_pump`
   - `sensor.dhw_return_to_heat_pump`
   - `sensor.cx50_pump_flow_lpm`
   - `sensor.g2_valve_position`

3. If `sensor.supply_from_heat_pump` doesn't exist, see SENSOR_DIAGNOSTIC.md

### Known Issue: HVAC Flow Rate Reading 0.0 LPM

Separately from the energy balance sensors, the HVAC flow sensor is reading 0.0 LPM even when zones are calling for heat. This blocks distribution efficiency calculations and needs investigation:

- Source sensor: `sensor.hydronic_flow_flow_rate`
- Wrapper: `sensor.hvac_buffer_tank_flow_rate`
- Used by: `sensor.hvac_thermal_power_used`

This is a separate issue from the energy balance tracking fix.
