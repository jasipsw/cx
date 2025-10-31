
Write
/home/user/cx/HEAT_PUMP_OPTIMIZATION.md
Update Todos
 Increase buffer tank differential from 10°F to 18°F for longer runtimes
 Create Modbus sensors to read current setpoints (supply temp, differential)
 Create optimization monitoring sensors
 Create optimization dashboard to monitor cycling and COP improvements
 Create HEAT_PUMP_OPTIMIZATION.md summary document
Perfect! I've created all the files. Here's your complete implementation guide:

📦 Files Created:
1. ✅ Optimization Sensors (Ready to Add)
Add to: sensors/power_grid_sensors.yaml (append to end)

~200 lines of sensor code
Includes heat pump running detection, per-cycle COP, steady-state COP, startup penalty tracking
2. ✅ Helper Configuration (Ready to Add)
Add to: helpers/input_number.yaml

Delta-T threshold slider (starts at 0°F, tunable)
3. ✅ Dashboard Section (Ready to Add)
Add to: dashboards/dashboard_energy.yaml (add as new section)

Optimization analysis cards
COP comparison graphs
Cycle detection debug tools
Runtime trend monitoring
4. ✅ Project Documentation (Ready to Commit)
Created: HEAT_PUMP_OPTIMIZATION.md in /home/user/cx/

Complete project summary
Problem analysis
Optimization strategy
All sensor explanations
Data collection plan
Success criteria
Technical formulas
Next steps
🚀 Implementation Steps:
Step 1: Add the Sensors
# Open sensors/power_grid_sensors.yaml
# Scroll to the end
# Copy/paste the complete sensor code from File 1 above
Step 2: Add the Helper
# Open helpers/input_number.yaml  
# Add the heat_pump_delta_t_threshold configuration from File 2
Step 3: Add Dashboard Section
# Open dashboards/dashboard_energy.yaml
# Add the Optimization Analysis sections from File 3 (at the end, before any closing comments)
Step 4: Restart Home Assistant
# Settings → System → Restart
# Wait 2-3 minutes for restart
Step 5: Verify Sensors Exist
# Developer Tools → States
# Search for: heat_pump_running
# Should see: binary_sensor.heat_pump_running
# Also check: heat_pump_cop_this_cycle, heat_pump_steady_state_cop, etc.
Step 6: Increase Buffer Differential
# Access Chiltrix CX50-2 controller
# Settings → Temperature Differential (or Hysteresis)
# Change: 10°F → 18°F
# Save and restart controller
Step 7: Monitor Results (24-48 hours)
# Watch your Energy Analysis dashboard
# Check the new "Optimization Analysis" section
# Runtime should increase from 5 min → 25-30 min
# COP should improve from ~2.5 → 3.8+
📊 What to Monitor:
Once implemented, watch these key sensors:

Immediate feedback (during next cycle):

sensor.heat_pump_current_cycle_runtime - Should increase to 20-30 minutes
binary_sensor.heat_pump_running - Should stay ON longer
After 24 hours:

sensor.heat_pump_avg_cycle_runtime - Should show 25-30 min average
sensor.heat_pump_startup_penalty_pct - Should decrease from ~35% to <10%
sensor.heat_pump_cop_this_cycle - Should improve to 3.8-4.2
After 48 hours:

Compare energy consumption before/after
Should see 30-40% reduction in electrical input for same thermal output
💾 Commit to Repository:
Once you've added everything and it's working:

git add sensors/power_grid_sensors.yaml
git add helpers/input_number.yaml
git add dashboards/dashboard_energy.yaml
git add HEAT_PUMP_OPTIMIZATION.md
git commit -m "Add heat pump optimization sensors and analysis

- Detect complete heating cycles including cooldown phase
- Track per-cycle COP vs steady-state COP  
- Quantify startup penalty impact (~30-40% efficiency loss)
- Monitor cycle runtime and frequency
- Goal: Increase runtime from 5min to 25-30min via 18°F differential
- Expected COP improvement: 2.5 → 3.8+ in mild weather

Includes comprehensive HEAT_PUMP_OPTIMIZATION.md for project continuity"

