# Energy Accumulation Sensors - Implementation Summary

This document describes the new sensors created for tracking heat pump energy accumulation and calculating COP for different intervals.

## Overview

The new sensor system provides:
1. **Proper energy accumulation** for both electrical input and thermal output
2. **Last run COP calculation** that accounts for water circulation after compressor stops
3. **Standby energy loss tracking** when circulator pump runs but heat pump is off
4. **Comprehensive cycle tracking** with duration and count metrics

---

## New Integration Sensors (sensors/legacy_sensors.yaml)

These sensors convert instantaneous power (W or kW) to accumulated energy (kWh):

### 1. Total Thermal Output
- **Sensor**: `sensor.cx_output_power_interval`
- **Source**: `sensor.heat_pump_thermal_power_output` (W)
- **Purpose**: Accumulates all thermal energy produced (Heat, Cool, DHW modes)
- **Unit**: kWh

### 2. Heating Electrical Energy
- **Sensor**: `sensor.hp_heating_electrical_energy_kwh`
- **Source**: `sensor.hp_heating_electrical_power_kw`
- **Purpose**: Accumulates electrical energy consumed in heating mode only
- **Unit**: kWh
- **Note**: Only accumulates when mode is 'Heat' or 'HEAT + DHW'

### 3. Heating Thermal Energy
- **Sensor**: `sensor.hp_heating_thermal_energy_kwh`
- **Source**: `sensor.hp_heating_thermal_power_kw`
- **Purpose**: Accumulates thermal energy produced in heating mode only
- **Unit**: kWh
- **Note**: Only accumulates when mode is 'Heat' or 'HEAT + DHW'

### 4. HVAC Thermal Energy Used
- **Sensor**: `sensor.hvac_thermal_energy_used`
- **Source**: `sensor.hvac_thermal_power_used` (W)
- **Purpose**: Accumulates thermal energy consumed by the HVAC system
- **Unit**: kWh

### 5. Standby Thermal Loss
- **Sensor**: `sensor.hp_standby_thermal_loss_accumulated`
- **Source**: `sensor.hp_standby_thermal_loss_rate` (W)
- **Purpose**: Accumulates energy lost when circulator runs but HP is off
- **Unit**: kWh
- **Note**: In heating mode, water is cooled; in cooling mode, water is warmed

---

## Heat Pump Cycle Tracking (sensors/legacy_sensors.yaml)

History stats sensors that track runtime and cycles:

### 1. Current Cycle Duration
- **Sensor**: `sensor.heat_pump_current_cycle_duration`
- **Purpose**: Shows how long the current heat pump run has been active
- **Unit**: hours
- **Updates**: Continuously while running

### 2. Current Cycle Duration (Minutes)
- **Sensor**: `sensor.heat_pump_current_cycle_duration_minutes`
- **Purpose**: Same as above but in minutes for easier reading
- **Unit**: minutes

### 3. Off Time Duration
- **Sensor**: `sensor.heat_pump_off_time_duration`
- **Purpose**: Shows how long the heat pump has been off
- **Unit**: hours

### 4. Daily Runtime Hours
- **Sensor**: `sensor.heat_pump_daily_runtime_hours`
- **Purpose**: Total hours the heat pump ran today
- **Unit**: hours
- **Resets**: Daily at midnight

### 5. Daily Cycle Count
- **Sensor**: `sensor.heat_pump_daily_cycle_count`
- **Purpose**: Number of times the heat pump turned on today
- **Unit**: count
- **Resets**: Daily at midnight

---

## Last Run COP Tracking (sensors/template/cx_trigger_sensors.yaml)

Trigger-based sensors that calculate COP for the last complete heat pump run:

### How It Works

The system defines a "run" as:
- **Start**: When heat pump turns ON (power > 500W)
- **End**: 5 minutes after heat pump turns OFF (to account for water circulation)

This 5-minute delay is CRITICAL because:
- Water continues circulating after compressor stops
- Heat pump continues delivering hot/cold water during this period
- Measuring COP immediately when compressor stops would be inaccurate

### Sensors Created

1. **Heat Pump Run Start Energy Input**
   - `sensor.heat_pump_run_start_energy_input`
   - Captures starting electrical energy when HP turns on

2. **Heat Pump Run Start Energy Output**
   - `sensor.heat_pump_run_start_energy_output`
   - Captures starting thermal energy when HP turns on

3. **Heat Pump Last Run Energy Input**
   - `sensor.heat_pump_last_run_energy_input`
   - Total electrical energy consumed during last run (kWh)

4. **Heat Pump Last Run Energy Output**
   - `sensor.heat_pump_last_run_energy_output`
   - Total thermal energy produced during last run (kWh)

5. **Heat Pump Last Run COP** ⭐
   - `sensor.heat_pump_last_run_cop`
   - **Formula**: Energy Output / Energy Input
   - Updates 5 minutes after each heat pump run completes
   - This is the COP for the ENTIRE run including circulation time

6. **Heat Pump Last Run Timestamp**
   - `sensor.heat_pump_last_run_timestamp`
   - When the last run ended

7. **Heat Pump Last Cycle Duration**
   - `sensor.heat_pump_last_cycle_duration`
   - Duration of last cycle in seconds

8. **Heat Pump Last Cycle Duration Minutes**
   - `sensor.heat_pump_last_cycle_duration_minutes`
   - Duration of last cycle in minutes

---

## Standby Energy Loss Tracking

### Binary Sensor: Circulator Running Without HP

**Sensor**: `binary_sensor.circulator_running_hp_off`
**Location**: sensors/template/cx_optimization_sensors.yaml

Detects when:
- Circulator pump is running (flow > 4 L/min)
- Heat pump is OFF (power < 500W)
- Compressor frequency = 0

**Why This Matters**:
- In heating mode: Hot water loses heat through the outdoor coil (even with fan off)
- In cooling mode: Cool water gains heat from the outdoor coil
- This is wasted energy that reduces system efficiency

### Power Loss Sensor

**Sensor**: `sensor.hp_standby_thermal_loss_rate`
**Location**: sensors/template/cx_optimization_sensors.yaml

Calculates instantaneous thermal loss rate (W) using:
```
Q = ṁ × Cp × |ΔT|
```
Where:
- ṁ = mass flow rate (kg/s)
- Cp = specific heat capacity (J/kg·°C)
- ΔT = outlet - inlet temperature (°C)

The absolute value of ΔT gives us the loss magnitude regardless of direction.

### Energy Loss Accumulation

**Sensor**: `sensor.hp_standby_thermal_loss_accumulated`
**Location**: sensors/legacy_sensors.yaml (integration platform)

Accumulates the standby loss over time to show total energy wasted (kWh).

### Daily Tracking

**Sensor**: `sensor.circulator_pump_idle_loss_duration_daily`
**Location**: sensors/legacy_sensors.yaml (history_stats platform)

Tracks how many hours per day the circulator runs without the heat pump.

---

## Utility Meters (sensors/utility_meters/utility_meters.yaml)

New utility meters for tracking energy by time period:

### Standby Loss
- `sensor.hp_standby_loss_daily` - Daily standby loss (kWh)
- `sensor.hp_standby_loss_monthly` - Monthly standby loss (kWh)

### Electrical Energy Input
- `sensor.hp_electrical_energy_hourly` - Hourly electrical consumption
- `sensor.hp_electrical_energy_daily` - Daily electrical consumption
- `sensor.hp_electrical_energy_monthly` - Monthly electrical consumption

### Thermal Energy Output
- `sensor.hp_thermal_energy_output_hourly` - Hourly thermal production
- `sensor.hp_thermal_energy_output_daily` - Daily thermal production
- `sensor.hp_thermal_energy_output_monthly` - Monthly thermal production

---

## Key Sensors for Dashboard

Here are the most important sensors to add to your dashboard:

### Real-Time Monitoring
1. `sensor.heat_pump_last_run_cop` - COP of last complete run ⭐
2. `sensor.heat_pump_current_cycle_duration_minutes` - Current run duration
3. `sensor.hp_standby_thermal_loss_rate` - Current standby loss rate (W)
4. `binary_sensor.circulator_running_hp_off` - Is energy being wasted?

### Daily Statistics
5. `sensor.hp_electrical_energy_daily` - Today's electrical consumption
6. `sensor.hp_thermal_energy_output_daily` - Today's thermal production
7. `sensor.hp_standby_loss_daily` - Today's standby loss
8. `sensor.heat_pump_daily_cycle_count` - Number of cycles today
9. `sensor.heat_pump_daily_runtime_hours` - Total runtime today
10. `sensor.circulator_pump_idle_loss_duration_daily` - Wasted hours today

### Historical Tracking
11. `sensor.heat_pump_last_run_energy_input` - Last run electrical use (kWh)
12. `sensor.heat_pump_last_run_energy_output` - Last run thermal production (kWh)
13. `sensor.heat_pump_last_cycle_duration_minutes` - Last run duration

---

## Calculating Different COP Metrics

With these sensors, you can now calculate:

### 1. Last Run COP (Already calculated)
```
sensor.heat_pump_last_run_cop
```

### 2. Hourly COP
```
COP = sensor.hp_thermal_energy_output_hourly / sensor.hp_electrical_energy_hourly
```

### 3. Daily COP
```
COP = sensor.hp_thermal_energy_output_daily / sensor.hp_electrical_energy_daily
```

### 4. Monthly COP
```
COP = sensor.hp_thermal_energy_output_monthly / sensor.hp_electrical_energy_monthly
```

### 5. Space Heating COP (Excludes DHW)
```
COP = sensor.hvac_hp_thermal_energy_produced_daily / sensor.hp_heating_electrical_energy_daily
```

---

## Troubleshooting

### If sensors show "unavailable":

1. **Check source sensors**: Ensure all source sensors are working
   - `sensor.heat_pump_electrical_power_input`
   - `sensor.heat_pump_thermal_power_output`
   - `sensor.cx50_pump_flow_lpm`
   - `binary_sensor.heat_pump_running`

2. **Check modbus connection**: Ensure CX50 is communicating
   - `sensor.cx50_compressor_frequency`
   - `sensor.cx50_input_ac_voltage`
   - `sensor.cx50_input_ac_current`

3. **Wait for first cycle**: Some sensors only update after the heat pump completes a full cycle

4. **Restart Home Assistant**: After adding new sensors, restart is required

### If Last Run COP seems incorrect:

1. Check that the 5-minute delay is appropriate for your system
   - Edit the delay in `sensors/template/cx_trigger_sensors.yaml` (lines 74-75 and 125-126)
   - Increase if water circulates longer after compressor stops
   - Decrease if 5 minutes is too long

2. Verify energy sensor accuracy:
   - Compare `sensor.heat_pump_last_run_energy_input` with expected consumption
   - Compare `sensor.heat_pump_last_run_energy_output` with thermal calculations

### If Standby Loss seems high:

This is normal! The heat pump coil acts as a heat exchanger even when off:
- In heating mode: Hot water loses 200-500W to outdoor air
- In cooling mode: Cool water gains heat from outdoor air
- Solution: Reduce minimum flow rate if possible, or add a bypass valve

---

## Files Modified

1. `sensors/legacy_sensors.yaml` - Integration and history_stats sensors
2. `sensors/template/cx_trigger_sensors.yaml` - Last run COP tracking
3. `sensors/template/cx_optimization_sensors.yaml` - Standby loss sensors
4. `sensors/utility_meters/utility_meters.yaml` - Utility meters for time-based tracking

---

## Next Steps

1. **Restart Home Assistant** to load all new sensors
2. **Monitor** `sensor.heat_pump_last_run_cop` after a few cycles
3. **Add to dashboard** using the key sensors listed above
4. **Calibrate** the 5-minute delay if needed
5. **Track** `sensor.hp_standby_loss_daily` to quantify efficiency loss
6. **Consider** reducing circulator minimum flow if standby loss is significant

---

## Questions or Issues?

If you notice any sensors not working correctly:
1. Check Home Assistant logs for errors
2. Verify all source sensors are available
3. Ensure modbus communication is stable
4. Adjust the 5-minute delay if runs extend longer than expected
