# 1. Base image
FROM osrf/ros:humble-desktop

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# set workspace name for flexibility
ENV WORKSPACE_NAME=WESTON_SLAM_WS
SHELL ["/bin/bash", "-c"]

# 3. Install required packages
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-numpy \
    ros-humble-navigation2 \
    ros-humble-nav2-bringup \
    ros-humble-tf2-ros \
    && rm -rf /var/lib/apt/lists/*

# Install additional Python dependencies via pip if needed


# 4. Set workspace directory
WORKDIR /root/WESTON_SLAM_WS

# 5. [IMPORTANT] Copy source code into the container
COPY ./src ./src
COPY ./maps ./maps


# 6. [IMPORTANT] Build the workspace
# This ensures the project is pre-built when reviewers pull the image
RUN source /opt/ros/humble/setup.bash && \
    colcon build --symlink-install

# 7. [IMPORTANT] Configure entrypoint script
# Copy the custom ROS entrypoint from docker/ directory
COPY ./docker/ros_entrypoint.sh /ros_entrypoint.sh

# Grant execution permission to the entrypoint script
RUN chmod +x /ros_entrypoint.sh

# 8. Set container startup behavior
ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
