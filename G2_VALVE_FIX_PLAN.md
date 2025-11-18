# G2 Valve Position Detection - Fix Plan

## Current Status: DISABLED (2025-11-18)

The G2 valve position detection has been temporarily disabled and will return:
- `sensor.g2_valve_position`: "Unknown (Detection Disabled)"
- `binary_sensor.g2_valve_dhw_mode`: "off"

## Why It Was Disabled

1. **DHW thermal power is negative** (-218W)
   - This is physically impossible
   - Indicates DHW supply/return temperature sensors are likely swapped

2. **Trend sensors not working**
   - Buffer supply sensor shows 0°F in G2 detection
   - Neither trend sensor is active when they should be

3. **Sensor naming inconsistencies**
   - Code references `sensor.buffer_supply_from_heat_pump`
   - But actual entity is `sensor.supply_from_heat_pump`

## Impact of Disabling

### ❌ What Doesn't Work Now

1. **Energy Balance Tracking** - Thermal power sensors depend on G2 position:
   - `sensor.buffer_tank_thermal_power_input` will always return 0
   - `sensor.dhw_tank_thermal_power_input` will always return 0
   - Energy accumulation paused until fixed

2. **Mode Classification** - Can't distinguish:
   - Heating mode (G2 → Buffer)
   - DHW mode (G2 → DHW)
   - Heat + DHW mode

3. **Efficiency Analysis** - Can't calculate:
   - Piping losses to each tank
   - Separate COPs for heating vs DHW

### ✅ What Still Works

1. Overall HP performance:
   - Total electrical input tracking
   - Total thermal output tracking
   - Overall COP calculation

2. Buffer tank distribution:
   - HVAC thermal power
   - Distribution efficiency

## Fix Plan - Step by Step

### Phase 1: Diagnose DHW Sensor Swap

**Action Required:**
Check current temperature readings in Developer Tools → States:

```
sensor.dhw_supply_from_heat_pump = ???°F
sensor.dhw_return_to_heat_pump = ???°F
```

**Expected:**
- Supply (from HP to tank) should be HOTTER
- Return (from tank to HP) should be COOLER

**If supply < return:**
The physical sensors are swapped and need to be either:
1. Re-labeled in the code, OR
2. Physically swapped at the hardware level

### Phase 2: Fix DHW Sensor Definitions

**If sensors are swapped in code:**

Edit `sensors/template/thermal_power_sensors.yaml` (around line 109):

```yaml
# SWAP THESE TWO LINES:
{% set supply_val = states('sensor.dhw_supply_from_heat_pump') | float(0) %}
{% set return_val = states('sensor.dhw_return_to_heat_pump') | float(0) %}

# TO:
{% set supply_val = states('sensor.dhw_return_to_heat_pump') | float(0) %}
{% set return_val = states('sensor.dhw_supply_from_heat_pump') | float(0) %}
```

OR update the sensor wrapper definitions to fix the naming.

### Phase 3: Fix Buffer Supply Sensor Naming

**Determine which entity name is correct:**

Check Developer Tools → States for:
- `sensor.supply_from_heat_pump` (currently working: 91.184°F)
- `sensor.buffer_supply_from_heat_pump` (not found)

**Option A: If supply_from_heat_pump is correct:**
Update binary_sensors.yaml trend sensor:

```yaml
# Line ~28 in sensors/binary_sensors.yaml
entity_id: sensor.supply_from_heat_pump  # Already correct
```

**Option B: If buffer_supply_from_heat_pump should exist:**
Investigate why shelly_buffer_tank_sensors.yaml isn't creating it.

### Phase 4: Test Thermal Power Sensors

After fixing sensor swaps, restart HA and verify:

```
sensor.buffer_tank_thermal_power_input = positive value when HP heating buffer
sensor.dhw_tank_thermal_power_input = positive value when HP heating DHW
```

Both should show:
- Positive values (W) when actively heating that tank
- 0 when not heating that tank
- Never negative

### Phase 5: Re-enable G2 Valve Detection

Once thermal power sensors show correct positive values:

1. Edit `sensors/template/g2_valve_sensors.yaml`
2. Restore the original state logic (see git history for commit before e5b4385)
3. Update sensor references to use correct entity names
4. Restart Home Assistant

### Phase 6: Validate G2 Detection

After re-enabling, monitor for 24 hours:

**When HP is heating buffer (space heating):**
- G2 Position should show "Buffer Tank"
- buffer_tank_thermal_power_input > 0
- dhw_tank_thermal_power_input = 0
- buffer_tank_heating_trend = on (within 3 min)

**When HP is heating DHW:**
- G2 Position should show "DHW Tank"
- dhw_tank_thermal_power_input > 0
- buffer_tank_thermal_power_input = 0
- dhw_tank_heating_trend = on (within 3 min)

**When HP is off:**
- G2 Position should show "Buffer Tank (HP Off)" or similar
- Both thermal power = 0

## Testing Checklist

- [ ] Check DHW supply/return temps (which is hotter?)
- [ ] Fix DHW sensor swap if needed
- [ ] Verify buffer supply sensor entity name
- [ ] Restart Home Assistant
- [ ] Verify thermal power sensors show positive values
- [ ] Check integration sensors are accumulating
- [ ] Re-enable G2 valve detection
- [ ] Monitor for 24 hours with HP in different modes
- [ ] Verify energy balance: HP Output ≈ Buffer In + DHW In + Losses

## Energy Balance Target

Once everything is working, the energy balance should show:

```
HP Thermal Output (Daily) =
  Buffer Tank Input (Daily) +
  DHW Tank Input (Daily) +
  Piping Losses (5-10%)
```

**Example:**
```
HP Output: 50.0 kWh
Buffer Input: 42.0 kWh (84%)
DHW Input: 5.0 kWh (10%)
Piping Losses: 3.0 kWh (6%) ✅ Good
Total: 50.0 kWh ✅ Balanced
```

## Git History

- **Disabled:** Commit e5b4385 (2025-11-18)
- **Last Working Version:** Commit d7bf21a (before disable)

To see original code:
```bash
git show d7bf21a:sensors/template/g2_valve_sensors.yaml
```
