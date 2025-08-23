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
from slugify import slugify
sys.stdout.reconfigure(encoding='utf-8')

env = open('.env')
mongo_uri=''
for line in env:
    if line.startswith('MONGO_URI'):
        mongo_uri = line.split('MONGO_URI=')[1].replace("'", "")

myclient = pymongo.MongoClient(mongo_uri)
mydb = myclient["public_gov"]

bc_disclosures = mydb["british_columbia_disclosures"]
bc_mlas = mydb["british_columbia_mlas"]

# Set up the driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            
# Navigate to the webpage
url = "https://www.leg.bc.ca/about/accountability/members-disclosures/public-disclosure-statements"
driver.get(url)

# Wait for JavaScript to load (adjust timing as needed)
driver.implicitly_wait(8)
sleep(1)

button = driver.find_element(By.CSS_SELECTOR, "a[role='button']")
button.click()

main_div = driver.find_element(By.CLASS_NAME, 'panel-body')
sleep(1)
p_tags = main_div.find_elements(By.TAG_NAME, 'p')

name_to_pdf_dict = dict()
name_list = []

for p in p_tags:

    full_text = p.text

    name_backwards = full_text.split(" - ")[0]
    name_backwards = name_backwards.replace("K.C., ", "")
    name = name_backwards.split(", ")[1] + " " + name_backwards.split(", ")[0]

    # Two Manual Corrections
    if name == "Qwulti'stunaat Toporowski":
        name = "Debra Toporowski (Qwulti'stunaat)"
    
    if name == "Amshen Phillip":
        name = "Joan Phillip (Amshen)"

    if name == "Laanas Davidson":
        name = "Tamara Davidson (Laanas)"

    found = bc_mlas.find_one({ 'name': name})

    if not found:
        print("Error for", name)
        continue
    
    else:
        pdf_tag = p.find_elements(By.TAG_NAME, 'a')[-1]
        pdf_url = pdf_tag.get_attribute('href')
        true_base_url = "https://lims.leg.bc.ca/pdms/file/content-committees/AccountabilityDocuments/MLAs/2025/Public%20Disclosures%20-%20CIO/"
        pdf_name = pdf_url.split('/')[-1].split('"')[0]
        name_to_pdf_dict[name] = slugify(pdf_name)+".pdf"
        name_list.append(name)
        urlretrieve(true_base_url + pdf_name, slugify(pdf_name)+".pdf")

def print_content(category, content, name):
    content = content.lstrip()
    content = content.rstrip()
    content = content.replace("S hares", "Shares") # Catch a small blip in some cases
    if (content not in ['n/a', 'N/A', "", " n/a"]):
        print({
            'name': name,
            'category': category,
            'content': content
        })

def read_pdf_basic2(name, pdf_path):
    # Create a reader object
    reader = PdfReader(pdf_path)
    
    # Extract text from second page
    all_pages = ""
    for p in reader.pages:
        all_pages += p.extract_text()

    lines = all_pages.split("\n")

    disclosure_type = ""
    content = ""
    for line in lines:
        if line.startswith("SOURCES OF INCOME"):
            disclosure_type = "Source(s) of Income"
            content = ""
            continue
    
        if line.startswith("ASSETS"):
            print_content(disclosure_type, content, name)
            disclosure_type = "Assets"
            content = ""
            continue
    
        if line.startswith("LIABILITIES"):
            print_content(disclosure_type, content, name)
            disclosure_type = "Liabilities"
            content = ""
            continue
    
        if line.startswith("GIFTS DISCLOSED"):
            print_content(disclosure_type, content, name)
            disclosure_type = "Gifts"
            content = ""
            continue

        # page break
        if "-2- " in line:
            continue

        if "- 2 -" in line:
            continue

        # Content is done
        if line.startswith("Filed with the Clerk of the Legislative Assembly"):
            print_content(disclosure_type, content, name)
            break

        if len(content) == 0:
            content += line.rstrip(" ")
        else:
            content += "\n"+line.rstrip(" ")

for name in name_list:
    read_pdf_basic2(name, name_to_pdf_dict[name])
