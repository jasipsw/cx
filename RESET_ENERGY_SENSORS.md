## Energy Sensor Reset Instructions

The integration sensors (`cx_output_power_interval` and `cx_input_power_kwh`) accumulate energy over time. Setting their state via Developer Tools → States does NOT properly reset them.

### Why Manual State Setting Doesn't Work

When you set a sensor state to "0" via Developer Tools, you're only changing the **display value**. The integration platform's internal accumulator continues from its previous value. This is why you see the sensor quickly return to ~21,000 kWh.

### Proper Reset Method

**Option 1: Delete Entity via UI (Easiest)**

1. Go to **Settings → Devices & Services → Entities**
2. Search for: `sensor.cx_output_power_interval`
3. Click on the entity
4. Click the **gear icon** (⚙️) in the top right
5. Scroll down and click **"Delete"**
6. Confirm deletion
7. Repeat for `sensor.cx_input_power_kwh`
8. **Restart Home Assistant**
9. Sensors will recreate with 0 values

**Option 2: Delete via .storage File (Advanced)**

1. Stop Home Assistant
2. Edit `.storage/core.entity_registry`
3. Find and remove the entries for:
   - `sensor.cx_output_power_interval`
   - `sensor.cx_input_power_kwh`
4. Save the file
5. Start Home Assistant
6. Sensors will recreate with 0 values

**Option 3: Use Utility Meter Reset (Partial Solution)**

The utility meters (hourly/daily/monthly) can be reset via automation on the first of each period. However, this doesn't reset the underlying integration sensor.

### After Reset

Once properly reset, the sensors will:
- Start accumulating from 0 kWh
- Utility meters will show correct periodic values
- Energy-based COP calculations will be accurate

### Current Accumulated Values (Pre-Reset)

- Output Energy: 21,017 kWh (accumulated since sensor creation)
- Input Energy: 354 kWh (accumulated since sensor creation)
- Energy COP: 59.31 (inflated due to accumulated values)

These represent total accumulated energy since the sensors were first created, NOT just recent operation.

### Expected Values After Proper Reset

After running for 24 hours:
- Daily output: ~50-100 kWh (depending on heating demand)
- Daily input: ~15-30 kWh
- Daily COP: 2.5-4.5 (realistic range)

The integration sensors will gradually accumulate from 0, and monthly values will accurately represent current month's usage.
