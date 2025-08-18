import random
import time
from time import sleep
from typing import Final, Optional, Tuple, Union

import pyautogui as gui
import win32con
import win32gui
from win32gui import FindWindowEx, GetWindowRect

wnd = FindWindowEx(None, None, None, "ToramOnline")

left, top, right, bottom = GetWindowRect(wnd)

w = right - left
h = bottom - top

LEFT = left + 7
TOP = top + 30
BOTTOM = TOP + h - 35
RIGHT = LEFT + w - 15

inner_width = RIGHT - LEFT
inner_height = BOTTOM - TOP

mid_x = inner_width // 2
mid_y = inner_height // 2


def convert_to_absolute(x, y) -> Tuple[Union[int, bool], Union[int, bool]]:
    """
    Convert relative position to absolute position.

    Args:
        x (float): The relative x position.
        y (float): The relative y position.

    Returns:
        tuple: The absolute position.
    """
    pos_x = round(x/100 * inner_width) + LEFT
    pos_y = round(y/100 * inner_height) + TOP

    in_bounds: bool = (LEFT <= pos_x <= RIGHT) and (TOP <= pos_y <= BOTTOM)

    return (pos_x, pos_y) if in_bounds else (False, False)


def convert_to_relative(x, y) -> Tuple[float, float]:
    """
    Convert absolute position to relative position.

    Args:
        x (int): The absolute x position.
        y (int): The absolute y position.

    Returns:
        tuple: The relative position.
    """
    rel_x = (x - LEFT) / inner_width * 100
    rel_y = (y - TOP) / inner_height * 100

    return rel_x, rel_y


def click_relative(x, y, alpha=1, beta=1, duration=0.2, converted=False) -> None:
    """
    Clicks on a relative position of the screen.

    Args:
        x (float): The relative x position.
        y (float): The relative y position.
        alpha (int): The x (horizontal) offset.
        beta (int): The y (vertical) offset.
        duration (int): The duration of the click.
        converted (bool): Whether the position is already converted into absolute pos.
    """
    pos_x, pos_y = (x, y) if converted else convert_to_absolute(x, y)

    if pos_x is False or pos_y is False:
        return

    offset = random.randint(0, 10)
    pos_x += random.randint(-alpha * offset, alpha * offset)
    pos_y += random.randint(-beta * offset, beta * offset)

    if duration:
        gui.moveTo(pos_x, pos_y, duration=duration)

    gui.click(pos_x, pos_y)

    # To prevent double click
    sleep(0.1)


def move_to(x, y, duration=0.2) -> None:
    pos_x, pos_y = convert_to_absolute(x, y)
    gui.moveTo(pos_x, pos_y, duration=duration)


def key_press(key) -> None:
    """
    Perform a keyboard key press down then release action after a random interval.

    Args:
        key (str): The key to press.
    """
    gui.press(key, interval=random.uniform(0.1, 0.4))


def key_press_and_release(key, duration=1) -> None:
    """
    Perform a keyboard key press and release action.

    Args:
        key (str or int): The key (or code) to press.
        duration (int): The duration (second) of the key press.
    """
    gui.keyDown(key)
    sleep(duration)
    gui.keyUp(key)


def switch_to_toram(window_title="ToramOnline", run_type='notebook') -> bool:
    """
    Switch to the Toram Online window. For Jupyter Notebook, perform a click on the screen to switch.

    Args:
        window_title (str): The title of the window to switch to.
        run_type (str): The mode of operation ('normal' for direct switching, 'notebook' for screen click).

    Returns:
        bool: True if the switch was successful, False otherwise.
    """
    try:
        if run_type == 'normal':
            # Find the window handle and bring it to the foreground
            hwnd = win32gui.FindWindow(None, window_title)
            if hwnd:
                win32gui.SetForegroundWindow(hwnd)
                sleep(1)  # Allow time for the switch
                return True
            else:
                print(f"Window with title '{window_title}' not found.")
                return False

        elif run_type == 'notebook':
            # Click on the screen to switch in notebook mode
            try:
                x, y = convert_to_absolute(50, 0)
                gui.click(x, y - 10)
                sleep(1)  # Allow time for the switch
                return True
            except Exception as e:
                print(f"Error during screen click in notebook mode: {e}")
                return False

        else:
            print(
                f"Invalid run_type '{run_type}'. Valid options are 'normal' or 'notebook'.")
            return False

    except Exception as e:
        print(f"Error occurred while switching to Toram: {e}")
        return False


def exit_toram(window_title="ToramOnline", run_type='notebook') -> None:
    """
    Exit the ToramOnline application based on the specified run type.

    Args:
        window_title (str): The title of the window to close (default is "ToramOnline").
        run_type (str): The method to exit the application. 
                        Options are 'normal' (close window directly) 
                        or 'notebook' (simulate in-game exit sequence).
    """
    if run_type == 'normal':
        # Close the window directly using Win32 API
        try:
            hwnd = win32gui.FindWindow(None, window_title)
            if hwnd:
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                sleep(10)  # Allow time for the window to close
            else:
                print(f"Window with title '{window_title}' not found.")
        except Exception as e:
            print(f"Error closing window: {e}")

    elif run_type == 'notebook':
        # Simulate in-game exit sequence
        try:
            key_press('esc')  # Open the exit menu
            click_relative(50, 84)  # Click "Close App"
            click_relative(65, 85)  # Click "Confirm"
            sleep(10)  # Allow time for the app to close
        except Exception as e:
            print(f"Error performing notebook exit: {e}")

    else:
        raise ValueError(
            f"Invalid run_type '{run_type}'. Valid options are 'normal' or 'notebook'.")


def swipe(start, end, duration=0.75) -> None:
    """
    Perform a swipe gesture from the start position to the end position over a given duration.

    Parameters:
        start (Tuple[int, int]): The starting (x, y) relative coordinates of the swipe.
        end (Tuple[int, int]): The ending (x, y) relative coordinates of the swipe.
        duration (float): The duration of the swipe in seconds. Default is 0.75 seconds.
    """
    try:
        # Convert relative coordinates to absolute screen coordinates
        start_x, start_y = convert_to_absolute(*start)
        end_x, end_y = convert_to_absolute(*end)

        # Perform the swipe gesture
        gui.moveTo(start_x, start_y)
        gui.mouseDown()
        gui.moveTo(end_x, end_y, duration=duration)
        gui.mouseUp()
    except gui.FailSafeException:
        print("Failsafe triggered")
        raise

    except Exception as e:
        print(f"Error occurred while performing swipe: {e}")


def move_random() -> None:
    """
    Move random within the game window.
    """
    x = random.randint(0, inner_width)
    y = random.randint(0, inner_height)

    x += LEFT
    y += TOP

    gui.moveTo(x, y, duration=random.uniform(0.1, 0.3))
