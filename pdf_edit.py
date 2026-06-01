# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 16:15:55 2026

@author: vzocc
"""

from PyPDF2 import PdfReader, PdfWriter

def estrai_pagine(input_pdf, output_pdf, pagine):
    """
    input_pdf: percorso del file PDF di origine
    output_pdf: percorso del file PDF di destinazione
    pagine: lista di numeri di pagina (partendo da 1)
    """
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for p in pagine:
        index = p - 1  # PyPDF2 usa indice da 0
        if 0 <= index < len(reader.pages):
            writer.add_page(reader.pages[index])
        else:
            print(f"Pagina {p} non valida")

    with open(output_pdf, "wb") as f:
        writer.write(f)

# Esempio di utilizzo
input_file = "input.pdf"
output_file = "output.pdf"

for i in range(1,13):
    pagine_da_estrarre = [114+i]  # pagine che vuoi salvare
    
    output = "C:\\Users\\vzocc\\Documents\\GitHub\\Notizie\\fumetti\\cine...no" + str(i) + ".pdf"
    
    estrai_pagine("C:\\Users\\vzocc\\Downloads\\topolino 0711.pdf", output, pagine_da_estrarre)