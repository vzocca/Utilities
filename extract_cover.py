# -*- coding: utf-8 -*-
"""
Created on Wed Oct 29 09:59:32 2025

@author: vzocc
"""

import fitz  # pip install PyMuPDF
from PIL import Image
from PyPDF2 import PdfMerger
from PyPDF2 import PdfReader, PdfWriter
import os

dpi_size = 300

# Load the original cover file
reader = PdfReader("C:\\Users\\vzocc\\Documents\\GitHub\\Il-sapore-del-tempo\\cover.pdf")

# --- Extract the front page ---
front_writer = PdfWriter()
front_writer.add_page(reader.pages[0])
with open("C:\\Users\\vzocc\\Documents\\GitHub\\Il-sapore-del-tempo\\front_cover.pdf", "wb") as f:
    front_writer.write(f)

# --- Extract the back page (if it exists) ---
if len(reader.pages) > 1:
    back_writer = PdfWriter()
    back_writer.add_page(reader.pages[1])
    with open("C:\\Users\\vzocc\\Documents\\GitHub\\Il-sapore-del-tempo\\back_cover.pdf", "wb") as f:
        back_writer.write(f)


def get_pdf_size(pdf_path):
    reader = PdfReader(pdf_path)
    # Get the first page
    page = reader.pages[0]
    # MediaBox gives coordinates: lower-left-x, lower-left-y, upper-right-x, upper-right-y
    media_box = page.mediabox
    width = float(media_box.width)
    height = float(media_box.height)
    return width, height


base_path = r"C:\Users\vzocc\Documents\GitHub\Il-sapore-del-tempo"
#base_path = r"C:\Users\vzocc\Documents\GitHub\cento_passi"
#base_path = r"C:\Users\vzocc\Documents\GitHub\The-Wall"

libro = "\il_sapore_del_tempo.pdf"
#libro = "\BRILLO_manoscritto_trovato_stanze_small.pdf"
#libro = "\The-Wall_edited_small.pdf"
    
# Paths to your PDFs

front_cover_path = base_path + r"\front_cover.pdf"
book_path = base_path + libro
back_cover_path = base_path + r"\back_cover.pdf"
    
cover_path = base_path + r"\cover.pdf"
output_path = base_path + r"\full_book_sapore.pdf"
#output_path = base_path + r"\full_book_brillo.pdf"
    
book_width, book_height = get_pdf_size(book_path)    
    
    
if os.path.exists(cover_path):    
    doc = fitz.open(cover_path)
    page = doc[0]
    
    # Render page to a pixel map
    pix = page.get_pixmap(dpi=dpi_size)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    # Split in half
    width, height = img.size
    mid = width // 2
    
    print (mid*72/dpi_size, height*72/dpi_size)
    
    diffx = round((mid*72/dpi_size-book_width)*dpi_size/72)
    diffy = round((height*72/dpi_size-book_height)*dpi_size/72)
    
    
    x = (diffx-60)/2.
    y = diffy/2.
    
    #back = img.crop((47, 37, mid-107, height-37))
    #front = img.crop((mid+107, 37, width-47, height-37))
    
    back = img.crop((x, y, mid-60-x, height-y))
    front = img.crop((mid+60+x, y, width-x, height-y))
    
    
    # Save as PDFs
    back.save(back_cover_path, "PDF", resolution=300.0)
    front.save(front_cover_path, "PDF", resolution=300.0)


# Create a PdfMerger object
merger = PdfMerger()

# Append PDFs in order
merger.append(front_cover_path)
merger.append(book_path)
merger.append(back_cover_path)

# Write out the merged PDF
merger.write(output_path)
merger.close()

print(f"Merged PDF saved as {output_path}")

front_width, front_height = get_pdf_size(front_cover_path)
back_width, back_height = get_pdf_size(back_cover_path)


print(f"Front cover size: {front_width} x {front_height}")
print(f"Book size: {book_width} x {book_height}")
print(f"Back cover size: {back_width} x {back_height}")