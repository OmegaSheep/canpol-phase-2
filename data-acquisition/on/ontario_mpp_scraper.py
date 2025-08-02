from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
from time import sleep
from slugify import slugify
# import pymongo
import sys
sys.stdout.reconfigure(encoding='utf-16')

# Set up the driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
hrefs = []
try:
    # Navigate to the webpage
    url = "https://www.ola.org/en/members/parliament-44"
    driver.get(url)
    sleep(0.4)
    
    # Wait for JavaScript to load (adjust timing as needed)
    driver.implicitly_wait(8)

    links = driver.find_elements(By.TAG_NAME, "a")
    for link in links:
        href = link.get_attribute('href')
        if href and 'en/members/all/' in href:
            hrefs.append(href)

    # Extract and print href attributes
    for href in hrefs:
        if href is None:
            continue
        if ('en/members/all/' in href):
            driver.get(href)
            sleep(0.01)
    
            imgs = driver.find_elements(By.TAG_NAME, 'img')
            base_image = ''
            for i in imgs:
                # Get the image URL
                img_url = i.get_attribute('src')
                
                if 'sites/default/files/member/profile-photo' in img_url:
                    # Download the image
                    base_image = img_url.split('/')[-1].split('.')[0]
                    base_image = slugify(base_image) + '.jpg'
                    # urlretrieve(img_url, f'{base_image}')

            name = driver.find_element(By.CSS_SELECTOR, "h1.field-content").text.rstrip('\n').replace('Hon. ', '')

            riding = driver.find_element(By.CSS_SELECTOR, "p.riding").text.rstrip('\n')

            party_blocks = driver.find_elements(By.CSS_SELECTOR, "div.views-row")
            party = 'Independent'
            for i in party_blocks:
                if 'Party' in i.text:
                    party = i.text.rstrip('\n')
                    break

            mpp_obj = {
                'name': name,
                'constituency': riding.split('\n')[0],
                'party': party,
                'image_name': base_image,
            }
            print(mpp_obj)



except Exception as e:
    print(f"Error: {str(e)}")