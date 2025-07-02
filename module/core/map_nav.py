import time

import keyboard

from .cursor import click_relative, key_press
from .graphic import img_is_visible
from .menu_nav import to_main


def teleport(map_name='sofya city', delay=0.4) -> None:
    """
    Teleport to a specific map.

    Args:
        map_name (str): The name of the map to teleport to.
        delay (float): The delay between keystrokes.
    """
    def type_text(text, delay=0.1):
        for char in text:
            keyboard.write(char)
            time.sleep(delay)
    
    to_main()
    key_press('m')
    while not img_is_visible('asset/images/map_navigation/back.png', 89.5, 1, 92, 7):
        time.sleep(0.5)

    click_relative(12, 91) # World map
    click_relative(12, 76) # Region selection
    click_relative(40, 22) # Chapter
    click_relative(48, 36) # Search from map name

    type_text(map_name, delay=delay)
    key_press('enter')

    while not img_is_visible('asset/images/map_navigation/fav_map_toggle.png', 50, 45, 56, 95):
        time.sleep(0.5)

    click_relative(30, 50) # Choose the first map
    click_relative(84, 92) # Move to the map
    click_relative(48, 83) # Move with 0 spina
    
    # Wait until the map is loaded
    while not img_is_visible('asset/images/battle/target_list.png', 71, 7, 79, 10.5):
        key_press('tab')
        time.sleep(1)
        
    key_press('tab')