import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/tarshin/Weston_SLAM_ws/install/weston_sim_py'
