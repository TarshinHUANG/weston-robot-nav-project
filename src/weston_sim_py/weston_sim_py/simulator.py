import rclpy # ros client library for python
from rclpy.node import Node
import numpy as np
from geometry_msgs.msg import Twist # msg format
import math # calculation

class WestonSimulator(Node):
    def __init__(self):
        super().__init__('weston_simulator')
        
        # 1. define maps (The World)
        # format: [x1, y1, x2, y2]
        # use numpy for easy math calculation
        self.map_walls = np.array([
            [-5.0, -5.0,  5.0, -5.0],  # down wall
            [ 5.0, -5.0,  5.0,  5.0],  # right wall 
            [ 5.0,  5.0, -5.0,  5.0],  # upper wall
            [-5.0,  5.0, -5.0, -5.0],  # left wall
            # one obstacle in the middle
            [ 1.0,  1.0,  2.0,  1.0],
            [ 2.0,  1.0,  2.0,  2.0],
            [ 2.0,  2.0,  1.0,  2.0],
            [ 1.0,  2.0,  1.0,  1.0] 
        ], dtype=np.float32)

        # ----- robot status ----- 
        # pose [x, y, theta]
        self.pose = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        # velocity [v, omega]
        self.vel=np.array([0.0, 0.0], dtype=np.float32)


        # ------ ROS interface -----
        # subscribe velocity
        self.create_subscription(Twist,'cmd_vel',self.cmd_callback,10)
        # timer
        self.dt=0.1  # 0.1s refresh
        self.create_timer(self.dt, self.update_step)


        self.get_logger().info(f"simulator.py start！map includes {len(self.map_walls)} walls and one obstacles.")



    # when receive command, safe velocity
    def cmd_callback(self,msg):
        self.vel[0] = msg.linear.x
        self.vel[1] = msg.angular.z

    # update position based on velocity
    def update_step(self):
        # extrade data
        x,y,theta = self.pose
        v,omega = self.vel
        dt = self.dt


        # ----- kinectics -----

        # update angle
        theta += omega*dt

        # normalized theta (-pi to pi)
        theta = math.atan2(math.sin(theta), math.cos(theta))

        # update postion
        x += v * math.cos(theta) * dt
        y += v * math.sin(theta) * dt

        # update pose
        self.pose = np.array([x,y,theta], dtype=np.float32)

        

        # print log
        self.get_logger().info(f"Pose: x={x:.2f}, y={y:.2f}, theta={theta:.2f}")


def main(args=None):
    rclpy.init(args=args)
    node = WestonSimulator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()