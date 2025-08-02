from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from time import sleep
import pymongo
import sys
sys.stdout.reconfigure(encoding='utf-16')

env = open('../../.env')
mongo_uri=''
for line in env:
    if line.startswith('MONGO_URI'):
        mongo_uri = line.split('MONGO_URI=')[1].replace("'", "")

myclient = pymongo.MongoClient(mongo_uri)
mydb = myclient["public_gov"]

mpps = mydb["ontario_mpps"]

allMpps = mpps.find({}).sort({ 'name': 1 })


# Set up the driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# f = open('ontario_proper_names.txt', 'r') # We can use the data from ontario_mpp_scraper.py for this
# lines = f.readlines()

for mpp in allMpps:
    # mpp = {
    #     'name': mpp.rstrip('\n')
    # }
    try:
        true_name = mpp['name']
        name = true_name

        if len(name.split(' ')) == 3 and '.' in name.split(' ')[1]:
            name = name.split(' ')[0] + ' ' + name.split(' ')[2]
        
        # Navigate to the webpage
        url = "https://pds.oico.on.ca/Pages/Public/PublicDisclosures.aspx"
        driver.get(url)
        
        # Wait for JavaScript to load (adjust timing as needed)
        driver.implicitly_wait(8)

        search_box = driver.find_element(By.ID, 'BodyContent_ddlYear')
        select_dropdown = Select(search_box)
        select_dropdown.select_by_value("2025")

        name_box = driver.find_element(By.ID, 'BodyContent_ddlMemberName')
        select_dropdown = Select(name_box)
        
        # Lots of name mismatches relative to the official ON MPP Portal. . . 
        if ('Sarrazin' in name):
            select_dropdown.select_by_value('c8ceff97-3d03-f011-bae3-002248b154b5')
        elif ('France G' in name):
            select_dropdown.select_by_value('6c80018e-3e04-f011-bae3-002248b154b5')
        elif ('Steve Pinsonneault' in name):
            select_dropdown.select_by_value('6932cb57-6b36-f011-8c4e-002248b154b5')
        elif ('Victor Fedeli' in name):
            select_dropdown.select_by_value('1f8b7671-953d-f011-b4cc-002248b154b5')
        elif ('Hardeep Singh Grewal' in name):
            select_dropdown.select_by_value('5200ca0f-703a-f011-b4cc-002248b154b5')
        elif ('Raymond Sung Joon Cho' in name):
            select_dropdown.select_by_value('6292128c-1725-f011-8c4d-002248b154b5')
        elif ('Cerjanec' in name):
            select_dropdown.select_by_value('8911415e-b73c-f011-b4cc-002248b154b5')
        elif ('Robert Bailey' in name):
            select_dropdown.select_by_value('239499bc-7c27-f011-8c4d-002248b154b5')
        else:
            select_dropdown.select_by_visible_text(name)

        income = driver.find_element(By.ID, "BodyContent_fldMppIncome").text
        assets = driver.find_element(By.ID, "BodyContent_fldMppAssets").text
        liabilities = driver.find_element(By.ID, "BodyContent_fldMppLiabilities").text
        gifts = driver.find_element(By.ID, "BodyContent_fldGiftsAndBenefits").text
        offices = driver.find_element(By.ID, "BodyContent_fldOffices").text

        # # Find and click the search button
        # search_button = driver.find_element(By.ID, 'ctl00_ctl42_g_17022c15_88ec_424e_bf2f_b9bdf7bf3836_csr_SearchLink')
        # search_button.click()

        incomeObj = {
            'name': true_name,
            'category': 'Income',
            'content': income,
        }
        assetsObj = {
            'name': true_name,
            'category': 'Assets',
            'content': assets,
        }
        liabilityObj = {
            'name': true_name,
            'category': 'Liabilities',
            'content': liabilities,
        }
        giftsAndBenefitsObj = {
            'name': true_name,
            'category': 'Gifts and Benefits',
            'content': gifts,
        }
        officesObj = {
            'name': true_name,
            'category': 'Offices',
            'content': offices,
        }

        print(incomeObj)
        print(assetsObj)
        print(liabilityObj)
        print(giftsAndBenefitsObj)
        print(officesObj)

    except Exception as e:
        print(f"Error ${mpp['name']}: {str(e)}")
