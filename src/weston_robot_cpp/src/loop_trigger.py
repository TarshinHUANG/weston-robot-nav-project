import rclpy
import time
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped


# start_trigger.py (只需发一次)
def main():
    # Initialize ROS 2 Python client library
    rclpy.init()

    # Create a Nav2 BasicNavigator instance
    navigator = BasicNavigator()

    print("Waiting for Nav2 to become active...")
    navigator.waitUntilNav2Active()
    
    # 只需要发一次！因为 XML 里面有 <Repeat> 无限循环
    # 这个 Dummy Goal 只是为了骗过 API 启动 BT
    dummy_goal = PoseStamped()
    dummy_goal.header.frame_id = 'map'
    dummy_goal.pose.position.x = 0.0
    dummy_goal.pose.position.y = 0.0
    dummy_goal.pose.position.z = 0.0
    dummy_goal.pose.orientation.x = 0.0
    dummy_goal.pose.orientation.y = 0.0
    dummy_goal.pose.orientation.z = 0.0
    dummy_goal.pose.orientation.w = 1.0
    # ... 设置 dummy_goal ...

    bt_xml_path = (
        '/home/tarshin/Weston_SLAM_ws/src/'
        'weston_robot_cpp/behavior_trees/loop_pure_bt.xml'
    )
    print("发送触发指令，BT 内部将接管无限循环...")
    navigator.goToPose(dummy_goal, behavior_tree=bt_xml_path)
    

    # 脚本可以退出了，或者在这里仅仅用于监控
    # 如果脚本退出，任务可能会被取消，建议保留监控
    while not navigator.isTaskComplete():
        time.sleep(1)


if __name__ == '__main__':
    main()
