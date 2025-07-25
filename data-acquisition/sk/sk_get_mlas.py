from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from slugify import slugify
from urllib.request import urlretrieve
from time import sleep
import sys
import pymongo
sys.stdout.reconfigure(encoding='utf-8')

env = open('.env')
mongo_uri=''
for line in env:
    if line.startswith('MONGO_URI'):
        mongo_uri = line.split('MONGO_URI=')[1].replace("'", "")

myclient = pymongo.MongoClient(mongo_uri)
mydb = myclient["public_gov"]

mnas = mydb["sk_mlas"]

# Set up the driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            
# Navigate to the webpage
url = "https://www.legassembly.sk.ca/mlas/"
driver.get(url)
driver.fullscreen_window()

# Wait for JavaScript to load (adjust timing as needed)
driver.implicitly_wait(8)
sleep(1)

links = driver.find_elements(By.TAG_NAME, "a")
link_array = []

for link in links:
    href = link.get_attribute('href')
    name = link.text
    name = name.replace("Hon. ", "")
    if href and "/mlas/member-details" in href:

        # SK site arbitrarily adds %20 to some names, so we remove it in some cases. Wild.
        if "Nathaniel"  not in name:
            href = href.replace('%20', '')
        link_array.append({
            'href': href,
            'name': name
        })

visited = []
for link in link_array:
    # Catches some duplicate links. . .
    if link['name'] in visited:
        continue
    
    driver.get(link['href'])

    sleep(0.1)

    # Party
    mla_header = driver.find_element(By.CLASS_NAME, "mla-header").text
    if ("OPPOSITION" in mla_header):
        party = "NDP"
    else:
        party = "Saskatchewan Party"

    # Constituency
    constituency = driver.find_element(By.CLASS_NAME, "mla-constituency-cell").text

    img = driver.find_element(By.CSS_SELECTOR, "img.img-fluid")
    img_url = img.get_attribute('src')
    img_name = slugify(link['name']+'-'+constituency)+".jpg"
    # urlretrieve(img_url, img_name)

    doc = {
        'name': link['name'],
        'party': party,
        'constituency': constituency,
        'image_name': img_name,
    }
    print(doc)
    sleep(0.1)
    visited += [link['name']]