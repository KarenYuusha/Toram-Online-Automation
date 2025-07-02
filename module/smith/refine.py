import re
from time import sleep

from tqdm import tqdm

from asset.constant.config import EQ_COORDINATE, EQ_POS, LUCK_ID, TEC_ID

from ..core.cursor import click_relative, key_press
from ..core.graphic import click_with_picture, img_is_visible, tesseract_ocr
from ..core.menu_nav import main_to_eq, main_to_ref, switch_char, to_main

GRADE ={
    "e" : 10,
    "d" : 11,
    "c" : 12,
    "b" : 13,
    "a" : 14,
    "s" : 15
}

def get_grade(text) -> int:
    """
    converting alphabet grade to number grade
    Args:
        text (str): alphabet grade
    Returns:
        int: number grade
    """
    if type(text) == int:
        return text

    if not text:
        return 0
    
    if '+' not in text:
        return 0

    grade = text.split()[-1][-1]

    # grade is higher than 9
    if grade in GRADE:
        return GRADE[grade]

    # grade lower than 10
    return int(grade)

def wait_for_refine() -> int:
    """
    waiting for the refine process to finish and return the current grade
    """
    max_attempts = 10
    attempts = 0
    
    # waiting for the refine process to finish
    sleep(5)
    
    # checking for the equipment current grade
    while attempts < max_attempts:
        
        text = tesseract_ocr(35, 31, 70, 40).lower()
        if get_grade(text) > 0:
            current_grade = get_grade(text)
            break
        
        attempts += 1
        sleep(0.5)
    
    # cannot get the grade
    else:
        return 1
    
    return current_grade

def init_refine() -> None:
    """
    from main screen to refine screen and start refining
    cannot click complete button because the system needs to read the grade first
    """
    main_to_ref()
    
    click_relative(75, 25) # choose ore
    click_relative(75, 25) # choose item
    click_relative(75, 25) # choose insurance
    click_relative(25, 90) # start refinement

def smart_refine(show_result=True) -> None:
    """
    refining from 0 to C using TEC character, 
    from C to S using LUCK character
    """
    # from main screen to the first refine
    init_refine()
    
    current_grade = wait_for_refine()
    current_role = "TEC"
    
    click_relative(50, 77) # complete
    count = 1 # count total amount of ore has been used
    
    while not current_grade == 15:
        click_relative(25, 90) # start refinement!
        
        current_grade = wait_for_refine()
        
        click_relative(50, 77) # complete
        count += 1
        
        if current_grade >= 12 and current_role != "LUCK":
            switch_char(LUCK_ID, fast_mode=True)
            current_role = "LUCK"

            init_refine()
            sleep(5)

        elif current_grade < 12 and current_role != "TEC":
            switch_char(TEC_ID, fast_mode=True)
            current_role = "TEC"
            
            init_refine()
            sleep(5)
    
    if show_result:        
        print(f"Used {count} ores")

def luck_refine(show_result=True) -> None:
    """
    refine from 0 to S using LUCK character
    """
    init_refine()
    
    current_grade = wait_for_refine()
    click_relative(50, 77) # complete
    
    count = 1 # count total amount of ore has been used
    
    while not current_grade == 15:
        click_relative(25, 90)
        current_grade = wait_for_refine()
        click_relative(50, 77)
        count += 1
    
    if show_result:
        print(f"Used {count} ores")

def select_eq(type='weapon', max_pos=12) -> bool:
    """
    select weapon to refine
    
    Args:
        type (str): type of equipment to refine. Example: weapon, sub, armor, add
        max_pos (int): total number of eq slot to check
    """
    main_to_eq()
    pos = EQ_POS[type]
    click_pos = ()
    
    # making sure the equipment tab is done loading
    while not img_is_visible('asset\images\smith\equipment.png', 81, 90, 89, 95):
        click_relative(*pos)
    
    # position start from 1 when you already equiped the item
    for index in range(1, max_pos):
        row = index // 4
        col = index % 4
        
        coordinate = EQ_COORDINATE[col]
        coordinate = (coordinate[0], coordinate[1] + row * 15, 
                      coordinate[2], coordinate[3] + row * 15)
        
        res = tesseract_ocr(*coordinate).strip('\n')
        
        try:
            ref_grade = re.search(r'\+(\w)', res).group(1)
            if ref_grade.lower() != 's':
                click_pos = (coordinate[0] + coordinate[2]) // 2, (coordinate[1] + coordinate[3]) // 2
        
        # if background and font has similar color, ocr will return empty string
        # this occurs when the item is crafted by player
        except AttributeError:
            click_pos = (coordinate[0] + coordinate[2]) // 2, (coordinate[1] + coordinate[3]) // 2
        
        finally:
            if click_pos:
                click_relative(click_pos[0], click_pos[1])
                click_with_picture('asset\images\smith\equipment.png', 81, 90, 89, 95)
                break
            if index == max_pos - 1:
                print("No item to refine")
                return False
            else:
                continue
    return True

def consecutive_ref(amount=2, type='weapon', strat='luck') -> None:
    """
    refine multiple equipment in a row
    this function does not take account the amount of ore used
    Args:
        amount (int): number of equipment to refine
        type (str): type of equipment to refine. Example: weapon, sub, armor, add
        strat (str): refining strategy. Example: luck, smart
    """
    if amount < 2:
        print("Amount must be greater than 1")
        return
    
    if type not in EQ_POS.keys():
        print("Invalid equipment type")
        return
    
    if strat not in ['luck', 'smart']:
        print("Invalid refining strategy")
        return
    
    for iter in tqdm(range(amount), desc="Refining", unit="item"):
        if strat == 'luck':
            luck_refine()
            if iter < amount - 1:
                # switch to the next equipment
                select_eq(type)
        
        # we need to switch weapon for both LUCK and TEC character        
        elif strat == 'smart':
            smart_refine()
            if iter < amount - 1:
                # switch eq for LUCK character
                select_eq(type)
                switch_char(TEC_ID)
                # switch eq for TEC character
                select_eq(type)