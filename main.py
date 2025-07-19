from module.core.cursor import switch_to_toram
from module.event.anniv import battle, to_battle
from time import sleep
from tqdm import trange

switch_to_toram('normal')
for _ in trange(100):
    to_battle()
    battle()
    sleep(1)