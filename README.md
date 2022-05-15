# ffxiv-gamerescape-fc-recipe-sum
Parses a Gamer Escape wiki page for a craftable item in Final Fantasy XIV to generate a summary of all the ingredients needed for crafting that item. Intended for use with Free Company crafts, where recipes may have redundant ingredients spread across multiple phases (although this works with regular craftable items, too).

# Requirements
Any Python version that supports BeautifulSoup 4.10.0 (developed and working with Python 3.10.4)

# Usage
Run in a command-line environment. Brackets indicate optional arguments.

```
gamerescape-recipe-sum.py [-h] -u URL [-o OUTPUT_FILE]
```

Examples:
```
python gamerescape-recipe-sum.py -u https://ffxiv.gamerescape.com/wiki/Coelacanth-class_Pressure_Hull
python gamerescape-recipe-sum.py -u https://ffxiv.gamerescape.com/wiki/Mythrite_Ingot -o output.csv
python gamerescape-recipe-sum.py -u https://ffxiv.gamerescape.com/wiki/Medium_Cafe_Walls/Recipe
```

Use of a virtual environment is highly recommended:

```
cd ffxiv-gamerescape-fc-recipe-sum

python -m venv .venv

./.venv/Scripts/activate.ps1    # Will be different depending on your dev platform; this is Powershell on Windows

pip install -r requirements.txt

# (you are now free to run/develop/debug/etc.... see the examples above)

deactivate
```
