from time import sleep

from .cursor import click_relative, key_press, key_press_and_release
from .graphic import click_with_image, img_is_visible
from .menu_nav import check_stamp_card


def player_is_dead() -> bool:
    return img_is_visible('./asset/images/battle/defeated.png')


def reviving() -> None:
    """
    check if the player is dead and trying to click struggle
    """
    while player_is_dead():
        while img_is_visible('asset/images/battle/revive_now.png'):
            # click struggle
            click_relative(88, 85)
            sleep(0.3)
        # revive here
        click_relative(85, 37)
        sleep(0.5)


def boss_is_dead() -> bool:
    return not img_is_visible('asset/images/battle/boss.png', 65, 6, 84, 70)


def is_finish_or_dead(finish='', dead='asset/images/battle/defeated.png') -> bool:
    """
    check if the battle is finished or the player is dead
    """
    if finish:
        return img_is_visible(finish) or img_is_visible(dead)
    else:
        return img_is_visible(dead)
