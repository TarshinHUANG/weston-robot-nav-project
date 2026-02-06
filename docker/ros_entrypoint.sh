#!/bin/bash
set -e

# 1. load ros2 humble 
source "/opt/ros/humble/setup.bash"

# 2. load self project
if [ -f "/root/WESTON_SLAM_WS/install/setup.bash" ]; then
    source "/root/WESTON_SLAM_WS/install/setup.bash"
fi

# 3. run user command
exec "$@"