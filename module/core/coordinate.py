import os
from typing import List, Tuple

from pynput.keyboard import Key
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Button, Controller
from pynput.mouse import Listener as MouseListener

from .cursor import convert_to_relative

coordinate_list = []
mouse_listener = None

def on_click(x, y, button, pressed, relative=True) -> bool:
    """
    Handle mouse click events.

    Args:
        x (float): The x-coordinate of the mouse click.
        y (float): The y-coordinate of the mouse click.
        button (Button): The mouse button that was clicked.
        pressed (bool): Whether the mouse button was pressed.
        relative (bool): Whether to convert coordinates to relative.
    """
    # Check for left click
    if button == button.left and pressed:
        if relative:
            x, y = convert_to_relative(x, y)

        coordinate_list.append((x, y))
        print(f"Left click detected at ({x}, {y})")

def on_key_press(key) -> bool:
    """
    Handle key press events to stop the listeners when 'q' is pressed.

    Args:
        Key: The key that was pressed.
    """
    if not hasattr(key, 'char'):
        return  # Ignore non-character keys

    if key.char == 'q':  # Stop listener if 'q' is pressed
        print('Stopping listeners due to "q" key press.')
        mouse_listener.stop()  # Explicitly stop the mouse listener
        return False  # Stop the keyboard listener

def start_mouse_listener(relative=True) -> None:
    """
    Start the mouse listener to track mouse click events.

    Args:
        Relative (bool): Whether to convert coordinates to relative.
    """
    global mouse_listener
    mouse_listener = MouseListener(on_click=lambda x, y, button, pressed: on_click(x, y, button, pressed, relative=relative))
    mouse_listener.start()
    mouse_listener.join()

def start_keyboard_listener() -> None:
    """
    Start the keyboard listener to detect 'q' key press for stopping.
    """
    with KeyboardListener(on_press=on_key_press) as listener:
        listener.join()

def save_coordinates_to_file(coordinates, filename) -> None:
    """
    Save the list of coordinates to a file.

    Args:
        Coordinates (List[Tuple[float, float]]): The list of coordinates to save.
        Filename (str): The file to save the coordinates in.
    """
    with open(filename, 'w') as file:
        for coord in coordinates:
            file.write(f"{coord[0]}, {coord[1]}\n")

def start_record_coordinates(filename: str='a.txt', relative: bool=False) -> None:
    """
    Start recording cursor coordinates and save them to a file.
    Press 'q' to stop recording.

    Args:
        Filename (str): The file to save the coordinates in. Defaults to 'asset/coordinate/a.txt'.
        Relative (bool): Whether to convert coordinates to relative position. Defaults to False.
    """
    global coordinate_list, mouse_listener
    coordinate_list = []

    # Start the mouse and keyboard listeners concurrently
    from threading import Thread
    mouse_thread = Thread(target=start_mouse_listener, args=(relative,))
    keyboard_thread = Thread(target=start_keyboard_listener)

    mouse_thread.start()
    keyboard_thread.start()

    mouse_thread.join()
    keyboard_thread.join()

    # Save coordinates to file
    cur_dir = os.getcwd()
    file_name = 'asset/coordinate/' + filename
    filename = os.path.join(cur_dir, file_name)

    save_coordinates_to_file(coordinate_list, filename)

def read_coordinates_from_file(filename = 'a.txt') -> List[Tuple[float, float]]:
    """
    Read coordinates from a file.

    Args:
        Filename (str): The file to read the coordinates from. Defaults to 'a.txt'.

    Returns:
        List[Tuple[float, float]]: The list of coordinates read from the file.
    """
    coordinates: List[Tuple[float, float]] = []
    
    with open(filename, 'r') as file:
        for line in file:
            x, y = map(float, line.strip().split(','))
            coordinates.append((x, y))
            
    return coordinates