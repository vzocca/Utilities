# -*- coding: utf-8 -*-
"""
Created on Tue Dec 23 17:34:39 2025

@author: vzocc
"""

import imaplib
import email
from email.header import decode_header
import os
from io import BytesIO
import ftplib
import tempfile
from pypdf import PdfReader, PdfWriter
import smtplib
from email.message import EmailMessage

KINDLE_EMAIL = "vzocca@kindle.com"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


FTP_HOST = "ftp.deepneural.net"
FTP_USER = "5834685@aruba.it"
FTP_PASS = "QeisdfZ2020!"

# --- Configuration ---
IMAP_SERVER = "imap.gmail.com"  # or your email provider
EMAIL_ACCOUNT = "documenti.portabili@gmail.com"
EMAIL_PASSWORD = "jewc cbzi imet fmcq"
REMOTE_DIR = "/deepneural.net/documenti.portabili/"  # API endpoint for upload
DOWNLOAD_FOLDER = "C:\\Users\\vzocc\\Downloads\\documenti.portabili"
SMTP_USER = EMAIL_ACCOUNT
SMTP_PASS = EMAIL_PASSWORD



#############################################################
# --- FTP Connection ---
def connect_ftp():
    print(f"🌐 Connecting to FTP: {FTP_HOST} ...")
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    print("✔ Connected to FTP server.\n")
    return ftp

#############################################################
# --- PDF Merge Helper ---
def merge_pdfs_overlay(local_file, remote_file, output_file):
    reader_local = PdfReader(local_file)
    reader_remote = PdfReader(remote_file)
    writer = PdfWriter()

    page_count = max(len(reader_local.pages), len(reader_remote.pages))

    for i in range(page_count):
        if i < len(reader_local.pages):
            page = reader_local.pages[i]
        else:
            page = reader_remote.pages[i]

        if i < len(reader_remote.pages):
            page.merge_page(reader_remote.pages[i])

        writer.add_page(page)

    with open(output_file, "wb") as f:
        writer.write(f)

#############################################################
# --- Upload with merge ---
def upload_file(ftp, local_file):
    """Upload a PDF to REMOTE_DIR, merging with remote if needed (Windows-safe)."""
    if not os.path.isfile(local_file):
        raise FileNotFoundError(f"File not found: {local_file}")

    filename = os.path.basename(local_file)

    # Ensure remote folder exists
    try:
        ftp.cwd(REMOTE_DIR)
    except:
        parts = REMOTE_DIR.strip("/").split("/")
        for part in parts:
            try:
                ftp.cwd(part)
            except:
                ftp.mkd(part)
                ftp.cwd(part)

    remote_files = ftp.nlst()

    if filename in remote_files:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_remote_path = os.path.join(tmpdir, "remote.pdf")
            temp_merged_path = os.path.join(tmpdir, "merged.pdf")

            # Download remote PDF
            with open(temp_remote_path, "wb") as f:
                ftp.retrbinary(f"RETR {filename}", f.write)

            # Merge remote on top of local PDF
            merge_pdfs_overlay(local_file, temp_remote_path, temp_merged_path)

            # Upload merged PDF
            with open(temp_merged_path, "rb") as f:
                ftp.storbinary(f"STOR {filename}", f)

            print(f"✅ Uploaded merged PDF: {filename}")
            
            # 🔴 ONLY HERE — merge happened
            send_to_kindle(temp_merged_path, filename)
            #send_to_kindle(local_file, os.path.basename(local_file))

    else:
        # No remote file exists, just upload
        with open(local_file, "rb") as f:
            ftp.storbinary(f"STOR {filename}", f)
        print(f"✅ Uploaded new PDF: {filename}")

#############################################################
# --- Email Retrieval ---
def retrieve_email():
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    mail.select("inbox")

    status, messages = mail.search(None, "UNSEEN")  # unread only
    email_ids = messages[0].split()
    downloaded_pdfs = []  # List of (file_path, email_id) tuples

    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        raw_subject = msg.get("Subject")
        if raw_subject is None:
            subject = "(no subject)"
        else:
            subject, encoding = decode_header(raw_subject)[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8", errors="ignore")
        print(f"Processing email: {subject}")

        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if part.get("Content-Disposition") is None:
                continue

            filename = part.get_filename()
            if not filename:
                continue

            filename, encoding = decode_header(filename)[0]
            if isinstance(filename, bytes):
                filename = filename.decode(encoding or "utf-8", errors="ignore")

            if not filename.lower().endswith(".pdf"):
                continue

            file_path = os.path.join(DOWNLOAD_FOLDER, filename)
            with open(file_path, "wb") as f:
                f.write(part.get_payload(decode=True))
            print(f"Saved PDF: {file_path}")

            downloaded_pdfs.append((file_path, email_id))

    mail.logout()
    return downloaded_pdfs

#############################################################
# --- Index HTML Generation ---
def generate_index_html(ftp):
    ftp.cwd(REMOTE_DIR)
    files = ftp.nlst()
    pdf_files = sorted(f for f in files if f.lower().endswith(".pdf"))

    html_lines = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head>",
        "  <meta charset='UTF-8'>",
        "  <title>Documenti Portabili</title>",
        "</head>",
        "<body style='font-size: 18px;'>",
        "  <h1>Documenti Portabili</h1>",
        "  <ul>",
    ]

    for pdf in pdf_files:
        html_lines.append(f"    <li><a href=\"{pdf}\">{pdf}</a></li>")

    html_lines.extend([
        "  </ul>",
        "",
        "  <script src=\"/log.js\"></script>",
        "</body>",
        "</html>"
    ])

    html_content = "\n".join(html_lines)
    print("⬆ Uploading index.html")
    bio = BytesIO(html_content.encode("utf-8"))
    ftp.storbinary("STOR index.html", bio)
    print("✅ index.html generated and uploaded successfully")
 
#############################################################
    
def send_to_kindle(pdf_path, attachment_name):
    """Send a PDF file to Kindle via Email-to-Kindle."""
    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = KINDLE_EMAIL
    msg["Subject"] = ""

    with open(pdf_path, "rb") as f:
        pdf_data = f.read()

    msg.add_attachment(
        pdf_data,
        maintype="application",
        subtype="pdf",
        filename=attachment_name,   # 👈 explicit filename
    )

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    print(f"📖 Sent merged PDF to Kindle: {attachment_name}")


#############################################################

# --- Main ---
if __name__ == "__main__":
    downloaded_pdfs = retrieve_email()
    if not downloaded_pdfs:
        print("No new PDFs to upload.")
    else:
        ftp = connect_ftp()
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select("inbox")
        for file_path, email_id in downloaded_pdfs:
            upload_file(ftp, file_path)
            # Mark email as read only after successful upload
            mail.store(email_id, "+FLAGS", "\\Seen")
        mail.logout()
        generate_index_html(ftp)