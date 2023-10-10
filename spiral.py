import math
import time
import ctypes

from pynput.mouse import Controller


def main():
    # Get screen dimensions and calculate the center
    user32 = ctypes.windll.user32
    screen_x, screen_y = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    center_x, center_y = screen_x // 2, screen_y // 2

    # Constants for the spiral motion
    num_turns = 20  # Number of turns in the spiral
    total_steps = 5000  # Total steps to complete the spiral

    # Calculate step size and angle increment for the spiral
    step_size = min(screen_x, screen_y) / total_steps
    angle_increment = (2 * math.pi * num_turns) / total_steps

    # Initialize the mouse controller
    mouse = Controller()

    # Move the mouse in a flower spiral pattern
    for step in range(total_steps):
        # Calculate the position of the mouse based on the spiral pattern
        radius = step * step_size
        angle = step * angle_increment
        x = int(center_x + radius * math.cos(angle))
        y = int(center_y + radius * math.sin(angle))

        # Move the mouse to the calculated position
        mouse.position = (x, y)

        # Add a slight delay to control the speed of the spiral motion
        time.sleep(0.001)
        
        
if __name__ == "__main__":
    main()
