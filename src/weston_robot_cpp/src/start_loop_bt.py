import rclpy
import time
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped
import os
from ament_index_python.packages import get_package_share_directory

def main():
    # Initialize ROS 2 Python client library
    rclpy.init()

    # Create a Nav2 BasicNavigator instance
    navigator = BasicNavigator()

    print("Waiting for Nav2 to become active...")
    navigator.waitUntilNav2Active()

    # -----------------------------------------------------
    # Define a square patrol path (3m x 3m)
    # Waypoint order:
    # (3, 0) -> (3, 3) -> (0, 3) -> (0, 0)
    # -----------------------------------------------------

    # List to store patrol waypoints (in the map frame)
    goal_poses = []

    # Waypoint A (bottom-right corner)
    p1 = PoseStamped()
    p1.header.frame_id = 'map'
    p1.pose.position.x = 3.0
    p1.pose.position.y = 0.0
    p1.pose.orientation.z = 0.707  # sin(45)
    p1.pose.orientation.w = 0.707  # cos(45)
    goal_poses.append(p1)

    # Waypoint B (top-right corner)
    p2 = PoseStamped()
    p2.header.frame_id = 'map'
    p2.pose.position.x = 3.0
    p2.pose.position.y = 3.0
    p2.pose.orientation.z = 1.0    # sin(90)
    p2.pose.orientation.w = 0.0    # cos(90)
    goal_poses.append(p2)

    # Waypoint C (top-left corner)
    p3 = PoseStamped()
    p3.header.frame_id = 'map'
    p3.pose.position.x = 0.0
    p3.pose.position.y = 3.0
    p3.pose.orientation.z = -0.707 # sin(-45)
    p3.pose.orientation.w = 0.707  # cos(-45)
    goal_poses.append(p3)

    # Waypoint D (back to origin / bottom-left corner)
    p4 = PoseStamped()
    p4.header.frame_id = 'map'
    p4.pose.position.x = 0.0
    p4.pose.position.y = 0.0
    p4.pose.orientation.z = 0.0    # sin(0)
    p4.pose.orientation.w = 1.0    # cos(0)
    goal_poses.append(p4)

    # Path to the custom Behavior Tree XML
    # Note: Make sure this path is correct.
    # relative location for docker
    pkg_weston_cpp = get_package_share_directory('weston_robot_cpp')
    bt_xml_path = os.path.join(pkg_weston_cpp, 'behavior_trees', 'loop_bt.xml')


    # Run patrol in an infinite loop
    while True:
        for i, goal in enumerate(goal_poses):
            print(f"--- Navigating to waypoint {i + 1} ---")

            # [Core] Send navigation goal using a custom Behavior Tree
            navigator.goToPose(goal, behavior_tree=bt_xml_path)

            # Monitor task execution
            while not navigator.isTaskComplete():
                feedback = navigator.getFeedback()
                # Optionally print remaining distance
                # if feedback:
                #     print(f"Remaining distance: {feedback.distance_remaining:.2f}")
                pass

            # Check navigation result
            result = navigator.getResult()
            if result == TaskResult.SUCCEEDED:
                print(f"Reached waypoint {i + 1}. Pausing for 2 seconds...")
                time.sleep(2.0)
            else:
                print(
                    f"Failed to reach waypoint {i + 1}. "
                    "This may be due to a persistent obstacle or injected failure."
                )
                # Optionally break the patrol loop or continue retrying
                time.sleep(1.0)


if __name__ == '__main__':
    main()
