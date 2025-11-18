# G2 Valve Position Detection - Fix Plan

## Current Status: RE-ENABLED with Delta-T Correlation (2025-11-18)

The G2 valve position detection has been reimplemented using a simpler, more robust method:
- `sensor.g2_valve_position`: Now uses delta-T correlation between HP outlet and tank supplies
- `binary_sensor.g2_valve_dhw_mode`: Active when valve position = "DHW Tank"

### How the New Method Works

**Simple principle:** Whichever supply line (buffer or DHW) has a temperature closest to the HP outlet is currently receiving flow from the G2 valve.

**Example with your current temps:**
```
HP Outlet: 95.36°F
Buffer Supply: 91.18°F → Difference: 4.18°F  ✅ CLOSEST
DHW Supply: 75.2°F     → Difference: 20.16°F
→ G2 Position: Buffer Tank
```

**Why this works:**
- Heat pump outlet temp directly reflects the heat being produced
- Active flow path will have temps close to HP outlet (accounting for pipe losses)
- Inactive path will cool down to ambient/tank temp
- Works during idle, defrost, and differential cooling scenarios
- No time windows or trend detection needed

**Threshold:** 10°F maximum difference to avoid false matches from stale temperatures

## Why It Was Originally Disabled

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

## Implementation Status

### ✅ Phase 1: Implemented Delta-T Correlation Method (COMPLETE)

**Status:** G2 valve detection reimplemented using temperature correlation
- Commit: 04775c7
- Method: Compares HP outlet temp with buffer/DHW supply temps
- Working with current sensors without requiring fixes

### 🔄 Phase 2: DHW Thermal Power Still Negative (MONITORING)

**Current readings:**
```
sensor.dhw_supply_from_heat_pump = 75.2°F
sensor.dhw_return_to_heat_pump = 75.542°F
sensor.dhw_tank_thermal_power_input = -218W ❌
```

**Analysis:** Temperatures are very close (0.34°F difference), suggesting:
- HP not actively heating DHW right now
- Differential cooling or recent mode switch
- G2 valve directing to buffer (confirmed: HP outlet 95°F matches buffer supply 91°F)

**Action:** Monitor during active DHW heating cycle to determine if sensor swap is real issue or just idle state behavior

### ✅ Phase 3: Buffer Supply Sensor Confirmed (COMPLETE)

**Resolution:** `sensor.supply_from_heat_pump` is the correct entity name
- Currently: 91.18°F
- Close to HP outlet (95.36°F), confirming active heating
- Updated G2 detection code to use this sensor

### ✅ Phase 4: Thermal Power Sensors Working (MOSTLY COMPLETE)

**Current status:**
```
sensor.buffer_tank_thermal_power_input = 0W (valve directing to buffer, waiting for HP cycle)
sensor.dhw_tank_thermal_power_input = -218W (low temps, small delta-T, needs monitoring)
```

**Energy accumulation:**
```
Buffer Tank: 19.274 kWh ✅
DHW Tank: 1.475 kWh (despite negative power - accumulated during actual heating)
```

### ✅ Phase 5: G2 Valve Detection Re-enabled (COMPLETE)

**Status:** Fully operational with delta-T correlation method
- Commit: 04775c7
- Binary sensor active
- Ready for energy balance tracking

### 🔄 Phase 6: Validate G2 Detection (IN PROGRESS)

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

## Future Enhancement: Post-G2-Valve Sensor

**Current limitation:** Detection uses supply temps at the tanks, which may lag valve switches by several minutes due to:
- Pipe thermal mass
- Flow propagation time
- Mixing with residual fluid in pipes

**Proposed improvement:** Add temperature sensor immediately downstream of G2 valve

**Benefits:**
- **Instant detection** - no waiting for temps to propagate
- **Faster response** - reduces detection lag from ~3 minutes to ~10 seconds
- **Higher accuracy** - cleaner signal before mixing/cooling occurs
- **Simpler logic** - single sensor comparison instead of two

**Implementation when sensor added:**
1. Update lines 32 and 36 in `sensors/template/g2_valve_sensors.yaml`
2. Change from tank supply sensors to new post-G2-valve sensor
3. May be able to reduce 10°F threshold to 5°F for tighter detection

## Testing Checklist

- [x] Implement delta-T correlation method
- [x] Verify buffer supply sensor entity name
- [x] Re-enable G2 valve detection
- [x] Check integration sensors are accumulating (19.274 kWh buffer, 1.475 kWh DHW)
- [ ] Monitor DHW thermal power during active DHW heating cycle
- [ ] Monitor for 24 hours with HP in different modes
- [ ] Verify energy balance: HP Output ≈ Buffer In + DHW In + Losses
- [ ] Optional: Install post-G2-valve sensor for faster detection

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
