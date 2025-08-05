from random import uniform as ruf
from time import sleep

from tqdm import tqdm

from ..core.chat import send_sms_message
from ..core.cursor import click_relative, key_press, swipe
from ..core.graphic import click_with_image, find_all_image, img_is_visible
from ..core.menu_nav import main_to_create, main_to_proc, to_main
from ..core.utils import get_abbreviation
from ..social.gift import auto_receive_gift, collect_spilled_item, spilled_bag


def select_cat(type='bow'):
    """
    Choosing the category of the item to craft
    """
    abbr_path = 'asset/constant/weapon_abbr.txt'

    type = get_abbreviation(type.lower(), abbr_path)

    while not img_is_visible(f'asset/images/smith/{type}.png',
                             confidence=0.9):
        swipe((51, 78), (51, 30))
        sleep(0.5)


def auto_craft_adv(limit=35):
    for _ in range(limit):
        click_relative(73, 73)  # body armor
        click_relative(72, 24)  # body armor all
        click_relative(22, 80)  # create
        click_relative(51, 81)  # start creation
        sleep(ruf(4, 5))
        click_relative(49, 79, alpha=5, beta=2)  # complete


def store_2s_eq(storage_pos=3):
    from asset.constant.config import DEPOSIT_POS
    from asset.constant.proc import SWIPE_END, SWIPE_START

    key_press('f')

    # Deposit
    click_relative(49, 53)

    while not img_is_visible('asset/images/bag/deposit_bag.png'):
        sleep(1)

    click_relative(*DEPOSIT_POS[storage_pos-1])  # Index start from 0
    click_relative(81, 72)
    sleep(1)
    if not img_is_visible('./asset/images/smith/2_slot.png'):
        swipe(SWIPE_START, SWIPE_END)
    while img_is_visible('./asset/images/smith/2_slot.png'):
        click_with_image('./asset/images/smith/2_slot.png')

        # Deposit
        click_relative(9, 30)
        # Ok
        click_relative(50, 84)


def calculate_cloth_needed(mat, point_per_item=40, mat_per_item=35, point_returned_per_discard=0.5) -> float:
    # Calculate how many items can be crafted with the given bird wings
    items_craftable = mat // mat_per_item

    # Calculate the total cloth needed for crafting the items
    total_cloth_needed = items_craftable * point_per_item

    # Calculate the cloth returned from discarding the items
    total_cloth_returned = items_craftable * point_returned_per_discard

    # Calculate the net cloth required
    net_cloth_needed = total_cloth_needed - total_cloth_returned

    return net_cloth_needed


def check_for_spilled_bag() -> bool:
    """
    Check if the bag is spilled.
    Returns True if the bag is spilled, otherwise False.
    """
    to_main()
    key_press('i')  # open bag
    sleep(1)

    empty_slots = find_all_image('asset/images/bag/empty_bag_slot.png',
                                 49, 16, 97, 90)
    return len(empty_slots) < 20


def auto_craft_and_proc_adv(bwing_stk=1000, max_eq=35, gift_limit=99,
                            deposit_pos=3, style=False, hardcode=False):
    from .proc import proc_eq
    total_adv = bwing_stk * 99 // 35
    crafted_adv = 0
    spilled_item = False

    while crafted_adv < total_adv:
        for _ in range(8):
            if crafted_adv >= total_adv:
                return

            main_to_create()
            select_cat('arm')

            # crafted max_eq items
            auto_craft_adv(max_eq)
            crafted_adv += max_eq

            main_to_proc()

            if proc_eq(max_eq, style, hardcode) is False:
                send_sms_message('2 slot detected', 'congrats')
                to_main()
                store_2s_eq(deposit_pos)

                main_to_proc()
                proc_eq(max_eq, style, hardcode)

        if spilled_item:
            collect_spilled_item()

        auto_receive_gift(gift_limit)
        sleep(1)
        spilled_item = check_for_spilled_bag()
