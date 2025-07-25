import os
from time import sleep

import pyautogui as gui
from dotenv import load_dotenv
from pushbullet import Pushbullet
import keyboard

dir = os.path.dirname(__file__)
dotenv_path = os.path.join(dir, '..', '..', 'asset', 'API', '.env')
load_dotenv(dotenv_path)


def send_sms_message(title, text) -> None:
    """
    Send a notification message using Pushbullet.

    Parameters:
        title (str): The title of the notification.
        text (str): The content of the notification.

    Requires the Pushbullet API key (`PUSHBULLET_API_KEY`) in asset/API/.env file.
    """

    # If KEY is none then print out on terminal
    KEY = os.getenv('PUSHBULLET_API_KEY')
    if KEY is None:
        print(f'{title}: {text}')
        return

    pb = Pushbullet(KEY)
    pb.push_note(title, text)


def type_text(text, delay=0.1):
    for char in text:
        keyboard.write(char)
        sleep(delay)
