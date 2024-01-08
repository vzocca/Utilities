# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 08:45:08 2024

@author: vzocc
"""


from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta

import subprocess



def open_pdf_file(file_path):
    try:
        subprocess.Popen([file_path], shell=True)
    except Exception as e:
        print(f"Error opening the PDF file: {e}")
        
def initial_page(name, phone_number):
    #c = canvas.Canvas(f"{num_parts}_parts_dates.pdf", pagesize=letter)
    # First Page: Bullet Journal
    c.setFont("Helvetica-Bold", 30)
    c.drawString(180, 600, "Bullet Journal")
    c.setFont("Helvetica", 12)
    c.drawString(50, 550, name)
    c.drawString(50, 530, phone_number)
    c.showPage()
    
def mental_inventory(c):
    #c.setPageSize((792, 612))  # Set landscape layout
    
    # Set initial positions for the page
    initial_y_position = 30
    
    page_width, page_height = letter
  
    x_pos = [i * page_height//3 + 50  for i in range(3)]
    c.rotate(90)
    
    # Second Page: Mental Inventory (Landscape layout)
    #c = canvas.Canvas(f"{num_parts}_parts_dates.pdf", pagesize=(792, 612))  # Set landscape layout)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(page_width/2. + 10, -initial_y_position, "Mental Inventory")
    c.setFont("Helvetica", 12)

    c.drawString(x_pos[0], -initial_y_position-40, "Working On:")
    c.drawString(x_pos[1], -initial_y_position-40, "Should be Working On:")
    c.drawString(x_pos[2], -initial_y_position-40, "Want to be Working On:")
    
    c.setLineWidth(0.2)  # Set the line thickness (you can adjust this value)
    
    for x in [i * page_height//3  for i in range(1, 3)]:
        c.line(x, -page_width, x, 0)
        
    c.line(10, -initial_y_position-10, page_height-10, -initial_y_position-10)
    c.line(10, -initial_y_position-60, page_height-10, -initial_y_position-60)
    
    #c.setPageSize((612, 792))
    c.showPage()
    
def index():
    # Third Page: Index
    
    # Set initial positions for the page
    x_position = 10
    y_border = 30
    
    page_width, page_height = letter
    initial_y_position = page_height-y_border
    
    draw_lines(c, page_width, page_height, x_position)
    
    #c = canvas.Canvas(f"{num_parts}_parts_dates.pdf", pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x_position, initial_y_position, "Index")
    c.showPage()
    
def future_log():
    # Third Page: Index
    
    # Set initial positions for the page
    x_position = 10
    y_border = 30
    
    page_width, page_height = letter
    initial_y_position = page_height-y_border
    
    draw_lines(c, page_width, page_height, x_position)
    
    #c = canvas.Canvas(f"{num_parts}_parts_dates.pdf", pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x_position, initial_y_position, "Future Log")
    c.showPage()

def birthdays():
    # Fourth Page: Birthdays
    
    # Set initial positions for the page
    x_position = 10
    y_border = 30
    
    page_width, page_height = letter
    initial_y_position = page_height-y_border
    
    draw_lines(c, page_width, page_height, x_position)
    
    c.setLineWidth(0.2)  # Set the line thickness (you can adjust this value)
        
    c.line(page_width/2., page_height - 10, page_width/2., 10)

    #c = canvas.Canvas(f"{num_parts}_parts_dates.pdf", pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x_position, initial_y_position, "Birthdays")
    c.showPage()
    
def tasks(month):
    #c = canvas.Canvas(f"{num_parts}_parts_dates.pdf", pagesize=letter)
    
    # Set initial positions for the page
    x_position = 10
    y_border = 30
    
    page_width, page_height = letter
    initial_y_position = page_height-y_border
    
    draw_lines(c, page_width, page_height, x_position)
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x_position, initial_y_position, f"{month} Tasks")
    c.showPage()
        
 
def appointments(month):
    #c = canvas.Canvas(f"{num_parts}_parts_dates.pdf", pagesize=letter)
    
    # Set initial positions for the page
    x_position = 10
    y_border = 30
    
    page_width, page_height = letter
    initial_y_position = page_height-y_border
    
    draw_lines(c, page_width, page_height, x_position)
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x_position, initial_y_position, f"{month} Appointments")
    c.showPage()
    c.showPage()
        
        
# Function to create a PDF with configurable number of parts for each date
def create_pdf(num_parts):

    # Starting date
    start_date = datetime(2024, 1, 1)
    # Ending date
    end_date = datetime(2024, 12, 31)
    
    page_width, page_height = letter

    # Set initial positions for the first page
    x_position = 10
    y_border = 30
    
    initial_y_position = page_height-y_border

    # Set the gap between the parts
    gap = (792-2*y_border)/num_parts
    
    initial_page("Valentino Zocca", "202 640 1381")
    
    mental_inventory(c)
    
    index()
    birthdays()
    future_log()
    c.showPage()
    
    tasks("January")
    appointments("January")
    
    new_month = False

    while start_date <= end_date:
        #if start_date.day == 1
            
        y_positions = [initial_y_position - i * gap  for i in range(num_parts)]
        
        draw_lines(c, page_width, page_height, x_position)

        for i in range(num_parts):
            # Write each part of the date
            date_string = (start_date + timedelta(i)).strftime("%d %B")
            c.setFont("Helvetica", 12)
            c.drawString(x_position, y_positions[i], date_string)
            
            next_date = start_date + timedelta(i+1)
            # If the next day's month changes, create a new page
            
            if next_date.month != start_date.month:
                new_month = True
                c.showPage()  # Create a new page
                c.setFont("Helvetica", 12)  # Reset font settings
                initial_y_position = page_height-y_border  # Reset y_position for the new page
                
                month_number = str(next_date.month)
                month_name  = datetime.strptime(month_number, '%m').strftime('%B')
                tasks(month_name)
                appointments(month_name)
                
                break
            
            # Move to the next position for the next iteration
            initial_y_position -= gap * (num_parts - 1)

        if new_month == True:
            new_month = False
        else:
            c.showPage()  # Create a new page
            
        c.setFont("Helvetica", 12)  # Reset font settings
        initial_y_position = page_height-y_border  # Reset y_position for the new page

        # Move to the next date
        start_date += timedelta(i+1)

    c.save()
    print(f"PDF with {num_parts} parts per date generated successfully!")

    

def draw_lines(c, page_width, page_height, x_position):
        line_gap = 30
        line_y_positions = [i * line_gap for i in range(1, int(page_height) // line_gap)]
        
        c.setLineWidth(0.2)  # Set the line thickness (you can adjust this value)
        for y_position in line_y_positions:
            c.line(x_position, y_position, page_width - x_position, y_position)
    


# Define the number of parts you want
num_parts = 2

#c = canvas.Canvas(f"{num_parts}_parts_dates.pdf", pagesize=letter)
c = canvas.Canvas("2024 Bullet Journal.pdf", pagesize=letter)

# Call the function to create the PDF with the specified number of parts
create_pdf(num_parts)

# open file to check result
open_pdf_file("2024 Bullet Journal.pdf")
