import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # ======================================================
    # 1. Base configuration and file paths
    # ======================================================
    pkg_weston_cpp = get_package_share_directory('weston_robot_cpp')
    pkg_nav2 = get_package_share_directory('nav2_bringup')
    
    # NOTE:
    # The map file is assumed to be located under the workspace root at:
    #   ~/Weston_SLAM_ws/maps/sim_map.yaml
    # Update this path if the map location changes.
    map_file_path = os.path.join(os.getenv('HOME'), 'Weston_SLAM_ws/maps/sim_map.yaml')

    # Default Nav2 parameter file
    nav2_params_path = os.path.join(pkg_nav2, 'params', 'nav2_params.yaml')

    # ======================================================
    # 2. Launch Arguments
    # ======================================================
    
    # Argument A: Map file path (can be overridden via CLI)
    map_arg = DeclareLaunchArgument(
        'map',
        default_value=map_file_path,
        description='Full path to the map YAML file'
    )

    # ======================================================
    # 3. Node Definitions
    # ======================================================

    # Node 1: Custom simulator node
    simulator_node = Node(
        package='weston_sim_py',
        executable='run_sim',
        name='weston_simulator',
        output='screen'
    )

    # Node 2: Static TF patch (base_link -> base_footprint)
    # Required by Nav2 frame conventions
    tf_patch_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0', '0', '0', '0', '0', '0', 'base_link', 'base_footprint'],
        output='screen'
    )

    # Node 3: Nav2 Bringup (navigation stack core)
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'map': LaunchConfiguration('map'),
            'use_sim_time': 'False',  # Set to True only if a simulated clock is used
            'params_file': nav2_params_path,
            
        }.items()
    )

    # Node 4: RViz2 visualization
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=[
            '-d',
            os.path.join(pkg_nav2, 'rviz', 'nav2_default_view.rviz')
        ],
        output='screen'
    )
    # rviz_node = Node(
    #     package='rviz2',
    #     executable='rviz2',
    #     name='rviz2',
    #     # arguments=['-d', os.path.join(pkg_nav2, 'rviz', 'nav2_default_view.rviz')], # <--- 暂时注释掉这一行
    #     output='screen'
    # )   

    return LaunchDescription([
        map_arg,
        simulator_node,
        tf_patch_node,
        nav2_launch,
        rviz_node
    ])
