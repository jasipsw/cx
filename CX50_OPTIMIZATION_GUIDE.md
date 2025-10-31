# CX50 Heat Pump Optimization Guide

## Overview

This guide documents the optimization process to improve the CX50-2 heat pump's Coefficient of Performance (COP) from the current 2.0-2.5 to the manufacturer's rating of 4.55 at 47°F ambient temperature.

## Problem Statement

### Current Performance
- **Measured COP:** 2.0-2.5
- **Target COP:** 4.55 (manufacturer rating at 47°F ambient)
- **Gap:** ~2.0 COP points (~82% improvement needed)

### Root Cause: Short Cycling
- **Current Runtime:** ~5 minutes per cycle
- **Off Time:** ~60 minutes between cycles
- **Issue:** Large startup energy spikes dominate overall efficiency
- **Impact:** Startup penalty negates steady-state efficiency gains

## Three-Phase Optimization Strategy

### Phase 1: Increase Buffer Differential (10°F → 18°F)
**Goal:** Extend heat pump runtime to reduce startup frequency

**Implementation:**
- Target: 18°F buffer tank temperature differential
- Method: Adjust control logic to allow wider temperature swing
- Expected Outcome: Longer runtime per cycle (15+ minutes target)

**How to Activate:**
1. Navigate to Energy Analysis dashboard → Optimization Settings tab
2. Set "Optimization Phase" to "Phase 1: Buffer Differential 18°F"
3. Monitor "Cycle Duration History" graph for improvements

**Success Metrics:**
- Average cycle duration increases from 5 min to 15+ min
- Off-time decreases from 60 min to 30-45 min
- Short cycle alerts reduce significantly

### Phase 2: Lower Supply Temperature (90°F → 85°F)
**Goal:** Improve COP by operating closer to optimal temperature differential

**Implementation:**
- Reduce heat pump outlet temperature setpoint from 90°F (32.2°C) to 85°F (29.4°C)
- Uses Modbus register P03 (address 143) - AC Heating Target Temperature
- Automation sets `number.cx50_heating_setpoint_c` to 29.4°C

**How to Activate:**
1. Ensure Phase 1 has been running for at least 2-3 days with good results
2. Navigate to Energy Analysis dashboard → Optimization Settings tab
3. Set "Optimization Phase" to "Phase 2: Supply Temp 85°F"
4. Monitor COP improvements over 24-48 hours

**Expected Results:**
- COP improves to 3.0-3.5 range
- Cycle efficiency increases to 65-75% of target
- Heat pump runs more efficiently but may cycle slightly more often

### Phase 3: Fine-tune to 82°F (Target)
**Goal:** Reach manufacturer's optimal operating point

**Implementation:**
- Further reduce outlet temperature to 82°F (27.8°C)
- This is the manufacturer's recommended temperature for optimal COP at 47°F ambient
- Final tuning based on actual performance data

**How to Activate:**
1. Verify Phase 2 results are stable and positive
2. Check that ambient temperatures are in the 40-50°F range
3. Set "Optimization Phase" to "Phase 3: Supply Temp 82°F (Target)"
4. Monitor closely for 48-72 hours

**Target Results:**
- COP reaches 4.0-4.55 range
- Cycle efficiency 85-100% of manufacturer rating
- Runtime remains stable at 15-20 minutes per cycle

## New Sensors & Monitoring

### Optimization Sensors
Located in: `/sensors/template/cx_optimization_sensors.yaml`

**Cycle Detection:**
- `binary_sensor.heat_pump_running` - Detects when heat pump is active (>500W)
- `sensor.heat_pump_current_cycle_duration` - Tracks current runtime in seconds
- `sensor.heat_pump_current_cycle_duration_minutes` - Runtime in minutes
- `sensor.heat_pump_off_time_duration` - Time since last shutdown

**Phase Detection:**
- `binary_sensor.heat_pump_in_startup_phase` - First 3 minutes of operation
- `binary_sensor.heat_pump_in_steady_state` - After 3 minutes of operation

**Performance Metrics:**
- `sensor.heat_pump_startup_phase_cop` - COP during startup (<3 min)
- `sensor.heat_pump_steady_state_cop` - COP during steady state (>3 min)
- `sensor.heat_pump_startup_energy_penalty` - Extra energy consumed during startup
- `sensor.heat_pump_cycle_efficiency` - Current COP as % of target (4.55)
- `sensor.heat_pump_cop_improvement_needed` - Gap between current and target COP

**Alerts:**
- `sensor.heat_pump_short_cycle_alert` - Status message for cycle health
- `sensor.heat_pump_cycle_ratio_warning` - Alerts for abnormal runtime ratios

### Helper Inputs
Located in: `/helpers/input_number.yaml`, `/helpers/input_select.yaml`, `/helpers/input_boolean.yaml`

**Optimization Controls:**
- `input_select.optimization_phase` - Phase selection dropdown
- `input_number.buffer_differential_target` - Target buffer differential (°F)
- `input_number.heat_pump_supply_temp_target` - Target supply temperature (°F)
- `input_number.target_cop` - Target COP goal (default: 4.55)
- `input_number.minimum_runtime_target` - Minimum desired runtime (minutes)

**Feature Toggles:**
- `input_boolean.enable_cop_optimization` - Enable/disable optimization tracking
- `input_boolean.enable_short_cycle_alerts` - Enable/disable short cycle notifications
- `input_boolean.enable_startup_penalty_tracking` - Enable/disable startup analysis

### Modbus Controls
Added to: `/modbus.yaml` (lines 1059-1115)

**New Number Entities:**
- `number.cx50_heating_setpoint_c` - AC heating target temp (15-60°C)
- `number.cx50_cooling_setpoint_c` - AC cooling target temp (5-30°C)
- `number.cx50_dhw_setpoint_c` - DHW target temp (20-70°C)
- `number.cx50_compressor_max_percentage` - Max compressor speed (30-100%)

**Modbus Register Mapping:**
- P03 (Address 143): AC Heating Target Temperature
- P02 (Address 142): AC Cooling Target Temperature
- P04 (Address 144): DHW Target Temperature
- P-13 (Address 127): Compressor Max Percentage

### Automations
Added to: `/automations.yaml` (lines 347-469)

1. **Phase 1 Automation** (`cx_optimization_phase_1`)
   - Triggers when Phase 1 is selected
   - Sets buffer differential target to 18°F
   - Sends notification

2. **Phase 2 Automation** (`cx_optimization_phase_2`)
   - Triggers when Phase 2 is selected
   - Sets heating setpoint to 29.4°C (85°F)
   - Sends notification

3. **Phase 3 Automation** (`cx_optimization_phase_3`)
   - Triggers when Phase 3 is selected
   - Sets heating setpoint to 27.8°C (82°F)
   - Sends notification

4. **Short Cycle Alert** (`cx_short_cycle_alert`)
   - Triggers when heat pump shuts off after <10 minutes
   - Sends notification with runtime
   - Can be disabled via `input_boolean.enable_short_cycle_alerts`

5. **Target COP Achieved** (`cx_target_cop_achieved`)
   - Triggers when COP exceeds 4.5 for 5+ minutes
   - Sends celebration notification
   - Can be disabled via `input_boolean.enable_cop_optimization`

## Dashboard Usage

### Energy Analysis Dashboard
Access via: Home Assistant sidebar → "Energy Analysis"

**Tab 1: COP Optimization**
- Current COP gauge and efficiency metrics
- Cycle status (running, idle, duration)
- Startup vs Steady State comparison
- COP trend graph (24 hours)
- Temperature monitoring
- Power input vs thermal output

**Tab 2: Optimization Settings**
- Phase selection dropdown
- Target parameter sliders
- Fluid property settings
- Quick controls for heat pump

**Tab 3: Cycle Analysis**
- 48-hour cycle duration history
- 7-day COP statistics
- Daily/monthly energy tracking
- Runtime statistics

**Tab 4: Technical Details**
- Calculation formulas
- Sensor health status
- HVAC load analysis (see below)

## HVAC Load vs Thermal Output Analysis

### The Question
"Why does HVAC load not more closely match thermal output?"

### Investigation Areas

**1. System Losses**
The heat pump's thermal output is measured at the unit's outlet, while HVAC load is measured at the distribution points. Heat is lost in between:

- **Piping Losses:** Heat loss through supply lines between heat pump and buffer tank
  - Monitor: `sensor.heat_pump_outlet_temperature` vs `sensor.hvac_buffer_tank_supply_temperature`
  - Calculate: Piping loss = (HP Outlet - Buffer Supply) × Flow Rate × Specific Heat

- **Buffer Tank Losses:** Standby heat loss from tank to environment
  - Monitor: `sensor.hvac_buffer_tank_delta_t` during idle periods
  - Insulation effectiveness can be evaluated

- **Distribution Losses:** Heat loss in lines from buffer to air handlers
  - Monitor: `sensor.hvac_buffer_tank_supply_temperature` vs actual air handler inlet temps

**2. Measurement Timing & Accuracy**
- Heat pump output: Calculated from Modbus sensors (CX50 built-in)
- HVAC load: Calculated from Shelly temperature sensors + flow meter
- Timing lag between measurements may cause apparent discrepancies
- Flow sensor accuracy at different flow rates
- Temperature sensor calibration differences

**3. Buffer Tank Behavior**
- Temperature stratification: Hot water at top, cooler at bottom
- Mixing losses during charge/discharge cycles
- Effective storage efficiency typically 85-95%

**4. Thermal Mass Effects**
- Thermal mass of piping and equipment
- Heat absorption/release during transient operation
- Most significant during startup and shutdown

### Recommended Analysis Steps

1. **Compare Sensors During Steady State:**
   ```
   Heat Pump Outlet (CX50): sensor.heat_pump_outlet_temperature
   Buffer Supply (Shelly):  sensor.hvac_buffer_tank_supply_temperature
   Temperature Drop:        Calculate difference
   ```

2. **Calculate System Efficiency:**
   ```
   System Efficiency = HVAC Thermal Load / Heat Pump Thermal Output

   Where:
   - Heat Pump Output: sensor.heat_pump_thermal_power_output
   - HVAC Load:       sensor.hvac_thermal_power_used

   Expected: 85-95% (10-15% losses)
   ```

3. **Track Losses Over Time:**
   Create a new sensor in `cx_optimization_sensors.yaml`:
   ```yaml
   - name: "System Distribution Losses"
     unit_of_measurement: "W"
     state: >-
       {% set hp_output = states('sensor.heat_pump_thermal_power_output') | float(0) %}
       {% set hvac_load = states('sensor.hvac_thermal_power_used') | float(0) %}
       {{ (hp_output - hvac_load) | round(0) }}
   ```

4. **Verify Flow Measurements:**
   - Compare `sensor.cx50_pump_flow_lpm` (heat pump side)
   - With `sensor.hvac_buffer_tank_flow_rate` (buffer side)
   - Should be similar; discrepancies indicate measurement error

### Expected Findings
Typical residential hydronic systems experience:
- Piping losses: 3-5% (well-insulated) to 10-15% (poorly insulated)
- Buffer tank losses: 2-5% during operation, higher during standby
- Distribution losses: 5-10% depending on distance and insulation
- Total system efficiency: 80-92% is normal

If losses exceed 20%, investigate:
- Inadequate pipe insulation
- Buffer tank insulation degradation
- Sensor calibration issues
- Flow meter accuracy

## Troubleshooting

### Short Cycling Persists After Phase 1
**Symptoms:** Runtime still <10 minutes, frequent starts

**Possible Causes:**
1. Buffer tank too small for heat load
2. Heat pump oversized for application
3. Control deadband settings too tight
4. External thermostat interference

**Solutions:**
- Verify buffer tank size (should be 10-15 gallons per ton of cooling capacity)
- Check `number.cx50_compressor_max_percentage` - reduce to 70-80% if oversized
- Review P-parameter settings in CX50 manual
- Disable any external thermostats temporarily to test

### COP Not Improving
**Symptoms:** COP remains at 2.0-2.5 after Phase 2/3

**Possible Causes:**
1. Ambient temperature too low (below design point)
2. Refrigerant charge issue
3. Flow rate insufficient
4. Heat exchanger fouling

**Solutions:**
- Check `sensor.heat_pump_ambient_temperature` - optimization assumes 40-50°F
- Verify `sensor.cx50_pump_flow_lpm` is within spec (check manual)
- Monitor `sensor.heat_pump_delta_t` - should be 5-10°F in heating mode
- If DeltaT too high: flow issue; too low: heat exchanger issue
- Consider professional refrigerant charge verification

### Startup Energy Penalty High
**Symptoms:** `sensor.heat_pump_startup_energy_penalty` consistently >500Wh

**Analysis:**
- Review `sensor.heat_pump_startup_phase_cop` vs `sensor.heat_pump_steady_state_cop`
- Large gap indicates significant startup losses
- This is normal but should improve with longer runtimes

**Solutions:**
- Focus on extending runtime (Phase 1)
- Consider buffer tank size increase
- Check for rapid temperature drops during off-cycle (indicates excessive load or small buffer)

## Data Collection & Analysis

### Key Metrics to Track
Create a spreadsheet or use Home Assistant's statistics to track:

**Daily Metrics:**
- Average COP (from history)
- Total runtime hours
- Number of cycles
- Average cycle duration
- Short cycle count
- Total energy input (kWh)
- Total thermal output (kWh)

**Weekly Comparison:**
Compare metrics before/after each phase implementation to quantify improvements.

### Expected Improvement Timeline

**Baseline (Week 0):**
- COP: 2.0-2.5
- Avg cycle: 5 minutes
- Cycles per hour: 1 every 65 minutes

**After Phase 1 (Week 1-2):**
- COP: 2.5-3.0 (20-40% improvement)
- Avg cycle: 15+ minutes
- Cycles per hour: 1 every 45 minutes

**After Phase 2 (Week 3-4):**
- COP: 3.0-3.5 (50-75% improvement)
- Avg cycle: 15-20 minutes
- Cycles per hour: 1 every 40-50 minutes

**After Phase 3 (Week 5+):**
- COP: 4.0-4.55 (100%+ improvement) - TARGET ACHIEVED!
- Avg cycle: 15-25 minutes
- Cycles per hour: 1 every 35-45 minutes

## References

### Files Modified/Created
1. `/sensors/template/cx_optimization_sensors.yaml` - NEW
2. `/helpers/input_number.yaml` - NEW
3. `/helpers/input_select.yaml` - NEW
4. `/helpers/input_boolean.yaml` - NEW
5. `/dashboards/dashboard_energy.yaml` - NEW
6. `/modbus.yaml` - MODIFIED (added number entities)
7. `/automations.yaml` - MODIFIED (added 5 automations)
8. `/configuration.yaml` - No changes needed (already includes helpers directory)

### Documentation
- CX50-2-IOM.PDF: Installation, Operation, and Maintenance manual
- Modbus register reference in `/dashboards/dashboard_modbus.yaml`
- This guide: `/CX50_OPTIMIZATION_GUIDE.md`

### Support
For questions or issues:
- Review GitHub issue #1: https://github.com/jasipsw/cx/issues/1
- Check Home Assistant logs for sensor errors
- Verify Modbus connection: `sensor.cx50_inlet_water_temp_c` should have valid readings
- Ensure all automations are enabled in Settings → Automations & Scenes

---

**Document Version:** 1.0
**Last Updated:** 2025-10-31
**Author:** Claude Code (Anthropic)
**Purpose:** CX50 Heat Pump COP Optimization from 2.5 to 4.55
