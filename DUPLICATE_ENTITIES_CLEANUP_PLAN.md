# Duplicate Entities Cleanup Plan

Generated: 2025-11-18
Total Duplicates Found: **186 entities**

## Executive Summary

Home Assistant has created 186 duplicate entities with `_2`, `_3`, `_4`, etc. suffixes. These are categorized into:

- **61 Unavailable Entities** - Safe to delete immediately
- **125 Active Entities** - Require investigation before deletion

## Root Causes Identified

### 1. YAML `unique_id` Conflicts (CRITICAL)

**Heat Pump Cycle Duration Sensors:**
```yaml
# CONFLICT DETECTED:
sensors/legacy_sensors.yaml:342:  unique_id: heat_pump_current_cycle_duration
sensors/template/heat_pump_cycle_sensors.yaml:10:  unique_id: heat_pump_current_cycle_duration

sensors/legacy_sensors.yaml:354:  unique_id: heat_pump_current_cycle_duration_minutes
sensors/template/heat_pump_cycle_sensors.yaml:38:  unique_id: heat_pump_current_cycle_duration_minutes
```

**Impact:** Creating `_2` duplicates for both sensors

**Resolution Required:**
- Determine which file contains the correct/current definition
- Remove duplicate `unique_id` from legacy_sensors.yaml (likely obsolete)
- Delete `_2` entities from entity registry
- Restart Home Assistant

### 2. Device Integration Re-pairing

Many Zigbee/Z-Wave devices have duplicates from:
- Device re-pairing without removing old entities
- Integration reconfigurations
- Device firmware updates

### 3. Enphase/Energy Monitoring Integration Changes

~40 energy sensor duplicates suggest the Enphase integration was:
- Reconfigured
- Updated
- Re-authenticated

## Cleanup Strategy

### Phase 1: Delete Unavailable Entities (LOW RISK - 61 entities)

These entities are unavailable and safe to delete via entity registry:

#### Heat Pump Sensors (2):
- `sensor.buffer_supply_from_heat_pump_2`
- `sensor.buffer_return_to_heat_pump_2`

#### Buttons (38):
All `button.*_identify_2` entities from Zigbee lights

#### Lights (9):
- `light.driveway_sconce_2`
- `light.family_room_tv_area_2`
- `light.shed_sconce_2`
- `light.cavern_inside_2`
- `light.cavern_sconce_2`
- `light.closet_chandelier_2`
- `light.over_bed_recessed_2`
- `light.kitchen_cabinet_2`
- `light.pantry_cabinet_2`
- `light.kitchen_recessed_2`
- `light.master_bath_shower_2`

#### Shades (15):
All Leviosa motor shade `_2`, `_3`, `_5` variants:
- `update.leviosa_motor_shades_firmware_2/3/5`
- `cover.leviosa_motor_shades_2/3/5`
- `sensor.leviosa_motor_shades_battery_2/3/5`
- `sensor.leviosa_motor_shades_battery_voltage_2/3/5`
- `sensor.leviosa_motor_shades_battery_charge_state_2/3/5`

#### Patio Bedroom Recessed (6):
- `update.patio_bedroom_recessed_3`
- `button.patio_bedroom_recessed_identify_4`
- `light.patio_bedroom_recessed_3`
- `number.patio_bedroom_recessed_on_level_3`
- `number.patio_bedroom_recessed_on_off_transition_time_3`
- `select.patio_bedroom_recessed_power_on_behavior_on_startup_3`

#### Water Heater (6):
- `sensor.esphome_econet_water_heater_alarm_2/3/4`
- `sensor.esphome_econet_water_heater_alarm_history_2`

#### Misc (10):
- `button.patio_family_room_identify_2`
- `button.west_backyard_flood_identify_2`
- `button.backyard_flood_east_identify_2`
- `button.patio_office_identify_2`
- `button.driveway_sconce_identify_2`
- `button.mr_overhead_identify_2`
- `button.driveway_downlight_identify_2`
- `button.bedroom_hallway_identify_2`
- `button.family_room_tv_area_identify_2`
- `button.shed_inside_light_identify_2`
- `button.shed_sconce_identify_2`
- `button.cavern_inside_identify_2`
- `button.cavern_sconce_identify_2`
- `button.front_hallway_recessed_identify_2`
- `button.sitting_area_recessed_identify_2`
- `button.over_bed_recessed_identify_2`
- `button.closet_chandelier_identify_2`
- `button.garage_gable_lights_identify_2`
- `button.master_suite_hallway_identify_2`
- `button.u6_iw_restart_2`
- `sensor.mech_room_2_total_daily_energy_cost_2`
- `media_player.family_room_tv_3`
- `device_tracker.google_pixel_watch_2`

### Phase 2: Investigate Active Entities (HIGH RISK - 125 entities)

#### Critical Heat Pump Duplicates (5) - **FIX YAML FIRST**

Before deleting these, fix the `unique_id` conflict in YAML:

1. **Action:** Check which definition is current:
   ```bash
   # Compare definitions in both files
   grep -A 10 "heat_pump_current_cycle_duration" sensors/legacy_sensors.yaml
   grep -A 10 "heat_pump_current_cycle_duration" sensors/template/heat_pump_cycle_sensors.yaml
   ```

2. **Decision:** If `heat_pump_cycle_sensors.yaml` is current:
   - Comment out or remove the duplicate from `legacy_sensors.yaml`
   - Delete the `_2` entities from entity registry
   - Restart HA to recreate correctly

**Affected entities:**
- `sensor.heat_pump_current_cycle_duration_2` (active: 1492)
- `sensor.heat_pump_current_cycle_duration_minutes_2` (active: 0.01)

**Other active heat pump duplicates to investigate:**
- `sensor.hvac_thermal_energy_used_2` (active: 812.15 kWh)
- `binary_sensor.cx_c31_electrical_valve_2` (active: on) - **NOTE:** This may be intentional (check YAML)
- `binary_sensor.cx_c31_electrical_valve_3` (active: on) - **Likely true duplicate**

#### CX Binary Sensors (3):
- `binary_sensor.cx_power_status_2` (active: on)
- `binary_sensor.cx_error_status_2` (active: off)
- `binary_sensor.a_h_condensation_threshold_2` (active: off)

**Action:** Check for `unique_id` conflicts in `sensors/template/cx_binary_sensors.yaml`

#### Energy Monitoring Sensors (~40)

These are all active and reporting values:

**Enphase Grid Feed:**
- `sensor.sub_panel_import_2` = 7615.05
- `sensor.sub_panel_consumption_2` = 10410.41
- `sensor.sub_panel_amps_2` = 4.0
- `sensor.sub_panel_watts_2` = 141.0
- `sensor.sub_panel_total_daily_energy_2` = 4.91

**Sub Panel:**
- `sensor.sub_panel_import_3` = 1056.0
- `sensor.sub_panel_consumption_3` = 16445.63
- `sensor.sub_panel_amps_3` = 15.0

**LC2 Grid Power:**
- `sensor.lc2_grid_power_import_2` = 0.07
- `sensor.lc2_grid_power_consumption_2` = 6070.49
- `sensor.lc2_grid_power_amps_2` = 0.5
- `sensor.lc2_grid_power_watts_2` = 71.0
- `sensor.lc2_grid_power_total_daily_energy_2` = 0.75

**WHEM Monitors (multiple legs):**
- All `sensor.*_whem_*_leg_2` sensors (frequency, volts, watts, amps)

**Inverter Sensors (19):**
- `sensor.inverter_482332040587` through `sensor.inverter_482334045995`
- All showing active power readings

**Action:** These likely came from Enphase/WHEM integration reconfiguration. Options:
1. Check which entities are being used in dashboards/automations
2. Verify which set has correct historical data
3. Delete the unused set
4. May need to reconfigure integration to prevent future duplicates

#### Thermal Comfort Sensors (17)

All Master Bath thermal comfort calculations have `_3` duplicates:
- `sensor.thermal_comfort_absolute_humidity_3`
- `sensor.thermal_comfort_dew_point_3`
- `sensor.thermal_comfort_dew_point_perception_3`
- (... 14 more)

**Action:** Check thermal comfort integration configuration

#### Device Trackers (15)

Multiple device tracker duplicates for phones, watches:
- `device_tracker.pixel_8_pro_5/6`
- `device_tracker.google_pixel_watch_2_2/3/4`
- `device_tracker.pixel_watch_4/4_2`
- UniFi default devices

**Action:** Check UniFi integration and Mobile App integration for conflicts

#### Smart Home Devices (35)

**Closet Recessed (5):**
- `update.closet_recessed_2`
- `light.closet_recessed_2`
- `number.closet_recessed_on_level_2`
- `number.closet_recessed_on_off_transition_time_2`
- `select.closet_recessed_power_on_behavior_on_startup_2`

**"Could Not Identify" Device (5):**
- Same pattern as above for `could_not_identify_2`

**Mudroom Recessed (5):**
- `update.d215s_firmware_2` (D215S device)
- Similar pattern

**Action:** These are Zigbee devices - check Z2M or ZHA for device re-pairing issues

#### HVAC Demand Sensors (6):
- `sensor.bedroom_demand_2`
- `sensor.front_bedroom_demand_2`
- `sensor.main_floor_demand_2`
- `sensor.family_room_demand_2`
- `sensor.master_suite_demand_2`
- `sensor.office_3_demand_2`

All showing 0.0 - likely safe to delete duplicates

#### UniFi Network Switches (4):
- `switch.unifi_network_ha_443/8443`
- `switch.unifi_network_waveshare_80/443`

**Action:** Check UniFi integration configuration

#### Enphase Battery Management (18):

Multiple sets of battery cutoff/restore/mode/action selects with `_2/_3/_4`:
- `number.cutoff_battery_level_2/3/4`
- `number.restore_battery_level_2/3/4`
- `select.mode_2/3/4`
- `select.grid_action_2/3/4`
- `select.microgrid_action_2/3/4`
- `select.generator_action_2/3/4`

**Action:** This suggests Enphase Enpower configuration created multiple battery manager instances

#### Scripts (3):

**NOTE:** These may NOT be duplicates - they may be intentionally numbered:
- `script.wtw_preset_0` - "Comfoairq stand 0"
- `script.wtw_preset_2` - "Comfoairq stand 2"
- `script.wtw_preset_3` - "Comfoairq stand 3"

**Action:** Verify these are actual presets 0, 2, 3 (not duplicates of a base script)

#### Input Numbers (1):
- `input_number.target_humidity_45` = 44.9

**Action:** Check if this is intentionally numbered or a duplicate

#### Misc Active (8):
- `sensor.family_room_humidity_2`
- `sensor.lgs_161224_sim_2`
- `sensor.pixel_8_pro_battery_level_2`
- `sensor.pixel_8_pro_battery_state_2`
- `sensor.pixel_8_pro_charger_type_2`
- `media_player.nesthub2de6_3`
- `media_player.family_room_tv_2` (note: `_3` is unavailable)
- `sensor.comfoairq_analog_input_2/3/4`
- Multiple Shelly temperature sensors with `_2` through `_6`
- `sensor.50clark_uptime_2`
- `sensor.u6_iw_uptime_3`
- `sensor.u6_iw_uplink_mac_2`
- `sensor.u6_iw_state_2`
- `sensor.50clark_cpu_utilization_2`
- `sensor.50clark_memory_utilization_2`
- `update.u6_iw_2`
- `sensor.airgradient_pm2_5` (ends in `_5` but may be intentional model number)
- `sensor.airgradient_pm0_3` (ends in `_3` but may be intentional)
- `switch.shellyplus1_c4d8d5543fc0_switch_0` (ends in `_0` - likely intentional)
- `sensor.shellyplus1_c4d8d5543fc0_uptime_2`
- `device_tracker.iphone_2`
- `device_tracker.pixel_tablet_2`
- `device_tracker.lgs_ipad_ubiquiti_2`
- `device_tracker.jas_2`
- `device_tracker.unifi_default_06_a6_94_7b_2c_30`

## Recommended Workflow

### Step 1: Fix YAML Conflicts (CRITICAL)

1. Review `sensors/legacy_sensors.yaml` for obsolete sensor definitions
2. Remove duplicate `unique_id` entries for:
   - `heat_pump_current_cycle_duration`
   - `heat_pump_current_cycle_duration_minutes`
3. Check for other `unique_id` conflicts across all sensor files

### Step 2: Delete Unavailable Entities (Safe)

Via Home Assistant UI:
1. Go to **Settings → Devices & Services → Entities**
2. Filter by "unavailable"
3. Search for each unavailable duplicate from Phase 1 list
4. Delete each entity
5. No restart needed

### Step 3: Investigate Active Duplicates

For each active duplicate:
1. Check which entity (original or duplicate) is used in:
   - Dashboards
   - Automations
   - Scripts
   - Other sensor calculations
2. Verify which has historical data (Developer Tools → Statistics)
3. Determine which is the "correct" entity
4. Update references if needed
5. Delete the incorrect duplicate

### Step 4: Restart and Verify

1. Restart Home Assistant
2. Wait for full initialization
3. Check duplicate detector dashboard
4. Verify no new duplicates created
5. Confirm critical sensors working (heat pump, energy monitoring)

## Prevention

To prevent future duplicates:

1. **Never change `unique_id` in YAML** - This creates new entities
2. **Check entity registry before removing old sensors** - Delete old entities first
3. **Use entity ID rename feature** - Settings → Entities → Rename (preserves history)
4. **Document integration changes** - Note when reconfiguring integrations
5. **Monitor duplicate detector** - Check hourly automation notifications

## Files to Review

- `sensors/legacy_sensors.yaml` - Check for obsolete definitions
- `sensors/template/heat_pump_cycle_sensors.yaml` - Current definitions?
- `sensors/template/cx_binary_sensors.yaml` - Check CX valve unique_ids
- `sensors/template/thermal_comfort_sensors.yaml` - Check Master Bath sensors
- Integration configs for Enphase, UniFi, Z2M/ZHA

## Next Actions

1. **User Decision Required:**
   - Which sensor file is current: `legacy_sensors.yaml` or `heat_pump_cycle_sensors.yaml`?
   - Should we audit all sensor files for `unique_id` conflicts?
   - Which energy monitoring sensors are correct (_original or _2/_3 versions)?

2. **Safe to Execute Now:**
   - Delete all 61 unavailable entities from Phase 1

3. **Requires Investigation:**
   - Compare sensor definitions in legacy vs current files
   - Check dashboard/automation usage of active duplicates
   - Review integration configurations

---

## Summary Statistics

| Category | Unavailable (Safe) | Active (Investigate) | Total |
|----------|-------------------|---------------------|-------|
| Heat Pump Sensors | 2 | 5 | 7 |
| Buttons | 38 | 0 | 38 |
| Lights | 11 | 2 | 13 |
| Energy Monitoring | 0 | 40 | 40 |
| Device Trackers | 1 | 15 | 16 |
| Shades | 15 | 0 | 15 |
| Smart Devices | 0 | 15 | 15 |
| Thermal Comfort | 0 | 17 | 17 |
| Misc | 4 | 31 | 35 |
| **TOTAL** | **61** | **125** | **186** |
