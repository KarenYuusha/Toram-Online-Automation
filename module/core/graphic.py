import os
import random
from time import sleep
from typing import Optional, Tuple

import cv2
import easyocr
import numpy as np
import pyautogui as gui
import pytesseract
from dotenv import load_dotenv
from matplotlib import pyplot as plt
from PIL import Image
from PIL import ImageGrab as IG

from .cursor import click_relative, convert_to_absolute

dir = os.path.dirname(__file__)
dotenv_path = os.path.join(dir, '..', 'asset', 'path', '.env')
load_dotenv(dotenv_path)
    
tesseract_path = os.getenv('TESSERACT_PATH')
pytesseract.pytesseract.tesseract_cmd = tesseract_path

def grab_image_in(left=0, top=0, right=100, bottom=100, dev= False, 
                  save_path=None, converted=True) -> Image:
    """
    Grabs an image from the window using relative position.
    
    Args:
        left (float): Left coordinate.
        top (float): Top coordinate.
        right (float): Right coordinate.
        bottom (float): Bottom coordinate.
        dev (bool): If True, display the image for debugging purposes. Default is False.
        save_path (str): Path to save the image (optional).
        converted (bool): If True, return the image as a NumPy array else Image object. Default is False.
    Returns:
        Image: The captured image as a PIL Image object or NumPy array.
    """
    try:
        abs_left, abs_top = convert_to_absolute(left, top)
        abs_right, abs_bottom = convert_to_absolute(right, bottom)

        width, height = abs_right - abs_left, abs_bottom - abs_top
        if width <= 0 or height <= 0:
            raise ValueError("Invalid region dimensions. Width and height must be positive.")
        
        image = gui.screenshot(region=(abs_left, abs_top, width, height))
        
        if converted:
            image_np = np.array(image)

        if dev:
            image.show(title="Captured Image")
        
        if save_path:
            image.save(save_path)

        return np.array(image) if converted else image

    except Exception as e:
        print(f"Error in grab_image_in: {e}")
        return None

def detect_blue(image, dev=False) -> bool:
    """
    Detects blue areas in the given image.
    
    Args:
        image (Image): The input image.
        dev (bool): If True, display the detected blue areas for debugging purposes. Default is False.
    
    Returns:
        bool: True if blue areas are detected, otherwise False.
    """
    hsv_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

    lower_blue = np.array([100, 150, 0])   
    upper_blue = np.array([140, 255, 255]) 
    
    blue_mask = cv2.inRange(hsv_image, lower_blue, upper_blue)
    
    if dev:
        blue_detected = cv2.bitwise_and(image, image, mask=blue_mask)

        cv2.imshow('Blue Areas Detected', blue_detected)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    return np.any(blue_mask > 0)

def detect_red(image, dev=False) -> bool:
    """
    Detects red areas in the given image.
    
    Args:
        image (Image): The input image.
        dev (bool): If True, display the detected red areas for debugging purposes. Default is False.
    
    Returns:
        bool: True if red areas are detected, otherwise False.
    """
    
    hsv_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

    # Define the range for red color in HSV (two ranges are needed for red)
    lower_red1 = np.array([0, 120, 70])     # Lower bound for red (first range)
    upper_red1 = np.array([10, 255, 255])   # Upper bound for red (first range)

    lower_red2 = np.array([170, 120, 70])   # Lower bound for red (second range)
    upper_red2 = np.array([180, 255, 255])  # Upper bound for red (second range)

    # Create masks for both red ranges
    red_mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)

    # Combine both red masks
    red_mask = red_mask1 | red_mask2

    if dev:
        red_detected = cv2.bitwise_and(image, image, mask=red_mask)

        cv2.imshow('Red Areas Detected', red_detected)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return np.any(red_mask > 0)

def tesseract_ocr(left, top, right, bottom, dev=False, 
                  number_only=False) -> str:
    """
    find text in the image using OCR with absolute position.
    Args:
        left (float): Left coordinate.
        top (float): Top coordinate.
        right (float): Right coordinate.
        bottom (float): Bottom coordinate.
        development (bool): Show the image in a window.
        detect_number_only (bool): Detect only numbers.
    Requires:
        tesseract path in asset/path/.env file.
    Returns:
        str: The text found within the bounding.
    """
    image_data = grab_image_in(left, top, right, bottom, dev)
    options = ""

    if number_only:
        options = r'--oem 3 --psm 6 outputbase digits'

    text = pytesseract.image_to_string(image_data, config=options)
    return text

def easy_ocr(left, top, right, bottom, n=1, dev=False, auto_correct=False) -> str:
    img = grab_image_in(left, top, right, bottom, dev)
    
    reader = easyocr.Reader(['en'], verbose=False, gpu=False)
    res = reader.readtext(img, detail=0)
        
    return res[:n]   

def image_matching(image1, image2, hash_size=8, tolerance=10, remove_bg=False) -> bool:
    """
    Check if two images are similar using average hash.
    
    Args:
        image can be numpy array or PIL Image.
        hash_size (int): Hash size. Default is 8.
        tolerance (int): Tolerance level. Default is 10, the lower the more strict.
        remove_bg (bool): Whether to remove the background from images before matching. Default is False.
        
    Returns:
        bool: True if the images are similar, False otherwise.
    """
    # Function to remove background if specified
    def remove_background(image):
        if isinstance(image, Image.Image):
            # Convert the image to bytes for rembg
            image_bytes = io.BytesIO()
            image.save(image_bytes, format='PNG')
            image_bytes.seek(0)  # Rewind the BytesIO object
            output_image = remove(image_bytes.read())
            return Image.open(io.BytesIO(output_image))
        return image

    # Convert to PIL Image if not already
    if not isinstance(image1, Image.Image):
        image1 = Image.fromarray(image1)
    if not isinstance(image2, Image.Image):
        image2 = Image.fromarray(image2)

    # Remove backgrounds if requested
    if remove_bg:
        import io

        import imagehash
        from rembg import remove
        image1 = remove_background(image1)
        image2 = remove_background(image2)
    
    # Compute the hashes
    hash1 = imagehash.average_hash(image1, hash_size)
    hash2 = imagehash.average_hash(image2, hash_size)
    
    # Return whether the images are similar
    return hash1 - hash2 <= tolerance

def img_is_visible(image_path, left=0, top=0, right=100, 
                   bottom=100,verbose=False, confidence=0.7) -> bool:
    """
    Check if the image is visible on the screen
    Args:
        image_path (str): path to the image
        left (float): left relative coordinate. Default is 0
        top (float): top relative coordinate. Default is 0
        right (float): right relative coordinate. Default is 100
        bottom (float): bottom relative coordinate. Default is 100
        confidence (float): confidence level. Default is 0.7
    """
    left, top = convert_to_absolute(left, top)
    right, bottom = convert_to_absolute(right, bottom)
    width = right - left
    height = bottom - top
    
    try :
        gui.locateOnScreen(image_path, confidence=confidence, region=(left, top, width, height))
        return True
    except:
        if verbose:
            print(f"Cannot find {image_path} on screen in region ({left}, {top}, {right}, {bottom}) with confidence {confidence}.")
        return False

def img_is_visible_grayscale(image_path, left=0, top=0, right=100, bottom=100,
                   verbose=False, confidence=0.7) -> bool:
    """
    The function is similar to the function above, but code manually
    and uses preprocessing 
    """
    left, top = convert_to_absolute(left, top)
    right, bottom = convert_to_absolute(right, bottom)
    width = right - left
    height = bottom - top
    
    screen = gui.screenshot(region=(left, top, width, height))
    screen_np = np.array(screen.convert('RGB'))
    screen_gray = cv2.cvtColor(screen_np, cv2.COLOR_RGB2GRAY)
    
    template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= confidence)

    if len(loc[0]) > 0:
        return True
    else:
        if verbose:
            print(f"Cannot find {image_path} in region ({left},{top},{right},{bottom}) with confidence {confidence}")
        return False

def get_img_coordinate(image_path, left=0, top=0, right=100, 
                       bottom=100, confidence=0.7, 
                       silence=False) -> Optional[Tuple[int, int]]:
    """
    Get the coordinate of the image
    Args:
        image_path (str): path to the image
        left (float): left relative coordinate. Default is 0
        top (float): top relative coordinate. Default is 0
        right (float): right relative coordinate. Default is 100
        bottom (float): bottom relative coordinate. Default is 100
        confidence (float): confidence level. Default is 0.7
        silence (bool): if True, do not print the error message. Default is False
    Returns:
        tuple: x, y coordinate of the image or False if not found
    """
    left, top = convert_to_absolute(left, top)
    right, bottom = convert_to_absolute(right, bottom)
    width = right - left
    height = bottom - top
    
    try:
        img_location = gui.locateOnScreen(image_path, confidence=confidence, region=(left, top, width, height))
        center_x, center_y = gui.center(img_location)
        return center_x, center_y
    
    except:
        if not silence:
            print(f"Cannot find {image_path} on screen in region ({left}, {top}, {right}, {bottom}) with confidence {confidence}.")
        
        return False

def find_all_image(match_image, left=0, top=0, right=100, 
                   bottom=100, threshold=0.9, dev=False):
    """
    finding all template image in the given region
    
    Args:
        match_image (str): path to the image
        left (float): left relative coordinate. Default is 0
        top (float): top relative coordinate. Default is 0
        right (float): right relative coordinate. Default is 100
        bottom (float): bottom relative coordinate. Default is 100
        threshold (float): confidence level. Default is 0.9
        dev (bool): if True, show the image with rectangles around the found images.
    Returns:
        list: list of coordinates of the found images
    """
    centers = []
    
    image = grab_image_in(left, top, right, bottom)
    template = cv2.imread(match_image)
    
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    res = cv2.matchTemplate(gray_image, gray_template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    
    if dev:
        for pt in zip(*loc[::-1]):
            cv2.rectangle(image, pt, (pt[0] + template.shape[1], pt[1] + template.shape[0]), (0, 255, 0), 2)
        plt.imshow(image)
        plt.show()
    
    # Non-maximum suppression
    rectangles = []
    for pt in zip(*loc[::-1]):
        # left, top, right, bottom
        rectangles.append([pt[0], pt[1], pt[0] + template.shape[1], pt[1] + template.shape[0]])
    
    # Recommend eps=0.2
    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    
    offset_x, offset_y = convert_to_absolute(left, top)
    for (l, t, r, b) in rectangles:
        center_x = l + (r - l) // 2 + offset_x # middle_x + the original abosulte x
        center_y = t + (b - t) // 2 + offset_y # middle_y + the original abosulte y
        centers.append((center_x, center_y))
    
    return centers

def click_with_picture(image_path, left=0, top=0, right=100, bottom=100, 
                       confidence=0.7, duration=0.4, silence=False) -> bool:
    """
    Click on the image
    Args:
        image_path (str): path to the image
        left (float): left relative coordinate. Default is 0
        top (float): top relative coordinate. Default is 0
        right (float): right relative coordinate. Default is 100
        bottom (float): bottom relative coordinate. Default is 100
        confidence (float): confidence level. Default is 0.7
        duration (float): duration of the click. Default is 0
    """
    coordinates = get_img_coordinate(image_path, left, top, right, bottom, confidence, silence)
    
    if coordinates:
        x, y = coordinates
        click_relative(x, y, duration=duration, converted=True)
        return True

    return False
