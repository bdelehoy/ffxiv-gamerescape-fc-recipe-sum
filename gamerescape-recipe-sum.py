import argparse
from collections import defaultdict
import csv
import urllib.request
from urllib.parse import urlparse

from bs4 import BeautifulSoup

FC_CRAFT_TEXT = "Free Company Craft"    # Text that appears on a Gamer Escape page indicating an FC craft

parser = argparse.ArgumentParser(description="FFXIV Gamer Escape Recipe Summer")
parser.add_argument("-u", "--url", required=True, help="URL of a Gamer Escape wiki page for a craftable item")
parser.add_argument("-q", "--quantity", type=int, help="Quantity multiplier for final ingredients")
parser.add_argument("-o", "--output-file", help="Name of a CSV file to write sums to")

def sanitize_url(s):
    parts = urlparse(s)
    assert parts.netloc.endswith("gamerescape.com")
    return s

def sanitize_csv_file_name(s):
    if (len(s) >= 4 and s[-4:] != ".csv") or len(s) < 4:
        s += ".csv"
    return s

def get_cmd_line_input(inp: argparse.Namespace) -> tuple[str, str]:
    url = sanitize_url(inp.url)

    quantity = 1
    if inp.quantity:
        quantity = int(inp.quantity)

    csv_filename = ""
    if inp.output_file:
        csv_filename = sanitize_csv_file_name(inp.output_file)
    return (url, quantity, csv_filename)

################################

URL,MAIN_QUANTITY,CSV_FILE = get_cmd_line_input(parser.parse_args())

print(f"Finding recipes from:  {URL}")
print(f"With quantity:         {MAIN_QUANTITY}")
if CSV_FILE:
    print(f"Will write to:         {CSV_FILE}")

req = urllib.request.Request(URL)
# workaround for the bot ban - apply to get this script approved!
req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0")
with urllib.request.urlopen(req) as html_content:
    soup = BeautifulSoup(html_content, "html.parser")

final_item = soup.find_all(name="h1")[1].contents[0].strip()
final_item = f"{final_item}{f' (x{MAIN_QUANTITY})' if MAIN_QUANTITY > 1 else ''}"

# If Gamer Escape makes any changes to their page layout, need to update (especially "IDENTIFIER"s)
try:
    recipes_source = soup.find_all(name="div", class_="itembox")   # IDENTIFIER
except Exception as e:
    print("Encountered an error trying to find recipes:", e)
    exit(1)

print()

if len(recipes_source) == 0:
    print("Could not find any recipes.")
    exit(0)

all_recipes: list[tuple[str, defaultdict]] = [] # [(job, recipe), ... ]
for i in recipes_source:
    recipe_soup = BeautifulSoup(str(i), "html.parser")
    first_a = recipe_soup.find(name="a")
    is_free_company_craft = first_a.contents[0] == FC_CRAFT_TEXT
    recipe = []
    recipe_title = ""
    if not is_free_company_craft:
        job = first_a.findNext(name="a").contents[0]
        print("Detected standard recipe for", job)
        ingredients = recipe_soup.find_all(attrs={"align":"center", "width":"10%"})     # IDENTIFIER
        for j in range(0, len(ingredients), 2):
            ingredient_soup = BeautifulSoup(str(ingredients[j+1].contents[0]), "html.parser")
            ingredient = ingredient_soup.find(name="a").attrs['title']
            quantity = ingredients[j].contents[0].strip()
            recipe.append((ingredient, quantity))
        recipe_title = job
    else:
        print("Detected FC recipe")
        ingredients = []
        quantities = []
        ingredients_source = recipe_soup.find_all(attrs={"style":"padding: 0em .5em; width: 20px; box-sizing: content-box;"})   # IDENTIFIER
        for j in ingredients_source:
            ingredient_soup = BeautifulSoup(str(j), "html.parser")
            ingredients.append(ingredient_soup.find(name="a").attrs['title'])
        quantities_source = recipe_soup.find_all(attrs={"style":"width: 1%; text-align: center;"})    # IDENTIFIER
        for k in range(1, len(quantities_source), 2):
            # FC crafts are organized into "batches": 10/30 means 30 total items in batches of 10
            # Iterating here goes through each item: batch size, then total size. We only want the totals, so these numbers:
            #   10, 30, 6, 18, 3, 9
            #       ^^     ^^     ^
            quantities.append(quantities_source[k].contents[0])
        assert len(ingredients) == len(quantities)
        for l,m in zip(ingredients, quantities):
            recipe.append((l,m))
        recipe_title = FC_CRAFT_TEXT
    sums = defaultdict(int)
    for item,quantity in recipe:
        sums[item] += int(quantity)*MAIN_QUANTITY

    all_recipes.append((recipe_title, sums))

print()

if all_recipes:
    print("Final recipe sums:")
    print(final_item)
    for title,recipe in all_recipes:
        print(f"  {title}")
        if title[:len(FC_CRAFT_TEXT)] == FC_CRAFT_TEXT:
            # For FC crafts: print out results sorted by total quantity
            for ing in sorted(recipe.keys(), key=lambda v: recipe[v]):
                print(f"    {recipe[ing]}x {ing}")
        else:
            for ing in recipe:
                print(f"    {recipe[ing]}x {ing}")

    if CSV_FILE:
        with open(CSV_FILE, "w+", newline='') as outfile:
            csv_writer = csv.writer(outfile)
            csv_writer.writerow([final_item])
            for title,recipe in all_recipes:
                csv_writer.writerow([title])
                for ing,qua in recipe.items():
                    csv_writer.writerow(["", ing, qua])
