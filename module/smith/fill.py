import re
from time import sleep

from asset.constant.config import ABILITY_SLOT_X, ABILITY_SLOT_Y, MAT_POINT

from ..core.cursor import click_relative, key_press, swipe
from ..core.graphic import click_with_picture, img_is_visible, tesseract_ocr
from ..core.menu_nav import main_to_fill, to_main


def read_tanaka(file_path):
    mats = {}
    highest_mats = 0
    formula = []
    pos_stat = []
    nega_stat = []
    with open(file_path) as f:
        for count, line in enumerate(f):
            if line == '\n':
                continue
            elif count == 0:
                for stat in line.split(','):
                    pos_stat.append(stat.split('Lv')[0].strip().lower())
            elif count == 1:
                for stat in line.split(','):
                    nega_stat.append(stat.split('Lv')[0].strip().lower())
            # total mats needed
            elif count == 4:
                pairs = re.split(r'(?<=pt),(?=\w+:)', line)
                for pair in pairs:
                    mat, point = pair.split(':')
                    mats[mat] = int(point.replace('pt', '').replace(',', ''))
            # highest mats per step
            elif count == 5:
                points = line.split(':')[1]
                highest_mats = int(points.split()[0].replace(',', ''))
            # success rate
            elif count == 6:
                continue
            # formula
            elif count > 6:
                line = re.sub(r'^\d+\.\s*', '', line)
                parts = line.split('.')
                line = '.'.join(parts[:-1]).strip()
                line = line.replace('.', '')
                line = line.replace('Add ', '')
                formula. append(line.replace('\n', '').lower())
    
    return formula, mats, highest_mats, pos_stat, nega_stat

def map_to_general(stat) -> str:
    """ Convert specific stats to a general category.
        This function only work properly with tanaka0 website.
    """
    stat = stat.lower()

    # to group multple stats in to a single category
    categories = {
        'stronger': 'dte',
        'pierce': 'attack',
        'atk': 'attack',
        'matk': 'attack',
        'stability': 'attack',
        'def': 'defense',
        'mdef': 'defense',
        'resistance': 'defense',
        'aspd': 'speed',
        'cspd': 'speed',
        'matching': 'element',
        'critical rate': 'critical',
        'critical damage': 'critical',
        'critical': 'critical',
        'accuracy': 'accuracy',
        'dodge': 'dodge',
        'natural': 'hp_mp',
        'maxhp': 'hp_mp',
        'maxmp': 'hp_mp',
        'ailment': 'special',
        'guard': 'special',
        'aggro': 'special',
        'evasion': 'special',
        'dex': 'stats',
        'int': 'stats',
        'vit': 'stats',
        'agi': 'stats',
        'str': 'stats',
    }

    for keyword, category in categories.items():
        if keyword in stat:
            return category

    return None

def get_default_custom_order():
    return [
        'element',
        'dte',
        'attack',
        'stats',
        'critical',
        'defense',
        'speed',
        'accuracy',
        'dodge',
        'hp_mp',
        'special'
    ]

def sort_stats(stats, custom_order=None):
    """ 
    sorted by custom order then by %
    stat with % will be on top
    stat within one category will be sorted alphabetically
    """
    if custom_order is None:
        custom_order = get_default_custom_order()
    
    return sorted(stats, key=lambda x: (
        custom_order.index(map_to_general(x)),  # Custom order
        '%' not in x,  # Prioritize items with '%'
        x.lower()  # Alphabetical order
    ))

def click_cat(cat) -> None:
    """
    click stat category 
    for example: enhance stats, hp/mp, attack, defense, etc
    
    Args:
        cat (str): category of stats
    """
    img_path = f'./asset/images/fill/{map_to_general(cat)}.png'
    # the stat is not in the upper half
    while not img_is_visible(img_path, 62, 15, 90, 97):
        swipe((55, 93), (55, 17))
        sleep(1)
    else:
        click_with_picture(img_path)

def select_slot(stat, sorted_stat) -> None:
    """
    select an ability slot base on the sorted priority
    
    Args:
        stat (str): stat to be filled
        sorted_stat (list): List of sorted stats by priority
    """
    try:
        idx = sorted_stat.index(stat.split('lv')[0].strip())
    except ValueError:
        raise ValueError(f"Stat '{stat}' not found in sorted_stat list.")
    
    # the stat is in the 4th slot or above
    if idx > 3:
        swipe((56, 92), (56, 50))
    click_relative(ABILITY_SLOT_X, ABILITY_SLOT_Y[idx])

def format_text(text) -> str:
    """
    Normalize the text for consistent storage and comparison.
    Update this function if the text format on Tanaka's website changes.
    
    Args:
        text (str): Text to be normalized.
    
    Returns:
        str: Normalized text.
    """
    text = text.lower()
    
    # Normalize spaces around '%' and other formatting nuances
    text = re.sub(r"\s*%\s*", "%", text)
    
    # Remove all spaces and strip leading/trailing whitespace
    return text.replace(" ", "").strip()

def increment_stat_level(level, delay=0.1) -> None:
    """
    Increment or decrement a stat by clicking a specified number of times.
    
    Args:
        level (int): The number of increments (positive) or decrements (negative).
        delay (float): Time delay between clicks, default is 0.1 seconds.
    """
    x_offset = 35 if level > 0 else 16  # X-offset for increment or decrement
    for _ in range(abs(level)):
        click_relative(x_offset, 72, duration=0.1)
        sleep(delay)
    
    # Confirm the action
    click_relative(25, 88)

def click_stat(cat, stat, tolerance=4, cache=None) -> None:
    """
    Click on a specific stat in the fill menu.
    
    Args:
        cat (str): Category of the stat (e.g., 'hp_mp', 'attack').
        stat (str): Specific stat to click on.
        tolerance (float): Total wait time before timeout, default is 4 seconds.
        cache (dict): Cache to store processed stats, default is None.
    """
    if cache is None:
        cache = {}

    image_path = f'./asset/images/fill/{cat}/{stat}.png'
    total_wait_time = 0.0

    # Check if the stat image is visible, swipe if necessary
    while not img_is_visible(image_path):
        sleep(0.5)
        if not img_is_visible(image_path) and total_wait_time==0:
            swipe((56, 92), (56, 34))
            
        total_wait_time += 0.5
        if total_wait_time > tolerance:
            raise TimeoutError(f"Failed to find the image {image_path} in the fill menu.")
    
    bbox = (52, 18, 97, 98)
    confidence = 0.93

    # special handling for 'hp_mp' category
    if cat == 'hp_mp':
        confidence = 0.96  # Adjust confidence for hp/mp due to similarity
    
    # click the stat only if not in cache
    if stat not in cache:
        click_with_picture(image_path, *bbox, confidence=confidence)
    
def confirm_stat(is_final=False) -> None:
    click_relative(25, 92) # start
    sleep(0.2)
    click_relative(49, 92) # start
    
    if is_final:
        click_relative(49, 85) # start
    sleep(5)
    
    click_relative(51, 78) # complete
    
def filling_stat(step_type: str, raw_stat: str, stat: str, stat_type: str,
                 stat_lvl: int, delay: float = 0, cache: dict = None) -> None:
    """
    Fill a stat with a specified level adjustment, using various step types.
    
    Args:
        step_type (str): Type of processing ('once', or 'one').
        raw_stat (str): Raw stat name.
        stat (str): Normalized stat name.
        stat_type (str): General category of the stat (e.g., 'attack', 'defense').
        stat_lvl (int): Level of the stat to be filled.
        delay (float): Delay between actions, default is 0.
        cache (dict): Cache to track processed stats, default is None.
    """
    if cache is None:
        cache = {}
    
    def process_stat() -> None:
        """Perform actions to select and click the correct stat."""
        select_slot(raw_stat)
        sleep(0.4)
        click_cat(raw_stat)
        sleep(1)
        if stat_type == 'dte':
            click_stat('element', stat)
        else:
            click_stat(map_to_general(raw_stat), stat)
    
    # adjust stat_lvl based on cache
    if stat in cache:
        stat_lvl -= cache[stat]
        if stat_lvl <= 0:
            raise ValueError(f"Stat '{stat}' already filled to the required level.")
    
    # process based on step type
    if step_type == 'once':
        process_stat()
        increment_stat_level(stat_lvl, delay=delay)
    elif step_type == 'one':
        flag = False
        for i in range(stat_lvl):
            if i == 1 and stat not in cache:
                cache[stat] = cache.get(stat, 0) + 1
                flag = True
            
            process_stat()
            increment_stat_level(1, delay=delay)

            if i < stat_lvl - 1:
                confirm_stat(is_final=False)
                click_relative(25, 92)  # Customize
                sleep(0.4)
    
    # update cache with the processed stat_lvl
    cache[stat] = cache.get(stat, 0) + stat_lvl - (1 if flag else 0)
    
# slot_x = 78
# fill_slot_y = [25, 39, 52, 67, 48, 62, 76, 89]

def auto_fill(formula_path, custom_order=None, check_mat=False):
    def has_enough_mats():
        to_main()
        key_press('p')
        click_relative(76, 25) # start
        click_relative(15, 93) # production
        
        missing_mats = {}
        
        for mat, point in mats.items():
            mat = mat.lower()
            cur_mat = tesseract_ocr(*MAT_POINT[mat], number_only=True)
            cur_mat = int(cur_mat.replace('.', ''))
            
            if cur_mat < point:
                missing_mats[mat] = point - cur_mat
        # no missing mats
        if missing_mats == {}:
            # check if enough limit
            limit = int(tesseract_ocr(21, 80, 29, 85, number_only=True))
            if limit < highest_mat:
                print('Not enough limit')
                return False
            return True
        else:
            print('Missing materials: ', missing_mats)
            return False
        
    formula, mats, highest_mat, pos_stat, nega_stat = read_tanaka(formula_path)
    
    if check_mat:
        if has_enough_mats() == False:
            raise ValueError("Not enough materials to fill the stats.")
    
    if custom_order is None:
        custom_order = get_default_custom_order()
    
    main_to_fill()
    click_relative(71, 25) # select 1st eq
    click_relative(26, 92) # customize
    
    sorted_pos_stats = sort_stats(pos_stat, custom_order)
    sorted_nega_stats = sort_stats(nega_stat, custom_order)
    sorted_stat = sorted_pos_stats + sorted_nega_stats
    
    cache = {}

    for idx, step in enumerate(formula):
        click_type = step.split(' ')[-1]
        stats = step.split(', ')

        click_relative(25, 92)  # customize
        sleep(0.4)

        for raw_stat in stats:
            stat_type = map_to_general(raw_stat)

            fill_stat, fill_stat_lv = raw_stat.split('lv')
            fill_stat_lv = int(re.findall(r'-?\d+', fill_stat_lv)[0])  # ensure fill_stat_lv is an integer

            # handle special cases for stat names
            if stat_type == 'dte':
                fill_stat = fill_stat.strip().split(' ')[-1]
            elif stat_type == 'element':
                fill_stat = fill_stat.split(' ')[0]

            fill_stat = format_text(fill_stat)

            filling_stat(click_type, raw_stat, fill_stat, stat_type, 
                         fill_stat_lv, cache=cache)
            sleep(0.5)

        # check if this is the last step
        confirm_stat(is_final=(idx == len(formula) - 1))