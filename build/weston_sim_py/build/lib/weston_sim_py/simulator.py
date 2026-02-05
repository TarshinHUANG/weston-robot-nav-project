import rclpy
from rclpy.node import Node
import numpy as np

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

        self.get_logger().info(f"simulator.py start！map includes {len(self.map_walls)} walls and one obstacles.")

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