# Unit Standardization Plan - Metric Internal, Imperial Display

## Goal
Standardize all sensors to use **metric units internally** for calculations, with separate **display sensors** for imperial units in the UI.

---

## Current State (Problems)

### Mixed Unit Usage
```yaml
# Current approach (INCONSISTENT):
- CX50 Modbus sensors: Store Celsius (good)
- Template sensors: Convert to Fahrenheit immediately (bad for calculations)
- HVAC sensors: Use Fahrenheit in calculations (caused the bug!)
- Some sensors: Mix units in same calculation
```

### Issues This Causes
1. ✗ Temperature unit bugs (Fahrenheit in Celsius formulas)
2. ✗ Confusion about which sensor to use in calculations
3. ✗ Hard to maintain and debug
4. ✗ Can't easily switch between unit systems

---

## Proposed Solution

### **Three-Tier Sensor Architecture**

```
┌─────────────────────────────────────────────────────────┐
│ TIER 1: RAW SENSORS (Modbus, Shelly, etc.)             │
│ - Store exactly as received from device                 │
│ - Usually metric (Celsius, L/min)                       │
│ - Examples: cx50_outlet_water_temp_c,                   │
│            shellyplus1_c4d8d5543fc0_temperature         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ TIER 2: CALCULATION SENSORS (Template - Metric Only)   │
│ - ALL calculations in metric                            │
│ - Celsius, L/min, kW, kg/m³                            │
│ - Naming: sensor.heat_pump_cop,                        │
│          sensor.heat_pump_thermal_power_kw             │
│ - Used in: Formulas, automations, statistics          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ TIER 3: DISPLAY SENSORS (Template - User Preference)   │
│ - Convert from Tier 2 to imperial                       │
│ - Fahrenheit, GPM, BTU/hr, lb/ft³                      │
│ - Naming: sensor.heat_pump_outlet_temp_display         │
│          sensor.heat_pump_thermal_power_btu_hr         │
│ - Used in: Dashboards, notifications, UI              │
└─────────────────────────────────────────────────────────┘
```

---

## Implementation Details

### **File Structure**

```
sensors/template/
├── cx_sensors_metric.yaml           # All metric calculations (NEW)
├── cx_sensors_display.yaml          # All imperial display (NEW)
├── hvac_sensors_metric.yaml         # All metric calculations (NEW)
├── hvac_sensors_display.yaml        # All imperial display (NEW)
├── cx_optimization_sensors.yaml     # Keep metric only (already correct)
└── cx_binary_sensors.yaml           # No units, keep as-is
```

**OR** (alternative - single file per component):

```
sensors/template/
├── cx_sensors.yaml                  # Combined: metric + display sections
├── hvac_sensors.yaml                # Combined: metric + display sections
└── cx_optimization_sensors.yaml     # Metric only (calculations)
```

---

## Sensor Naming Conventions

### **Metric Sensors (Tier 2 - Calculations)**
```yaml
# Temperature (always Celsius)
sensor.heat_pump_outlet_temp_c          # Explicit _c suffix
sensor.heat_pump_inlet_temp_c
sensor.heat_pump_delta_t_c

# Flow (always L/min or L/s)
sensor.heat_pump_flow_lpm               # Explicit _lpm suffix
sensor.heat_pump_flow_lps

# Power (always Watts or kW)
sensor.heat_pump_thermal_power_w
sensor.heat_pump_thermal_power_kw
sensor.heat_pump_electrical_power_w

# COP (unitless, but always from metric inputs)
sensor.heat_pump_cop
```

### **Display Sensors (Tier 3 - User Interface)**
```yaml
# Temperature (Fahrenheit)
sensor.heat_pump_outlet_temp_f          # Explicit _f suffix
sensor.heat_pump_inlet_temp_f
sensor.heat_pump_delta_t_f

# Flow (GPM)
sensor.heat_pump_flow_gpm               # Explicit _gpm suffix

# Power (BTU/hr for HVAC folks)
sensor.heat_pump_thermal_power_btu_hr

# Keep kW for display (Americans use kW too)
sensor.heat_pump_thermal_power_kw_display
```

### **Dashboard Usage**
```yaml
# WRONG (current approach):
- entity: sensor.heat_pump_outlet_temperature  # Is this F or C? Unclear!

# RIGHT (new approach):
- entity: sensor.heat_pump_outlet_temp_f       # Clear: Fahrenheit for display
  name: "Outlet Temperature"
```

---

## Migration Strategy

### **Phase 1: Create Metric Foundation** (Week 1)
1. Create new metric-only sensors (Tier 2)
2. Update all calculations to use metric sensors only
3. Keep existing sensors working (don't break anything)

### **Phase 2: Create Display Sensors** (Week 1)
1. Create imperial display sensors (Tier 3)
2. Add to dashboards alongside metric versions
3. User can choose which to display

### **Phase 3: Update Dashboards** (Week 2)
1. Update dashboards to use display sensors
2. Add toggle for metric/imperial preference (optional)
3. Ensure automations use metric sensors (never display sensors)

### **Phase 4: Deprecate Old Sensors** (Week 2-3)
1. Identify old mixed-unit sensors
2. Add deprecation warnings
3. Eventually remove (after verifying nothing uses them)

---

## Specific Sensor Refactoring

### **Example 1: Heat Pump Outlet Temperature**

#### Current (Mixed):
```yaml
# TIER 1: Raw (Celsius from Modbus)
- name: "cx50_outlet_water_temp_c"
  state: "{{ states('...') }}"

# TIER 2: Immediately converts to Fahrenheit (BAD!)
- name: "Heat Pump Outlet Temperature"
  unit_of_measurement: "°F"
  state: >
    {% set outlet = states('sensor.cx50_outlet_water_temp_c') | float(0) %}
    {{ (outlet * 1.8 + 32.0) | round(2) }}
```

#### Proposed (Separated):
```yaml
# TIER 1: Raw (unchanged)
- name: "cx50_outlet_water_temp_c"
  state: "{{ states('...') }}"

# TIER 2: Metric calculation sensor (keep Celsius)
- name: "Heat Pump Outlet Temp"
  unique_id: heat_pump_outlet_temp_c
  unit_of_measurement: "°C"
  state_class: measurement
  device_class: temperature
  state: "{{ states('sensor.cx50_outlet_water_temp_c') | float(0) }}"

# TIER 3: Display sensor (Fahrenheit)
- name: "Heat Pump Outlet Temp (Display)"
  unique_id: heat_pump_outlet_temp_f
  unit_of_measurement: "°F"
  state_class: measurement
  device_class: temperature
  state: >
    {% set temp_c = states('sensor.heat_pump_outlet_temp_c') | float(0) %}
    {{ (temp_c * 1.8 + 32.0) | round(1) }}
```

### **Example 2: Thermal Power Calculation**

#### Current (Risky):
```yaml
# Calculation uses Fahrenheit sensors (caused the bug!)
- name: "HVAC Thermal Power Used"
  state: >-
    {% set delta_t = states('sensor.hvac_buffer_tank_delta_t') | float(0) %}
    # ↑ This was in Fahrenheit! Wrong!
```

#### Proposed (Safe):
```yaml
# TIER 2: Metric calculation (always Celsius)
- name: "HVAC Thermal Power"
  unique_id: hvac_thermal_power_w
  unit_of_measurement: "W"
  state: >-
    {% set delta_t_c = states('sensor.hvac_buffer_delta_t_c') | float(0) %}
    {% set flow_lpm = states('sensor.hvac_flow_lpm') | float(0) %}
    {# All metric - clear and safe #}
    {{ (flow_lpm / 60 * 970 / 1000 * 3950 * delta_t_c) | round(0) }}

# TIER 3: Display (kW for readability)
- name: "HVAC Thermal Power (Display)"
  unique_id: hvac_thermal_power_kw_display
  unit_of_measurement: "kW"
  state: >
    {{ (states('sensor.hvac_thermal_power_w') | float(0) / 1000) | round(2) }}

# TIER 3: Display (BTU/hr for HVAC professionals)
- name: "HVAC Thermal Power (BTU/hr)"
  unique_id: hvac_thermal_power_btu_hr
  unit_of_measurement: "BTU/hr"
  state: >
    {% set watts = states('sensor.hvac_thermal_power_w') | float(0) %}
    {{ (watts * 3.412) | round(0) }}
```

---

## Complete Sensor Inventory

### **Sensors to Refactor**

| Current Sensor | Current Unit | New Metric Sensor | New Display Sensor |
|----------------|--------------|-------------------|-------------------|
| `heat_pump_outlet_temperature` | °F | `heat_pump_outlet_temp_c` | `heat_pump_outlet_temp_f` |
| `heat_pump_inlet_temperature` | °F | `heat_pump_inlet_temp_c` | `heat_pump_inlet_temp_f` |
| `heat_pump_ambient_temperature` | °F | `heat_pump_ambient_temp_c` | `heat_pump_ambient_temp_f` |
| `heat_pump_target_heating_temperature` | °F | `heat_pump_target_temp_c` | `heat_pump_target_temp_f` |
| `heat_pump_delta_t` | °F | `heat_pump_delta_t_c` | `heat_pump_delta_t_f` |
| `hvac_buffer_tank_supply_temperature` | °F | `hvac_buffer_supply_temp_c` | `hvac_buffer_supply_temp_f` |
| `hvac_buffer_tank_return_temperature` | °F | `hvac_buffer_return_temp_c` | `hvac_buffer_return_temp_f` |
| `hvac_buffer_tank_delta_t` | °F | `hvac_buffer_delta_t_c` | `hvac_buffer_delta_t_f` |
| `cx50_pump_flow_gpm` | GPM | `heat_pump_flow_lpm` | `heat_pump_flow_gpm` |

### **Sensors Already Correct (Keep As-Is)**

| Sensor | Unit | Status |
|--------|------|--------|
| `heat_pump_cop` | (none) | ✅ Already unitless |
| `heat_pump_electrical_power_input` | W | ✅ Already metric |
| `heat_pump_thermal_power_output` | W | ✅ Already metric (after our fix) |
| `sensor.cx50_pump_flow_lpm` | L/min | ✅ Already metric |
| All optimization sensors | Various | ✅ Already use metric inputs |

---

## Helper Input Updates

Update helper inputs to use metric internally:

```yaml
# Current:
heat_pump_supply_temp_target:
  initial: 90          # Fahrenheit
  unit_of_measurement: "°F"

# Proposed:
heat_pump_supply_temp_target_c:
  name: Heat Pump Supply Temp Target
  initial: 32.2        # Celsius (90°F)
  unit_of_measurement: "°C"

heat_pump_supply_temp_target_f:
  name: Heat Pump Supply Temp Target (Display)
  initial: 90
  unit_of_measurement: "°F"
```

**Automation would use:**
```yaml
- action: number.set_value
  target:
    entity_id: number.cx50_heating_setpoint_c
  data:
    value: "{{ states('input_number.heat_pump_supply_temp_target_c') }}"
```

---

## Dashboard Configuration

### **Option 1: Show Both Units**
```yaml
- type: entities
  title: Temperatures
  entities:
    - entity: sensor.heat_pump_outlet_temp_c
      name: Outlet (°C)
    - entity: sensor.heat_pump_outlet_temp_f
      name: Outlet (°F)
```

### **Option 2: User Preference Toggle**
```yaml
# Add to helpers/input_boolean.yaml
prefer_imperial_units:
  name: Prefer Imperial Units (°F, GPM)
  initial: true

# In dashboard:
- type: conditional
  conditions:
    - entity: input_boolean.prefer_imperial_units
      state: "on"
  card:
    type: entities
    entities:
      - entity: sensor.heat_pump_outlet_temp_f
        name: Outlet Temperature

- type: conditional
  conditions:
    - entity: input_boolean.prefer_imperial_units
      state: "off"
  card:
    type: entities
    entities:
      - entity: sensor.heat_pump_outlet_temp_c
        name: Outlet Temperature
```

---

## Testing & Validation

### **Validation Checklist**
- [ ] All calculations use metric sensors only
- [ ] All display sensors correctly convert from metric
- [ ] Dashboards show preferred units (Fahrenheit for US users)
- [ ] Automations use metric sensors (never display sensors)
- [ ] No formulas mix units (e.g., Fahrenheit in Celsius calculation)
- [ ] Helper inputs store metric values internally
- [ ] Modbus number entities use Celsius (match device)

### **Test Cases**
1. **Temperature Conversion Test:**
   - Set HP outlet to 35°C (Modbus)
   - Verify `_c` sensor shows 35.0°C
   - Verify `_f` sensor shows 95.0°F

2. **Calculation Test:**
   - Heat pump running with 10°C delta T
   - Verify thermal power calculation uses 10, not 18
   - Verify result matches manual calculation

3. **Dashboard Test:**
   - View dashboard in Fahrenheit mode
   - All temperatures show °F
   - All values make sense for US users

---

## Documentation Updates

Update these files:
- `CX50_OPTIMIZATION_GUIDE.md` - Explain metric/imperial sensor strategy
- `HVAC_LOAD_BUG_FIX_CHECKLIST.md` - Reference correct sensors
- Dashboard YAML - Add comments explaining unit choices
- README.md - Document sensor naming conventions

---

## Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| **1. Planning** | 1 day | Review this plan, get approval |
| **2. Create Metric Sensors** | 1 day | Refactor calculation sensors to metric-only |
| **3. Create Display Sensors** | 1 day | Create imperial display sensors |
| **4. Update Dashboards** | 1 day | Use display sensors in UI |
| **5. Update Automations** | 1 day | Ensure automations use metric sensors |
| **6. Testing** | 2 days | Validate all sensors, calculations, displays |
| **7. Documentation** | 1 day | Update guides and add comments |
| **8. Cleanup** | 1 day | Remove deprecated sensors |

**Total: ~1-2 weeks** (can be done incrementally)

---

## Benefits Summary

✅ **Prevents bugs** - All calculations use consistent metric units
✅ **Clear intent** - Sensor name tells you exactly what unit it uses
✅ **Flexible display** - Easy to show metric or imperial in UI
✅ **Maintainable** - Future developers know which sensors to use
✅ **Professional** - Follows Home Assistant best practices
✅ **User-friendly** - Americans see Fahrenheit, Europeans see Celsius

---

## Questions to Resolve

1. **File organization preference?**
   - Separate files (`_metric.yaml` / `_display.yaml`)
   - Combined files with sections
   - Current: User preference?

2. **Naming convention preference?**
   - `_c` / `_f` suffixes (current proposal)
   - `_metric` / `_imperial` suffixes
   - `_display` suffix for imperial only
   - Current: User preference?

3. **Dashboard approach?**
   - Show both units always
   - User toggle for preference
   - Hardcode to imperial (since US-based)
   - Current: User preference?

4. **Migration pace?**
   - All at once (big bang)
   - Incremental (component by component)
   - Current recommendation: Incremental

---

## Next Steps

1. **Review this plan** - Does it make sense?
2. **Choose preferences** - Answer questions above
3. **Start with one component** - Heat pump temps as pilot?
4. **Validate approach** - Test metric/display separation
5. **Roll out to rest** - Apply to all sensors
6. **Update documentation** - Ensure clarity for future

**Ready to proceed?** Let me know your preferences and I can start implementing!
