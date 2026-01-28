from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from urllib.request import urlretrieve
from time import sleep
import sys
import requests
import pymongo
sys.stdout.reconfigure(encoding='utf-8')

env = open('.env')
mongo_uri=''
for line in env:
    if line.startswith('MONGO_URI'):
        mongo_uri = line.split('MONGO_URI=')[1].replace("'", "")

myclient = pymongo.MongoClient(mongo_uri)
mydb = myclient["public_gov"]
mlas = mydb["new_brunswick_mlas"]


def download_with_headers(url, out_name, driver=None):
    session = requests.Session()
    headers = {}
    try:
        if driver:
            ua = driver.execute_script("return navigator.userAgent;")
            headers['User-Agent'] = ua
            headers['Referer'] = driver.current_url
        else:
            headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
            headers['Referer'] = 'https://www.legnb.ca/'
    except Exception:
        headers['User-Agent'] = 'Mozilla/5.0'
        headers['Referer'] = 'https://www.legnb.ca/'

    resp = session.get(url, headers=headers, stream=True, timeout=15)
    print(f"GET {url} -> {resp.status_code}")
    if resp.status_code == 200:
        with open(out_name, 'wb') as f:
            for chunk in resp.iter_content(8192):
                if chunk:
                    f.write(chunk)
        print(f"Saved {out_name}")
    else:
        print(f"Download failed: {resp.status_code}")

# Set up the driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            
# Navigate to the webpage
url = "https://www.legnb.ca/en/members/current"
driver.get(url)

# Wait for JavaScript to load (adjust timing as needed)
driver.implicitly_wait(4)
sleep(1)

mla_blocks = driver.find_elements(By.CLASS_NAME, "member-card")

for block in mla_blocks:
    image_block = block.find_element(By.CLASS_NAME, "member-card-avatar-image")
    name_block = block.find_element(By.CLASS_NAME, "member-card-description-name")
    party_block = block.find_element(By.CLASS_NAME, "member-card-description-party")
    constituency_block = block.find_element(By.CLASS_NAME, "member-card-description-riding")

    name = name_block.text.replace("Hon. ", "")
    name = name.split(", ")[1] + " " + name.split(", ")[0]
    name = name.rstrip(" ")
    name = name.rstrip("\n")

    party = party_block.text

    constituency = constituency_block.text

    img = image_block.find_element(By.TAG_NAME, "img")
    img_url = img.get_attribute('src')
    img_name = img_url.split('/')[-1].split('"')[0].split("?")[0]
    
    # urlretrieve(img_url, img_name) # Fails
    # download_with_headers(img_url, img_name) # Site gets mad if you don't have headers

    doc = {
        'name': name,
        'party': party,
        'constituency': constituency,
        'image_name': img_name,
    }
    print(doc)