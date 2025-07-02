import math

from tqdm import tqdm

from asset.constant.proc import *

from ..core.cursor import click_relative, swipe
from ..core.graphic import (detect_blue, find_all_image, grab_image_in,
                            img_is_visible)
from ..core.utils import find_closest_match

category_dict = {
        "all": 0,
        "metal": 1,
        "cloth": 2,
        "beast": 3,
        "wood": 4,
        "medicine": 5,
        "mana": 6
    }

def filtered_bag(selected_type='collectible', dev=False) -> None:
    """
    Ensure only the selected bag is on by toggling states.
    
    Args:
        selected_type (str): The type of bag to enable ("collectible", "tool", "equipment").
                             All other bags will be disabled.
        dev (bool): Developer mode flag to show images within region.
    """
    # the first 4 coordinate is bbox, rest is center
    bag_configs = {
        "collectible": (82, 90, 98, 98, 90, 94),
        "tool": (65, 90, 81, 98, 70, 94),
        "equipment": (48, 90, 65, 98, 58, 94),
    }
    
    selected_type = find_closest_match(selected_type, bag_configs.keys())
    if selected_type not in bag_configs:
        raise ValueError(f"Invalid bag type: {selected_type}. Valid options are: {list(bag_configs.keys())}")
    
    def toggle_bag(left, top, right, bottom, click_x, click_y, flag=True) -> None:
        """
        Toggle the state of a specific bag.
        
        Args:
            left (float): Left relative coordinate.
            top (float): Top relative coordinate.
            right (float): Right relative coordinate.
            bottom (float): Bottom relative coordinate.
            click_x (float): X relative coordinate to click.
            click_y (float): Y relative coordinate to click.
            flag (bool): True to turn on, False to turn off.
        """
        captured_image = grab_image_in(left, top, right, bottom, dev=dev)
        is_blue_detected = detect_blue(captured_image)
        should_click = (flag and not is_blue_detected) or (not flag and is_blue_detected)
        if should_click:
            click_relative(click_x, click_y)

    # Toggle each bag based on the selected type
    for bag_type, coords in bag_configs.items():
        toggle_bag(*coords, flag=(bag_type == selected_type))

def click_grid_pos(row, col, base_x=INITIAL_X, base_y=INITIAL_Y) -> None:
    x = base_x + col * COL_WIDTH
    y = base_y + row * ROW_HEIGHT
    click_relative(x, y)

def proc_eq(item_limit=35, style=False, hard_code=True, dev=False) -> bool:
    """
    Process equipment in the bag.
    return False if 2 slot equipment is detected
    Args:
        item_limit (int): Maximum number of items to process, default is 35.
        style (bool): If True, show a progress bar.
        hard_code (bool): If True, use hard-coded grid positions, otherwise use image detection.
        dev (bool): If True, enable debugging mode with image detection.
    """
    scroll_limit = math.ceil(item_limit / (4 * 5))  # 4 rows and 5 columns
    filtered_bag(selected_type='equipment')
    
    
    click_relative(39, 36) # Switch to process all items

    # Create a progress bar if style is True
    progress_bar = tqdm(total=item_limit, desc="Processing Items") if style else None

    for scroll in range(scroll_limit):
        if img_is_visible('asset/images/smith/2_slot.png'):
            if style:  # Close the progress bar if active
                progress_bar.close()
            return False
        
        if hard_code:
            remaining_items = item_limit - (scroll * 20)
            remaining_rows = (remaining_items + 4) // 5  # compute how many full rows are left
            
            for row in range(4):
                if row == remaining_rows and scroll == scroll_limit - 1:
                    break  # stop early if no full rows left
                
                for col in range(5):
                    click_grid_pos(row, col)
                    if style:
                        progress_bar.update(1)  # Update progress bar for each click
        
        # use matching template
        else:
            res = find_all_image('asset/images/smith/armor.png', 49, 16, 97, 90, dev=dev)
            for _ in res:
                click_relative(*_, converted=True, duration=0.3)
                if style:
                    progress_bar.update(1)
            
            # early stopping
            if len(res) < 20:
                break
            
        if scroll < scroll_limit - 1:
                swipe(SWIPE_START, SWIPE_END)

    # Process items and confirm
    click_relative(23, 36)  # process
    click_relative(50, 85)  # receive
    click_relative(49, 80)  # OK

    if style:  # Close the progress bar if active
        progress_bar.close()

    return True

# def get_current_category() ->str:
#     """
#     finding the current category in processing menu
    
#     Returns:
#         str: current category
#     """
#     cur_cat = find_text(2, 41, 13, 46.9)
#     # normalise the text
#     cur_cat = cur_cat.replace('\n', '').replace('.', '').lower()
#     if cur_cat == '' or cur_cat == 'all':
#         cur_cat = 'all'
    
#     return cur_cat

# def calculate_clicks(from_category: str, to_category: str) -> int:
#     """
#     calculate the number of clicks needed to reach the desired category
    
#     Parameters:
#         from_category (str): current category
#         to_category (str): desired category
#     Returns:
#         int: number of clicks needed
#     """
#     from_index = category_dict[from_category]
#     to_index = category_dict[to_category]
    
#     if from_index > to_index:
#         return abs(from_index - (to_index + 6)) + 1
#     else:
#         return to_index - from_index

# def proc_mats_by_category(category_list):
#     category_list = [cat.lower() for cat in category_list]
#     current_category = get_current_category()
#     category_list = sorted(category_list, key=lambda x: calculate_clicks(current_category, x))
    
#     toggle_bag(collectibles=True)
    
#     # switch to process all
#     click_relative(39, 36)
    
#     for category in category_list:
        
#         # switch to correspoding category
#         for click in range(calculate_clicks(get_current_category(), category)):
#             click_relative(8, 36)
            
#         last_mats = ''
#         last_quantity = ''
        
#         for scroll in range(5):
#             x, y = 53, 26
            
#             for row in range(4):
                
#                 tmp_y = y + row * 17
                
#                 for col in range(5):
#                     tmp_x = x + col * 10
                    
#                     click_relative(tmp_x, tmp_y)
                    
#                     # name of the material in the current slot
#                     cur_mats = find_text(3, 60, 38, 66)
#                     cur_mats = cur_mats.replace('\n', '').replace('.', '').lower()
                    
#                     cur_mats_quantity = find_text(30, 60, 45, 66, number_only=True)
#                     cur_mats_quantity = cur_mats_quantity.replace('\n', '').replace('.', '')
#                     cur_mats_quantity = int(cur_mats_quantity) if cur_mats_quantity else 0
                
#             swipe((48, 76), (47, 23))  
            
#             # last scroll reached
#             if scroll == 4:
#                 break
        
#         # process        
#         click_relative(23, 36)
#         # receive!
#         click_relative(50, 85)
#         # ok
#         click_relative(49, 80)

