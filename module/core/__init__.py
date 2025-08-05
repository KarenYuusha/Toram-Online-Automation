import os
import subprocess
from time import sleep

from dotenv import load_dotenv
from win32gui import FindWindowEx


def start_toram() -> None:
    """
    Open the Toram Online game.
    """
    load_dotenv(dotenv_path)

    toram_path = os.getenv('TORAM_PATH')
    try:
        subprocess.Popen(toram_path, shell=True)
    except FileNotFoundError:
        print(f"Error: {toram_path} not found")
    except Exception as e:
        print(f"An error occurred: {e}")
    sleep(30)


version = '0.1.0'

# getting toram path in .env file
dir = os.path.dirname(__file__)
dotenv_path = os.path.join(dir, '..', '..', 'asset', 'path', '.env')
load_dotenv(dotenv_path)

TORAM_PATH = os.getenv('TORAM_PATH')

if not FindWindowEx(None, None, None, "ToramOnline"):
    start_toram()
