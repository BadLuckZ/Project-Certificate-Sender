import os
import csv
import base64
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import img2pdf
import resend
from dotenv import load_dotenv

# =============================================
# Configuration
CSV_FILE = "name.csv"
MAX_COUNTER = 1
CERTIFICATE_PATH = "certificate.png"
FONT_PATH = "IBMPlexSansThai-SemiBold.ttf"
FONT_SIZE = 48
NAME_POSITION = (400, 400)
NAME_COLOR = (255, 0, 0)
# ============================================

def read_csv(filename):
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows

def write_csv(filename, rows, fieldnames):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def generate_certificate(name):
    img = Image.open(CERTIFICATE_PATH).convert("RGBA")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_PATH, size=FONT_SIZE)

    # Fill with red color
    draw.text(NAME_POSITION, name, font=font, fill=NAME_COLOR)

    png_path = f"Certificate_CUOPH2026_{name}.png"
    pdf_path = f"Certificate_CUOPH2026_{name}.pdf"

    img.save(png_path)
    with open(pdf_path, "wb") as f:
        f.write(img2pdf.convert(png_path))

    return png_path, pdf_path

def send_email(to_email: str, name: str, attachment_path: list):
    html_content = f"""
        <h1>Hello {name}!</h1>
        <p>This is the email sending system powered by Resend.</p>
        <p>Sent to: {to_email}</p>
        <p>Sent at: {datetime.now().isoformat()}</p>
    """
    attachments = []
    try:
        for path in attachment_path:
            with open(path, "rb") as f:
                file_content = f.read()
                
            attachments.append({
                "filename": os.path.basename(path),
                "content": base64.b64encode(file_content).decode(),
            })
            
    except Exception as e:
        print(f"Error reading attachment: {e}")

    sender_name = "Staff CUOPH2026"
    sender_email = "staff@cuoph2026.com"
    sending_topic = "CUOPH2026 Certificate"

    try:
        payload = {
            "from": f"{sender_name} <{sender_email}>",
            "to": [to_email],
            "subject": sending_topic,
            "html": html_content,
        }
        
        if attachments:
            payload["attachments"] = attachments

        resend.Emails.send(payload)
        return True
    
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def main():
    counter = 0
    rows = read_csv(CSV_FILE)

    if rows and 'sent' not in rows[0]:
        for row in rows:
            row['sent'] = ''

    updated = False
    for row in rows:
        if counter >= MAX_COUNTER:
            print(f"LIMIT {MAX_COUNTER} emails. Stopping.")
            break

        if not row.get('sent') or row['sent'].strip().upper() != 'TRUE':
            email = row['email']
            name = row['name']
            print(f"Sending email to {email} ({name}) ...")

            png_path, pdf_path = generate_certificate(name)
            if send_email(email, name, [png_path, pdf_path]):
                row['sent'] = 'TRUE'
                updated = True
                counter += 1
                print("Success!")
            else:
                row['sent'] = 'FALSE'
                print("Fail!")
            os.remove(pdf_path) 
            os.remove(png_path)

    if updated:
        fieldnames = list(rows[0].keys())
        write_csv(CSV_FILE, rows, fieldnames)

load_dotenv()
env = os.environ.get("NODE_ENV", "development")
resend.api_key = os.environ.get(f"RESEND_API_{env.upper()}", "")

main()