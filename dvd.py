import ctypes
import random
import time

from pynput import mouse as ms
from pynput import keyboard as kb

__doc__ = """Moves the mouse emulating the bouncing DVD screensaver motion."""

# Set the step size for the mouse movement
STEP_SIZE = 0.5

# Set the delay for the mouse movement (in seconds)
DELAY = 0.0001

# Create a flag to track if the EXIT_KEY is pressed
EXIT_FLAG = False

# Set the key to exit the program
EXIT_KEY = kb.Key.esc


def get_screen_dimensions() -> tuple[int, int]:
    """Returns the screen dimensions in pixels."""
    
    # Get the screen dimensions using ctypes
    user32 = ctypes.windll.user32
    return (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))


def main() -> None:
    # Get screen dimensions
    screen_x, screen_y = get_screen_dimensions()
    
    # Set the initial position and direction of the mouse randomly
    mouse_x, mouse_y = random.randint(0, screen_x), random.randint(0, screen_y)

    direction_x = random.choice([-1, 1])  # -1 or 1 for moving horizontally
    direction_y = random.choice([-1, 1])  # -1 or 1 for moving vertically

    # Initialize the mouse controller
    mouse = ms.Controller()
    
    # Start listening to the keyboard
    with kb.Listener(on_press=key_to_exit) as listener:
        # Bouncing DVD screensaver motion
        while not EXIT_FLAG:
            # Move the mouse
            mouse_x += STEP_SIZE * direction_x
            mouse_y += STEP_SIZE * direction_y

            # Check if the mouse hit the screen boundaries
            if mouse_x <= 0 or mouse_x >= screen_x:
                direction_x *= -1  # Change direction
            if mouse_y <= 0 or mouse_y >= screen_y:
                direction_y *= -1  # Change direction

            # Move the mouse to the new position
            mouse.position = (mouse_x, mouse_y)

            # Add a delay to control the speed of the motion
            time.sleep(DELAY)

    # Stop listening to the keyboard
    listener.stop()


# Function to handle key press event to exit the program
def key_to_exit(key):
    global EXIT_FLAG
    if key == EXIT_KEY:
        EXIT_FLAG = True
        return False  # Stop listener


if __name__ == "__main__":
    main()