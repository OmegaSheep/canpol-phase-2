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

env = open('../../.env')
mongo_uri=''
for line in env:
    if line.startswith('MONGO_URI'):
        mongo_uri = line.split('MONGO_URI=')[1].replace("'", "")

myclient = pymongo.MongoClient(mongo_uri)
mydb = myclient["public_gov"]

mlas = mydb["saskatchewan_mlas"]
disclosures = mydb["saskatchewan_disclosures"]


# Get all MLA names into a set for fast lookup
allMlaNames = set(mla['name'] for mla in mlas.find({}))


f = open('sask_disclosures.txt', 'r', encoding='utf-8')

for line in f.readlines():
    line = line.strip()

    if not line:
        continue 

    if line.startswith('--'):
        name = line[2:].strip()
        continue

    if line.startswith('$$'):
        category = line[2:].strip()
        continue

    if name not in allMlaNames:
        print(f"MLA {name} not found in database.")
        continue

    if name == "Matt Love":
        disclosure_item = {
            'name': name,
            'category': category,
            'content': line
        }
        disclosures.insert_one(disclosure_item)

f.close()

