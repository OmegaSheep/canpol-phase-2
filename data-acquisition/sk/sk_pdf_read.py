# from PyPDF2 import PdfReader # Works substantially worse
from pypdf import PdfReader

def print_pdf(name, pdf_path):
    # Create a reader object
    reader = PdfReader(pdf_path)
    
    # Extract text from second page
    for i in reader.pages:
        print(i.extract_text())

# literally does not matter because they are not machine readable, thanks Scott Moe 