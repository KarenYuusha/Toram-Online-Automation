import math
from random import uniform as ruf
from time import sleep, time

import pyautogui as gui
from tqdm import tqdm

from asset.constant.config import ITEM_NAME
from asset.constant.proc import SWIPE_END, SWIPE_START

from ..core.chat import send_sms_message
from ..core.cursor import click_relative, key_press, swipe
from ..core.graphic import (click_with_picture, get_img_coordinate,
                            img_is_visible, tesseract_ocr)
from ..core.menu_nav import is_main_screen, main_to_mailbox, to_main
from ..core.utils import find_closest_match
from ..smith.proc import click_grid_pos, filtered_bag

GIFT_POS = {
    'party': (50, 34),
    'guild': (50, 60),
    'friend': (50, 84)
}


def auto_receive_gift(limit=100) -> None:
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
                    send_sms_message(
                        'receiving bug', f'received {received_count} out of {limit}')

                return
            sleep(0.5)

        click_relative(78, 28)  # receive
        click_relative(50, 88)  # receive
        received_count += 1


def spilled_bag() -> bool:
    to_main()
    key_press('i')  # open bag
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


def ensure_png(file_name):
    if not file_name.lower().endswith('.png'):
        file_name = f'asset/images/user/{file_name}.png'
    return file_name


def find_usr_pos(user_name, timeout=120):
    start_time = time()

    # Ensure the filename ends with .png
    if not user_name.lower().endswith('.png'):
        user_name += '.png'

    sleep(1)
    while not img_is_visible(user_name, 30, 26, 65, 95):
        if time() - start_time > timeout:
            raise TimeoutError(
                f"User '{user_name}' not found after {timeout} seconds.")
        swipe((24, 89), (24, 35))
        sleep(0.3)

    return get_img_coordinate(user_name, confidence=0.9)


def find_item_pos(item_name='bird wing', item_limit=100):
    if not item_name:
        click_grid_pos(0, 0)
        return (0, 0, 0)
    scroll_limit = math.ceil(item_limit / (4 * 5))
    for scroll in range(scroll_limit):
        for row in range(4):
            for col in range(5):
                cur_item_pos = 20 * scroll + 5 * row + col
                if cur_item_pos >= item_limit:
                    return None
                click_grid_pos(row, col)
                cur_item_name = find_closest_match(
                    tesseract_ocr(3, 60, 31, 66.5), ITEM_NAME)
                cur_item_name = cur_item_name.lower().strip()
                if cur_item_name == item_name.lower():
                    return (scroll, row, col)
    return None


def auto_gift(user_name, item_name='bird wing', quantity=50, bag_limit=100,
              item_type='collectible', type='friend'):
    def get_to_item(scroll, row, col):
        for _ in range(scroll):
            swipe(SWIPE_START, SWIPE_END)
        click_grid_pos(row, col)

    def gifting(first_iter=False):
        nonlocal user_pos, item_pos
        click_relative(73, 51)  # send gift
        click_relative(*GIFT_POS[type])

        if first_iter:
            user_pos = find_usr_pos(user_name)
            sleep(0.1)

        click_relative(*user_pos, converted=True)
        click_relative(55, 50)  # attach

        if first_iter:
            filtered_bag(item_type)
            item_pos = find_item_pos(item_name, bag_limit)
        else:
            get_to_item(*item_pos)

        click_grid_pos(item_pos[1], item_pos[2])
        click_relative(71, 44)  # max amount
        # (65, 44) increase 1
        # (34, 44) decrease 1
        click_relative(50, 72)  # select
        click_relative(29, 44)  # confirm
        click_relative(49, 91)  # send gift
        while not img_is_visible('asset/images/social/ok.png'):
            sleep(0.1)
        click_relative(49, 87)  # ok
        while not img_is_visible('asset/images/social/present.png', 55, 77, 59, 84):
            sleep(0.1)

    type = find_closest_match(type, GIFT_POS.keys())
    user_name = ensure_png(user_name)

    user_pos = None
    item_pos = None

    main_to_mailbox()
    gifting(first_iter=True)
    quantity -= 1
    for _ in range(quantity):
        gifting()
