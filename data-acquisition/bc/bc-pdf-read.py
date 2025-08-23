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

def print_content(category, content, name):
    content = content.lstrip()
    content = content.rstrip()
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

        # Content is done
        if line.startswith("Filed with the Clerk of the Legislative Assembly"):
            print_content(disclosure_type, content, name)
            break

        if len(content) == 0:
            content += line.rstrip(" ")
        else:
            content += "\n"+line.rstrip(" ")


read_pdf_basic2("fuckin britne", "anderson-20g-202025-pdf.pdf")