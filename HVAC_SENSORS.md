# HVAC Buffer Sensor Entities

This document lists the HVAC buffer sensor entities used for thermal power calculations.

## Entity List

These sensors are provided by the Home Assistant integration and represent the HVAC buffer tank measurements:

### Temperature Sensors

- **`sensor.buffer_supply_to_hvac_load`**
  - Description: Supply temperature from buffer to HVAC load
  - Unit: °C or °F (automatically detected)
  - Used in: HVAC Thermal Power Used calculation

- **`sensor.buffer_return_from_hvac_load`**
  - Description: Return temperature from HVAC load to buffer
  - Unit: °C or °F (automatically detected)
  - Used in: HVAC Thermal Power Used calculation

### Flow Rate Sensor

- **`sensor.hvac_buffer_tank_flow_rate`**
  - Description: Flow rate through HVAC buffer tank
  - Unit: L/min, GPM, or GPH (automatically detected and converted to L/min)
  - Used in: HVAC Thermal Power Used calculation

### Calculated Sensors

- **`sensor.hvac_thermal_power_used`**
  - Description: HVAC thermal power consumption
  - Formula: Q = ṁ × Cp × ΔT
  - Unit: W (Watts)
  - Dependencies: All three sensors above
  - Location: `sensors/template/hvac_sensors.yaml`

## Automatic Unit Conversion

The `sensor.hvac_thermal_power_used` sensor automatically handles unit conversion:

### Temperature Conversion
- °F → °C: `(temp - 32) / 1.8`
- °C → °C: No conversion

### Flow Rate Conversion
- GPM (gallons per minute) → L/min: `flow × 3.78541`
- GPH (gallons per hour) → L/min: `flow × 3.78541 / 60`
- L/min → L/min: No conversion

## Thermal Power Calculation

The thermal power calculation uses the formula:

```
Q = ṁ × Cp × ΔT

Where:
- Q = Thermal power (W)
- ṁ = Mass flow rate (kg/s)
- Cp = Specific heat capacity (J/kg·°C)
- ΔT = Temperature difference (°C)
```

### Calculation Steps

1. Get sensor values and check units
2. Convert temperatures to Celsius if needed
3. Convert flow rate to L/min if needed
4. Calculate delta T: `supply_temp - return_temp`
5. Convert flow rate: L/min → L/s → kg/s
6. Apply thermal power formula
7. Output result in Watts

## Integration Source

These sensors are provided by the integration connected to the HVAC buffer tank monitoring system. They are not defined in YAML configuration files but are available as entities in the Home Assistant instance.

## Related Files

- `sensors/template/hvac_sensors.yaml` - Contains the thermal power calculation sensor
- Issue #8 - Original request to use buffer entities
