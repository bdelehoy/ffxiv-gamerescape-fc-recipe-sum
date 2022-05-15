from collections import defaultdict
import csv
from sys import argv
import urllib.request
from urllib.parse import urlparse

from bs4 import BeautifulSoup

def sanitize_url(s):
    parts = urlparse(s)
    assert parts.netloc.endswith("gamerescape.com")
    return s

def sanitize_csv_file_name(s):
    assert len(s) > 4
    if s[-4:] != ".csv":
        raise Exception("Filename must end in '.csv'")
    return s

################################

url = sanitize_url(argv[1])

print(f"Finding recipes from: {url}")

req = urllib.request.Request(url)
# workaround for the bot ban - apply to get this script approved!
req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0")
with urllib.request.urlopen(req) as html_content:
    soup = BeautifulSoup(html_content, "html.parser")

try:
    recipes = soup.find_all(name="div", class_="itembox")
except:
    print("Could not find any recipes.")
    exit(1)

# If Gamer Escape makes any changes to their page layout, "IDENTIFIER" lines must be changed!
for i in recipes:
    recipe_soup = BeautifulSoup(str(i), "html.parser")
    first_a = recipe_soup.find(name="a")
    is_free_company_craft = first_a.contents[0] == "Free Company Craft"
    recipe = []
    recipe_title = ""
    if not is_free_company_craft:
        job = first_a.findNext(name="a").contents[0]
        print()
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
            quantities.append(quantities_source[k].contents[0])
        assert len(ingredients) == len(quantities)
        for l,m in zip(ingredients, quantities):
            recipe.append((l,m))
        recipe_title = "Free Company Craft"
    #print(f"    {recipe}")
    sums = defaultdict(int)
    for item,quantity in recipe:
        sums[item] += int(quantity)

    print("Final recipe sums:")
    print(f"  {recipe_title}")
    if is_free_company_craft:
        # For FC crafts: display results sorted by total quantity
        for ing in sorted(sums.keys(), key=lambda v: int(sums[v])):
            print(f"    {sums[ing]}x {ing}")
    else:
        for ing in sums:
            print(f"    {sums[ing]}x {ing}")
