import numpy as np
import cv2
import yaml

# === 1. Configuration parameters (MUST match simulator.py) ===
# Real-world map size (meters)
REAL_WIDTH = 10.0
REAL_HEIGHT = 10.0

# Map resolution (meters per pixel)
# Smaller value -> higher resolution.
# Nav2 commonly recommends 0.05.
RESOLUTION = 0.05 

# Compute image size in pixels
IMG_W = int(REAL_WIDTH / RESOLUTION)
IMG_H = int(REAL_HEIGHT / RESOLUTION)

# Create a white background:
# 255 (or near) = free space
# 0 = occupied (wall/obstacle)
# In Nav2 maps:
#   255 = Free
#   0   = Occupied
image = np.ones((IMG_H, IMG_W), dtype=np.uint8) * 254


# === 2. Helper functions to convert world coordinates to pixel coordinates ===
def world_to_pixel(wx, wy):
    """
    Coordinate system conversion:

    Simulator:
        origin at center (0,0)
        +x right, +y up

    Map image:
        origin bottom-left conceptually
        OpenCV origin is top-left
        rows increase downward

    Steps:
        1) Shift world coords into [0, width/height]
        2) Convert meters -> pixels
        3) Flip Y-axis for image coordinates
    """

    # Shift to positive coordinates (0 ~ map size)
    shifted_x = wx + REAL_WIDTH / 2.0
    shifted_y = wy + REAL_HEIGHT / 2.0

    # Convert to pixel coordinates
    px = int(shifted_x / RESOLUTION)
    py = int(shifted_y / RESOLUTION)

    # Flip Y-axis because image coordinates grow downward
    py = IMG_H - 1 - py
    return px, py


def draw_wall(x1, y1, x2, y2):
    """
    Draw a wall line in the occupancy grid.
    Value 0 = occupied.
    Thickness = 3 pixels (simulate wall width).
    """
    p1 = world_to_pixel(x1, y1)
    p2 = world_to_pixel(x2, y2)
    cv2.line(image, p1, p2, 0, 3)


# === 3. Copy wall definitions from simulator.py ===

# Outer boundary walls
draw_wall(-5, -5, 5, -5)
draw_wall(5, -5, 5, 5)
draw_wall(5, 5, -5, 5)
draw_wall(-5, 5, -5, -5)

# Inner square obstacle
draw_wall(1.0,  1.0,  2.0,  1.0)
draw_wall(2.0,  1.0,  2.0,  2.0)
draw_wall(2.0,  2.0,  1.0,  2.0)
draw_wall(1.0,  2.0,  1.0,  1.0)


# === 4. Save PGM map image ===
print("Generating map.pgm ...")
cv2.imwrite("sim_map.pgm", image)


# === 5. Generate Nav2 YAML metadata file ===
yaml_content = f"""image: sim_map.pgm
mode: trinary
resolution: {RESOLUTION}
origin: [{-REAL_WIDTH/2.0}, {-REAL_HEIGHT/2.0}, 0.0]
negate: 0
occupied_thresh: 0.65
free_thresh: 0.196
"""

print("Generating map.yaml ...")
with open("sim_map.yaml", "w") as f:
    f.write(yaml_content)

print("Done! Check sim_map.pgm and sim_map.yaml under the maps/ directory.")
