## 🕹️ Toram Online Automation
A python-based automation tool for MMORPG Toram Online. This project aim to automate certain tasks to improve **quality of life (QoL)** for players.
<p align="center"><strong>⚠️ WARNING: USE IT AT YOUR OWN RISK ⚠️</strong></p>

## 🔍 Features
**Refining** - Work for both luck and tec character, support refining multiple equipments of the same category

**Auto craft adventurer's garb** - Crafting, restocking from gifts, auto process armor, store and send notification when 2 slot equipment is detected

**Auto fill** - Auto customize the equipment base on the formula from [tanaka0](https://tanaka0.work/en/BouguProper#output)

**Other miscellaneous function**

## 📌 TODO
- [ ] Auto send gifts
- [ ] Using object detection module
- [ ] Auto fishing
- [ ] Auto guild quest
- [ ] Applying reinforcement learning

## 🚀 Quick Start

### 🛠️ Environment Setup

#### ✅ Recommended Setup

```bash
#1. Clone the repo
git clone https://github.com/KarenYuusha/Toram-Online-Automation.git

#2. (Optional) Create a clean Python environment
conda create -n toa python=3.10
conda activate toa

#3. Install dependencies
#3.1 Install required packages
pip install -r requirements.txt

# If you get OSError run this command instead:
pip install --user -r requirements.txt

#3.2 Install tesseract
# Install tesseract installer from here
https://github.com/UB-Mannheim/tesseract/wiki
```

### 📁 File Path Setup
```bash
# Change toram online in steam path
# The path is located in asset/path/.env
# For example: 
TORAM_PATH = 'C:\\Users\\user-name\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Steam\\Toram Online.url'

# Change tesseract path
# Located at asset/path/.env
# For example: 
TESSERACT_PATH = 'T:\\tesseract\\tesseract.exe'

# (Optional) provide pushbullet API key
# Create your API key here:
# https://www.pushbullet.com/
# Change your API key in asset/API/.env
# For example: 
PUSHBULLET_API_KEY = 'oxitia1rcn2cvecanoha'
```

### 🧪 Run Examples
```bash
# auto craft adventurer garb
from module.core.cursor import switch_to_toram
from module.smith.craft import auto_craft_and_proc_adv

switch_to_toram()
auto_craft_and_proc_adv()

# auto fill
from module.smith.fill import auto_fill

switch_to_toram()
auto_fill('./fill_order.txt')

# refining
# remember to manually equip the gear before running this code
from module.smith.refine import luck_refine, smart_refine

switch_to_toram()
luck_refine() # only using LUK char

# by default you should put TEC char in the first position and LUK in the second position of your character list
smart_refine() # using both LUK and TEC char
```
 
## 💡 Usage Tips
- To achieve optimal results, you must run the game in **1600x900** resolution
- Remember to run the function switch_to_toram()
- You can accelerate the process by modifying the argument duration in module/core/cursor.py
- When import anything from module/core if Toram Online is not open then it will automically open Toram Online from Steam

## ❌ Limitations and Suggestions
⚠️ Note: The project currently uses template matching, which is scale-variant. Therefore, it is recommended to run the game at 1600x900 resolution for best results.

🎮 Compatibility: The current implementation only supports launching Toram Online via Steam. Asobimo launcher is not supported at this time.

🖼️ Troubleshooting: If the graphic module fails to recognize images correctly, you can retake all images in the asset/images/ folder. This usually resolves matching issues.
