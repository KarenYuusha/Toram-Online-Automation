from random import uniform as ruf
from time import sleep

import pyautogui as gui
from tqdm import tqdm

from ..core.chat import send_sms_message
from ..core.cursor import click_relative, key_press, swipe
from ..core.graphic import click_with_picture, img_is_visible
from ..core.menu_nav import is_main_screen, main_to_mailbox, to_main
from ..smith.proc import filtered_bag


def auto_receive_gift(limit= 100) -> None:
    """
    starting from main screen, receive gift and return to the main screen
    """
    main_to_mailbox()
    
    # receive gift
    click_relative(74, 66)
    
    # keep track of the number of received gift
    received_count = 0
    
    for iter in range(limit):
        count = 0
        
        # early stopping when cannot receive gift
        while not img_is_visible('./asset/images/social/gift_box.png', 13, 33, 18, 40):
            count += 1
            if count == 10:
                if received_count < 0.9 * limit:
                    send_sms_message('receiving bug', f'received {received_count} out of {limit}')
                    
                return 
            sleep(0.5)
        
        click_relative(78, 28) # receive 
        click_relative(50, 88) # receive
        received_count += 1

def spilled_bag() -> bool:
    to_main()
    key_press('i') # open bag
    sleep(1)
    
    if img_is_visible('./asset/images/bag/spilled_bag.png'):
        return True

    return False

def collect_spilled_item(equipment=False, tool=False, 
                      collectible=True) -> None:
    to_main()
    key_press('i')
    filtered_bag(equipment, tool, collectible)
    
    click_relative(23, 45)
    click_relative(53, 25)
    click_relative(8, 26)
    
# in development
# def auto_send_gift(item_name=None, stack=1, type='friend', user_name=None) -> None:
#     if not user_name.endswith('.png'):
#         user_name = f'./asset/images/user_name/{user_name}.png'
#     main_to_mailbox()
    
#     click_relative(65, 52) # send gift
    
#     if type=='party':
#         click_relative(49, 35)
#     elif type=='guild':
#         click_relative(49, 59)
#     else:
#         click_relative(50, 85)
    
#     while not img_is_visible(user_name, 39, 26, 60, 95):
#         swipe((24, 89), (24, 35))
#         sleep(0.3)
    
#     click_with_picture(user_name, 39, 26, 60, 95)