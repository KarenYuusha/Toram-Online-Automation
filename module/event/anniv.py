from time import sleep
import random

from asset.constant.config import ANNIHILATOR, ASURA

from ..core.battle import boss_is_dead, player_is_dead, reviving
from ..core.cursor import click_relative, key_press, key_press_and_release
from ..core.graphic import click_with_picture, img_is_visible, img_is_visible_grayscale
from ..core.menu_nav import check_stamp_card
from ..core.menu_nav import is_main_screen
from ..core.menu_nav import check_stamp_card

ANNIHILATOR = str(ANNIHILATOR)
ASURA = str(ASURA)
keys = ['w', 'a', 's', 'd']

def to_battle() -> None:
    check_stamp_card()
    
    while not img_is_visible_grayscale('asset/images/anniv/arena_entry.png'):
        while not img_is_visible_grayscale('asset/images/battle/target_list.png'):
            key_press('tab')
            sleep(0.4)
        
            if img_is_visible_grayscale('asset/images/anniv/arena_entry.png'):
                break
            
        # ex arena entry
        click_relative(79, 42)
        click_relative(79, 42)
        sleep(1)
    
    click_relative(49, 45) # ex arena entry
    sleep(0.4)
    
    key_press('esc')
    
    while not img_is_visible_grayscale('asset/images/anniv/im_ready.png'):
        sleep(0.3)
    
    click_relative(76, 83) # im ready

def combo() -> None:
    raise NotImplementedError

def battle() -> None:
    def starter_combo() -> None:
        try:
            combo()
        except NotImplementedError:
            key_press(ANNIHILATOR)
            sleep(1)
            key_press(ASURA)
    
    def random_key_press():
        global keys
        
        key = random.choice(keys)
        duration = random.randint(1, 2)
        key_press_and_release(key, duration)
    
    # loading to game
        while not img_is_visible('asset/images/anniv/crystal.png'):
            sleep(1)
    reward_img_path = 'asset/images/anniv/quest_reward.png'
    
    while not is_main_screen():
        sleep(0.3)
    
    # go near the crystal
    key_press_and_release('w', 3)
    key_press_and_release('d', 2.8)
    # key_press_and_release_backup('w', 4) in case the above does not work
    
    key_press('f')
    starter_combo()
    dead = False
    
    sleep(0.2)
    key_press('tab')
    
    while is_main_screen():
        count = 0
        # check if player is dead
        if player_is_dead():
            reviving()
            key_press('f')
            dead = True

        if dead:
            starter_combo()
            dead = False
            key_press('tab')
            
        # while boss_is_dead():
        #     # finish the battle
        #     if not is_main_screen():
        #         break
            
        #     key_press('tab')
        #     key_press('tab')
        
        click_relative(75, 18) # click the boss
        click_relative(75, 18)
        
        flag = False
        while not boss_is_dead():
            # if not is_main_screen():
            #     break
            click_relative(75, 18) # click the boss
            click_relative(75, 18)
            
            count  += 1
                
            if count == 30:
                for _ in range(4):
                    random_key_press()
                        
                    if not is_main_screen() or boss_is_dead():
                        flag = True
                        break
            if flag:
                break
        defeated_boss += 1
    for _ in range(3):
        key_press('esc')
    sleep(0.5)
    if img_is_visible('asset/images/anniv/quest_reward.png'):
        click_relative(50, 86)
        click_relative(50, 86)
    
    count = 0
    while not is_main_screen():
        sleep(0.5)
        count += 1
        if img_is_visible_grayscale('asset/images/anniv/quest_reward.png'):
            click_relative(50, 86)
            count = 0 
        if count > 50:
            check_stamp_card()
            count = 0
            count = 0 
        if count > 50:
            check_stamp_card()
            count = 0
