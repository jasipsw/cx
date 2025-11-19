# Sensor Naming Audit & Recommendations

## Executive Summary

**Problem:** Inconsistent sensor naming is causing confusion and potential coding errors. Some sensors follow clear naming patterns while others don't.

**Impact:**
- Makes code harder to understand
- Increases likelihood of bugs
- Difficult to debug issues
- Harder for future maintainability

**Recommendation:** YES, this is worth fixing. Propose systematic renaming following consistent patterns.

---

## Current Naming Issues Identified

### Issue 1: Inconsistent Prefix Usage

**Buffer Tank Sensors:**
```yaml
❌ sensor.supply_from_heat_pump          # Missing "buffer" prefix
✅ sensor.buffer_return_to_heat_pump     # Has "buffer" prefix
```

**Should be:**
```yaml
✅ sensor.buffer_supply_from_heat_pump   # Consistent with return sensor
✅ sensor.buffer_return_to_heat_pump     # Already correct
```

**DHW Tank Sensors:**
```yaml
✅ sensor.dhw_supply_from_heat_pump      # Has "dhw" prefix
✅ sensor.dhw_return_to_heat_pump        # Has "dhw" prefix
```
These are GOOD - they follow the pattern consistently.

### Issue 2: Direction Naming Ambiguity

Some sensors use "from/to" directional naming inconsistently:

**Current:**
- `supply_from_heat_pump` - FROM the heat pump (hot water leaving HP)
- `return_to_heat_pump` - TO the heat pump (cool water returning to HP)
- `buffer_supply_to_hvac_load` - TO the HVAC load
- `buffer_return_from_hvac_load` - FROM the HVAC load

**Recommendation:** Stick with "from/to" pattern consistently for all flow sensors.

### Issue 3: HVAC Wrapper Sensors

**Current:**
```yaml
sensor.hvac_buffer_tank_supply_temperature
sensor.hvac_buffer_tank_return_temperature
```

These are **wrappers** around the physical buffer tank sensors. They duplicate:
```yaml
sensor.supply_from_heat_pump (or buffer_supply_from_heat_pump)
sensor.buffer_return_to_heat_pump
```

**Question:** Are these wrappers needed, or should we use the physical sensors directly?

---

## Proposed Naming Convention

### Pattern Structure

```
[system]_[measurement]_[direction]_[location]
```

**Examples:**
- `buffer_supply_from_heat_pump` - Buffer tank's supply line coming FROM heat pump
- `buffer_return_to_heat_pump` - Buffer tank's return line going TO heat pump
- `dhw_supply_from_heat_pump` - DHW tank's supply line coming FROM heat pump
- `dhw_return_to_heat_pump` - DHW tank's return line going TO heat pump
- `buffer_supply_to_hvac_load` - Buffer tank's supply line going TO HVAC
- `buffer_return_from_hvac_load` - Buffer tank's return line coming FROM HVAC

### Heat Pump Sensors

```yaml
✅ sensor.heat_pump_inlet_temperature    # Water entering HP
✅ sensor.heat_pump_outlet_temperature   # Water leaving HP
✅ sensor.heat_pump_electrical_power_input
✅ sensor.heat_pump_thermal_power_output
```

These are GOOD - consistent "heat_pump_" prefix pattern.

---

## Recommended Renames

### High Priority (Causing Active Confusion)

| Current Name | Recommended Name | Reason |
|-------------|------------------|---------|
| `sensor.supply_from_heat_pump` | `sensor.buffer_supply_from_heat_pump` | Match pattern of `buffer_return_to_heat_pump` |

### Medium Priority (For Consistency)

| Current Name | Recommended Name | Reason |
|-------------|------------------|---------|
| `sensor.hvac_buffer_tank_supply_temperature` | Keep or remove? | Wrapper - may be redundant |
| `sensor.hvac_buffer_tank_return_temperature` | Keep or remove? | Wrapper - may be redundant |
| `sensor.hvac_buffer_tank_flow_rate` | `sensor.buffer_flow_to_hvac_load` | Clearer what it measures |

### Energy/Power Sensors

These seem consistent and good:
```yaml
✅ sensor.buffer_tank_thermal_power_input
✅ sensor.dhw_tank_thermal_power_input
✅ sensor.buffer_tank_energy_input
✅ sensor.dhw_tank_energy_input
```

---

## Impact Assessment

### Code Files That Reference `supply_from_heat_pump`

Based on grep results, these files need updates if renamed:

1. **sensors/template/hvac_sensors.yaml** - 4 references
2. **sensors/template/g2_valve_sensors.yaml** - 3 references
3. **sensors/template/thermal_power_sensors.yaml** - 3 references
4. **sensors/binary_sensors.yaml** - 1 reference
5. **dashboards/dashboard_sensor_verification.yaml** - 3 references

**Total:** ~14 code references to update

### UI Dashboard Risk

**Critical Question:** Is `sensor.supply_from_heat_pump` used in any UI-configured dashboards?

**Mitigation Strategy:**
1. Before renaming, document all current uses
2. Search HA's `.storage` folder for entity_id references (if accessible)
3. Consider creating an entity alias/redirect if HA supports it
4. Alternatively: Keep old entity as a template wrapper pointing to new one during transition

---

## Recommended Implementation Plan

### Phase 1: Audit & Document (Low Risk)
1. ✅ Create this audit document
2. Check which entity actually exists in HA: `supply_from_heat_pump` or `buffer_supply_from_heat_pump`
3. Document all UI dashboard uses (user to verify)
4. Get user approval on naming convention

### Phase 2: Code-Only Changes (Low Risk)
1. Update all code references to use consistent naming
2. Update YAML sensor definitions
3. Test with Home Assistant config check
4. No restart yet - just verify syntax

### Phase 3: Rename & Migrate (Medium Risk)
1. Restart Home Assistant to create new entity names
2. Verify new entities appear
3. Update any UI dashboards (user action)
4. Remove old entity definitions after 24hr soak period
5. Clean up entity registry if needed

### Phase 4: Validation (Low Risk)
1. Verify all sensors working
2. Check energy tracking still accumulating
3. Verify G2 valve detection still working
4. Monitor for 24 hours

---

## Questions for User

1. **Does `sensor.supply_from_heat_pump` currently exist in your Home Assistant?**
   - Or is it actually `sensor.buffer_supply_from_heat_pump`?
   - Check Developer Tools → States

2. **Do you have any UI-configured dashboards using these sensors?**
   - Besides the YAML dashboards we've been editing
   - Lovelace cards, entity cards, etc.

3. **Where are the DHW supply/return sensors defined?**
   - Couldn't find `sensor.dhw_supply_from_heat_pump` in YAML files
   - Is this from a Shelly integration? Another file?

4. **Approval on naming convention?**
   - `[system]_[measurement]_[direction]_[location]` pattern
   - Example: `buffer_supply_from_heat_pump`

---

## Benefits of Fixing This

✅ **Reduced confusion** - Clear, consistent names
✅ **Fewer bugs** - Less chance of using wrong sensor
✅ **Easier debugging** - Know exactly what each sensor measures
✅ **Better maintainability** - Future you (or others) will thank you
✅ **Self-documenting** - Names explain what they do
✅ **Scalability** - Easy to add new sensors following pattern

---

## My Recommendation

**YES, fix this now.**

The system is still relatively small, and you're actively working on it. The longer you wait:
- More code will depend on incorrect names
- More UI dashboards may reference them
- Harder to change later

The effort is:
- **Time:** 1-2 hours to implement and test
- **Risk:** Low-Medium (with proper planning)
- **Benefit:** HIGH (long-term code quality)

Better to do it now while the pain is fresh and the scope is manageable.
