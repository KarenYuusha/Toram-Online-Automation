import math
import os
import re
from random import uniform as ruf
from time import sleep, time

import pyautogui as gui
from tqdm import tqdm

from asset.constant.config import ITEM_NAME
from asset.constant.proc import SWIPE_END, SWIPE_START

from ..core.chat import send_sms_message
from ..core.cursor import click_relative, key_press, swipe, move_to
from ..core.graphic import (click_with_image, get_img_coordinate,
                            img_is_visible, tesseract_ocr, waiting_for_image)
from ..core.menu_nav import is_main_screen, main_to_mailbox, to_main
from ..core.utils import find_closest_match
from ..smith.proc import click_grid_pos, filtered_bag
from ..core.coordinate import convert_to_relative

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
                        'receiving bug', f'received {received_count} out of {limit}'
                    )

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
    # Add .png extension if not present
    if not file_name.lower().endswith('.png'):
        file_name = f'asset/images/user/{file_name}.png'

    # Check if the file exists
    if not os.path.exists(file_name):
        raise FileNotFoundError(f"File does not exist: {file_name}")

    return file_name


def find_usr_pos(user_name, time_out=20, type='friend'):
    start_time = time()

    # Ensure the filename ends with .png
    if not user_name.lower().endswith('.png'):
        user_name += '.png'

    if not os.path.exists(user_name):
        raise FileNotFoundError(f"User image does not exist: {user_name}")

    sleep(0.7)
    while not img_is_visible(user_name, 30, 26, 65, 95):
        if time() - start_time > time_out:
            raise TimeoutError(
                f"User '{user_name}' not found after {time_out} seconds.")
        if not img_is_visible('asset/images/social/send_gift_pos.png'):
            start_time = time()
            click_relative(*GIFT_POS[type])
        swipe((24, 89), (24, 35))
        sleep(0.3)

    return get_img_coordinate(user_name, confidence=0.9)


def find_item_pos(item_name='bird wing', item_limit=100, starter_pos=(0, 0, 0)):
    if not item_name:
        click_grid_pos(0, 0)
        return (0, 0, 0)

    if starter_pos[0] != 0:
        swipe(SWIPE_START, SWIPE_END)

    scroll_limit = math.ceil(item_limit / (4 * 5))
    for scroll in range(starter_pos[0], scroll_limit):
        row_start = starter_pos[1] if scroll == starter_pos[0] else 0
        for row in range(row_start, 4):
            col_start = starter_pos[2] if scroll == starter_pos[0] and row == row_start else 0
            for col in range(col_start, 5):
                cur_item_pos = 20 * scroll + 5 * row + col
                if cur_item_pos >= item_limit:
                    return None

                click_grid_pos(row, col)
                cur_item_name = find_closest_match(
                    tesseract_ocr(3, 60, 31, 66.5), ITEM_NAME)
                cur_item_name = cur_item_name.lower().strip()

                if cur_item_name == item_name.lower():
                    return (scroll, row, col)

        if scroll < scroll_limit - 1:
            swipe(SWIPE_START, SWIPE_END)

    return None


def auto_gift_ocr(user_name, item_name='bird wing', quantity=50, bag_limit=100,
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


def auto_gift_ocr_99(user_name, item_name='bird wing', quantity=50, bag_limit=100,
                     type='friend') -> int:
    count = 0

    def get_to_item(scroll, row, col):
        for _ in range(scroll):
            swipe(SWIPE_START, SWIPE_END)
        click_grid_pos(row, col)

    def gifting(first_iter=False):
        nonlocal user_pos, item_pos, count
        click_relative(73, 51)  # send gift
        click_relative(*GIFT_POS[type])

        while not img_is_visible('asset/images/social/send_gift.png'):
            sleep(0.2)

        if first_iter:
            user_pos = find_usr_pos(user_name)
            sleep(0.1)

        click_relative(*user_pos, converted=True)
        click_relative(55, 50)  # attach

        if first_iter:
            filtered_bag('collectible')

        item_pos = find_item_pos(item_name, bag_limit, starter_pos=item_pos)

        stack = ''
        start_time = time()
        stack = tesseract_ocr(35, 59, 45, 68, number_only=True)
        while stack == '':
            if time() - start_time > 5:  # 5 seconds
                stack = 1
                break

            sleep(0.5)
            stack = tesseract_ocr(35, 59, 45, 68, number_only=True)
        try:
            stack = int(re.findall(r'\d+', stack)[0])
        except IndexError:
            stack = 1
        if stack < 99:
            return False  # signal to stop gifting
        click_grid_pos(item_pos[1], item_pos[2])

        click_relative(71, 44)  # max amount
        click_relative(50, 72)  # select
        click_relative(29, 44)  # confirm
        click_relative(49, 91)  # send gift
        while not img_is_visible('asset/images/social/ok.png'):
            sleep(0.1)
        click_relative(49, 87)  # ok
        count += 1
        while not img_is_visible('asset/images/social/present.png', 55, 77, 59, 84):
            sleep(0.1)
        return True  # successful gift

    type = find_closest_match(type, GIFT_POS.keys())
    user_name = ensure_png(user_name)

    user_pos = None
    item_pos = (0, 0, 0)

    main_to_mailbox()

    if not gifting(first_iter=True):
        return count  # stop immediately if not enough items

    quantity -= 1

    for _ in range(quantity):
        if not gifting():
            break  # stop if item stack drops below 99
    return count


def auto_gift_obj_99(user_name, item_path=None, quantity=50, bag_limit=100,
                     type='friend') -> int:
    count = 0

    def gifting(first_iter=False):
        nonlocal user_pos, item_pos, count
        click_relative(73, 51)  # send gift
        while not img_is_visible('asset/images/social/send_gift.png'):
            sleep(0.1)
        click_relative(*GIFT_POS[type])

        while not img_is_visible('asset/images/social/send_gift.png'):
            sleep(0.1)

        if first_iter:
            user_pos = find_usr_pos(user_name)
            sleep(0.1)

        click_relative(*user_pos, converted=True)
        while not img_is_visible('asset/images/social/send_gift.png'):
            sleep(0.1)
        click_relative(55, 50)  # attach

        # if first_iter:
        #     filtered_bag('collectible')

        sleep(0.1)
        item_pos = get_img_coordinate(
            item_path, confidence=0.96)
        swipe_count = 0
        while not item_pos:
            if swipe_count == 3:
                return False
            swipe(SWIPE_START, SWIPE_END)
            item_pos = get_img_coordinate(
                item_path, confidence=0.95)
            swipe_count += 1
            sleep(0.3)

        if item_pos:
            item_pos = convert_to_relative(*item_pos)
            click_relative(*item_pos)
            sleep(0.01)
            click_relative(*item_pos, duration=0.1)
        else:
            return False

        click_relative(71, 44, duration=0.15)  # max amount
        click_relative(50, 72, duration=0.1)  # select
        click_relative(29, 44, duration=0.1)  # confirm
        click_relative(49, 91, duration=0.15)  # send gift

        start_time = time()
        while not img_is_visible('asset/images/social/ok.png'):
            if start_time > 5:
                return False
            sleep(0.1)
        print('before present')
        print(start_time)
        count += 1
        start_time = time()
        while not img_is_visible('asset/images/social/present.png', 55, 77, 59, 84):
            if start_time > 5:
                return False
            click_relative(49, 87)  # ok
            sleep(0.1)
        return True  # successful gift

    type = find_closest_match(type, GIFT_POS.keys())
    user_name = ensure_png(user_name)

    user_pos = None
    item_pos = None

    main_to_mailbox()

    if not gifting(first_iter=True):
        return count  # stop immediately if not enough items

    quantity -= 1

    for _ in range(quantity):
        if not gifting():
            break  # stop if item stack drops below 99
    return count
