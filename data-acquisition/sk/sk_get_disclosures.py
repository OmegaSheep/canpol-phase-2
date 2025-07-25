from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from urllib.request import urlretrieve
# from PyPDF2 import PdfReader
from pypdf import PdfReader
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

ab_disclosures = mydb["alberta_disclosures"]
ab_mlas = mydb["alberta_mlas"]

# Set up the driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            
# Navigate to the webpage
url = "https://www.legassembly.sk.ca/mlas/mla-disclosure-statements/"
driver.get(url)

# Wait for JavaScript to load (adjust timing as needed)
driver.implicitly_wait(8)
sleep(1)

row_tags = driver.find_elements(By.TAG_NAME, 'tr')
sleep(1)

name_to_pdf_dict = dict()
name_list = []

for tag in row_tags:

    tds = tag.find_elements(By.TAG_NAME, 'td')
    if len(tds) != 5:
        continue

    if "Former" in tds[2].text:
        continue

    name = tds[0].text
    
    a_tags = tds[4].find_elements(By.TAG_NAME, 'a')

    the_pdf_tag = a_tags[0]
    pdf_url = the_pdf_tag.get_attribute('href')
    pdf_name = pdf_url.split('/')[-1].split('"')[0]
    name_to_pdf_dict[name] = pdf_name
    name_list.append(name)


    # urlretrieve(pdf_url, pdf_name)


def print_pdf(name, pdf_path):
    # Create a reader object
    reader = PdfReader(pdf_path)
    
    # Extract text from second page
    for i in reader.pages:
        print(i.extract_text())

    # literally does not matter because they are not machine readable, thanks Scott Moe 
    
for name in name_list:
    print_pdf(name, name_to_pdf_dict[name])