import rclpy # ros client library for python
from rclpy.node import Node
import numpy as np
import math # calculation
import time

# msg format
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster
from sensor_msgs.msg import LaserScan  

# quaternion
def euler_to_quaternion(roll, pitch, yaw):
    
    # from (Roll, Pitch, Yaw) to (x, y, z, w)

    qx = np.sin(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) - np.cos(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
    qy = np.cos(roll/2) * np.sin(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.cos(pitch/2) * np.sin(yaw/2)
    qz = np.cos(roll/2) * np.cos(pitch/2) * np.sin(yaw/2) - np.sin(roll/2) * np.sin(pitch/2) * np.cos(yaw/2)
    qw = np.cos(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
    return (qx, qy, qz, qw)

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
        # odem
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        # TF
        self.tf_broadcaster = TransformBroadcaster(self)
        # publish lidar
        self.scan_pub = self.create_publisher(LaserScan, '/scan', 10)

        # timer
        self.dt=0.1  # 0.1s refresh
        self.create_timer(self.dt, self.update_step)


        self.get_logger().info(f"simulator.py start！map includes {len(self.map_walls)} walls and one obstacles. Publishing Odem, tf ... Maps and Laser are ready")



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

        current_time = self.get_clock().now()

        # publish Odom & TF
        self.publish_odom_tf(self.pose, self.vel, current_time)

        # publish lidar data
        self.publish_scan(self.pose, current_time)

        # # print log
        # self.get_logger().info(f"Pose: x={x:.2f}, y={y:.2f}, theta={theta:.2f}")
        

    def publish_odom_tf(self, pose, vel, current_time):
        x,y,theta = pose
        v, omega = vel

        # calculate quaternion
        qx, qy, qz, qw = euler_to_quaternion (0,0,theta)  # 2d


        # ----- boardcast TF (Odem -> base_link)-----
        # tell Rviz where robot base is
        t = TransformStamped()
        t.header.stamp = current_time.to_msg()
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'
        
        t.transform.translation.x = float(x)
        t.transform.translation.y = float(y)
        t.transform.translation.z = 0.0
        t.transform.rotation.x = qx
        t.transform.rotation.y = qy
        t.transform.rotation.z = qz
        t.transform.rotation.w = qw
        
        self.tf_broadcaster.sendTransform(t)


        # ----- boardcast Odem -----
        # tell nav the robot status
        odom = Odometry()
        odom.header.stamp = current_time.to_msg()
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_link'
        
        # pose
        odom.pose.pose.position.x = float(x)
        odom.pose.pose.position.y = float(y)
        odom.pose.pose.orientation.x = qx
        odom.pose.pose.orientation.y = qy
        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw
        
        # vel
        odom.twist.twist.linear.x = float(v)
        odom.twist.twist.angular.z = float(omega)
        
        self.odom_pub.publish(odom)


    # publish lidar msg
    def publish_scan(self, pose, current_time):
        
        scan = LaserScan()
        scan.header.stamp = current_time.to_msg()
        scan.header.frame_id = 'base_link' # lidar is fixed on robot 
        
        scan.angle_min = -np.pi
        scan.angle_max = np.pi
        scan.angle_increment = 2 * np.pi / 360 # scan by 1 degree
        scan.time_increment = 0.0
        scan.range_min = 0.1
        scan.range_max = 10.0
        
        # calculate distance using function
        ranges = self.get_laser_scan(pose, scan.angle_min, scan.angle_increment, 360)
        scan.ranges = ranges.tolist()
        
        self.scan_pub.publish(scan)

    # use numpy, got intersection between wall and laser
    def get_laser_scan(self, pose, angle_min, angle_inc, num_readings):

        x, y, theta = pose
        
        # generate all the scan angles, 360
        scan_angles = angle_min + np.arange(num_readings) * angle_inc + theta
        
        # vector for laser (dx, dy)
        ray_dx = np.cos(scan_angles)
        ray_dy = np.sin(scan_angles)
        
        # set min distance
        min_dists = np.full(num_readings, 10.0) # set the max range as 10m

        # loop for each wall
        for wall in self.map_walls:
            wx1, wy1, wx2, wy2 = wall
            
            # vector for wall
            wall_vec_x = wx2 - wx1
            wall_vec_y = wy2 - wy1
            
            # Line-Line Intersection problem: use Cross Product          
            denom = ray_dx * wall_vec_y - ray_dy * wall_vec_x
            
            # avoid parallel, which will divide by 0
            # if denom close 0，then will be infinite large
            denom = np.where(np.abs(denom) < 1e-6, 1e-6, denom)
            valid_mask = np.abs(denom) > 1e-6
            
            
            # calculate t (distance) 和 u (intersection)
            # vector calculation, 260 dimension
            dx_w = wx1 - x
            dy_w = wy1 - y
            
            t = (dx_w * wall_vec_y - dy_w * wall_vec_x) / denom
            u = (dx_w * ray_dy - dy_w * ray_dx) / denom
            
            # valid intersection：
            # 1. t > 0 (in the front)
            # 2. 0 <= u <= 1 (in wall part, not extended line)
            hit_mask = valid_mask & (t > 0) & (u >= 0) & (u <= 1)
            
            # upgrade min distance, if hitted

            min_dists = np.where(hit_mask, np.minimum(min_dists, t), min_dists)

        return min_dists


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