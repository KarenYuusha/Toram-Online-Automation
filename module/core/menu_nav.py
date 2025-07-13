from time import sleep

import pyautogui as gui

from .cursor import click_relative, key_press, swipe
from .graphic import (click_with_picture, grab_image_in, image_matching,
                      img_is_visible)


def is_main_screen() -> bool:
    """
    Check if the current screen is the main screen
    """
    from PIL import Image
    
    return image_matching(Image.open('./asset/images/menu_navigation/orb_shop.png'), grab_image_in(90, 87, 93.7, 96), remove_bg=True)

def to_main() -> None:
    """
    Navigate to main menu
    """
    if not is_main_screen():
        key_press('ESC')
        sleep(0.5)

def main_to_smith() -> None:
    """
    Navigate to smith menu
    """
    to_main()
    
    key_press('p') # Open player tab
    
    click_relative(75,  38) # Skills
    click_relative(75, 25) # Use ex skills
    
    # Click smith skills
    click_with_picture('./asset/images/menu_navigation/smith_skill.png', 4, 21, 95, 73)

def main_to_proc() -> None:
    """
    Navigate to process material menu
    """
    main_to_smith()
    click_relative(50, 60)

def main_to_ref() -> None:
    """
    Navigate to refine menu
    """
    main_to_smith()
    click_relative(74, 60)

def main_to_fill() -> None:
    """
    Navigate to fill menu
    """
    main_to_smith()
    swipe((51, 37), (5, 38))
    click_relative(66, 60) # skill

def main_to_mailbox() -> None:
    """
    Navigate to mailbox
    """
    to_main()
    
    key_press('c')
    sleep(1)
    
    # Mailbox
    click_relative(76, 80)
    sleep(0.5)

def main_to_create() -> None:
    """
    Navigate to crafting menu
    """
    main_to_smith()
    click_relative(96, 60)

def main_to_eq() -> None:
    """
    Navigate main screen to equipment page
    """
    to_main()
    key_press('p')
    click_relative(76, 52) # Equipment
    
    while not img_is_visible('asset\images\smith\combat.png'):
        sleep(0.5)

def switch_char(char_id=1, fast_mode=False) -> None:
    """
    Switch to a character based on the given ID.
    ID start from 0.
    For now only support the first 5 characters.
    Avoid using fast_mode in slow loading maps, ex: your land.
    """
    
    char_id = min(4, max(0, char_id))
    if not is_main_screen():
        to_main()
    
    key_press('p')
    
    click_relative(80, 80) # switch character
    
    while not img_is_visible('./asset/images/menu_navigation/switch.png', 14, 87, 24, 93):
        click_relative(75, 23 + 14 * char_id - 1)
        sleep(1)
    
    click_relative(20, 90) # switch
    sleep(7)

    # Wait until the main screen is loaded
    # You can remove this if you want to switch character faster
    if not fast_mode:
        while not is_main_screen():
            sleep(0.5)

def check_stamp_card() -> None:
    if img_is_visible('asset/images/misc/close_stamp_card.png'):
        click_relative(50, 91)
        sleep(0.5)
