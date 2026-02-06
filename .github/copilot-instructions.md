# Copilot instructions

- This is a ROS 2 Python package built with `ament_python`. Core code lives in `src/weston_sim_py/weston_sim_py/`.
- The main node is `WestonSimulator` in [src/weston_sim_py/weston_sim_py/simulator.py](src/weston_sim_py/weston_sim_py/simulator.py). It publishes `/odom`, `/scan`, and TF `odom -> base_link`, and subscribes to `cmd_vel`.
- The simulator uses a fixed 2D map (`map_walls` line segments) and updates robot pose every `dt=0.1` seconds. Keep changes consistent with the existing kinematics and map representation (numpy arrays of `[x1, y1, x2, y2]`).
- Lidar is simulated with 360 rays and `range_max=10.0`. Intersection math uses vectorized numpy in `get_laser_scan`; preserve this style if extending the sensor model.

## Key workflows
- Build (colcon): `colcon build --symlink-install`
- Source environment: `source install/setup.bash`
- Run node (entry point): `ros2 run weston_sim_py run_sim`
- Tests (ament): `colcon test --packages-select weston_sim_py`

## Project-specific conventions
- ROS topics and frames are hard-coded: `/odom`, `/scan`, `cmd_vel`, and TF `odom -> base_link`. Keep naming consistent unless you also update any downstream configs.
- All ROS interfaces are created in the node constructor; timer-based updates happen in `update_step`.
- The entry point is defined in [src/weston_sim_py/setup.py](src/weston_sim_py/setup.py) (`run_sim = weston_sim_py.simulator:main`).

## Integration points
- Dependencies are declared in [src/weston_sim_py/package.xml](src/weston_sim_py/package.xml) and include `rclpy`, `geometry_msgs`, `nav_msgs`, `sensor_msgs`, and `tf2_ros`.
- Generated artifacts live under `build/` and `install/`; source of truth is under `src/`.
