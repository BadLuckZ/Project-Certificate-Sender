import os
import csv
import base64
from PIL import Image, ImageDraw, ImageFont
import img2pdf
import resend
from dotenv import load_dotenv
from pythainlp.util import normalize

# =============================================
# Configuration
CSV_FILE = "nameMock.csv"               # CSV Name
MAX_COUNTER = 400
CERTIFICATE_PATH = "certificate.png"
FONT_PATH = "Sarabun-Regular.ttf"

NAME_POSITION = (50, 42)                # Name Position: 50% from left, 42% from top
NAME_COLOR = (0, 0, 0)                  # Black
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
    formatted_name = normalize(name)
    FONT_SIZE = 72
    if len(name) > 30:
        FONT_SIZE = 60
    
    img = Image.open(CERTIFICATE_PATH).convert("RGBA")
    imgWidth, imgHeight = img.size
    
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_PATH, size=FONT_SIZE)

    # Target the center of text container
    bbox = font.getbbox(name)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    center_x, center_y = int(imgWidth * NAME_POSITION[0] / 100), int(imgHeight * NAME_POSITION[1] / 100)
    x = center_x - text_width // 2
    y = center_y - text_height // 2

    # Fill Color
    draw.text((x, y), formatted_name, font=font, fill=NAME_COLOR)

    png_path = f"Certificate_CUOPH2026_{name}.png"
    pdf_path = f"Certificate_CUOPH2026_{name}.pdf"

    img.save(png_path)
    with open(pdf_path, "wb") as f:
        f.write(img2pdf.convert(png_path))

    return png_path, pdf_path

def send_email(to_email: str, name: str, attachment_path: list):
    html_content = f"""
        <p>เรียน คุณ {name}</p>
        <p>ทางคณะผู้จัดงาน Chula Open House 2026 ขอขอบคุณที่ให้ความสนใจ และเข้าร่วมกิจกรรมเมื่อวันที่ 28-29 มีนาคม 2569 ที่ผ่านมา</p>
        <p>เพื่อเป็นการตอบแทนความตั้งใจและแสดงความยินดีในการร่วมค้นหาตัวตนและเส้นทางการศึกษาต่อ ณ จุฬาลงกรณ์มหาวิทยาลัย ทางเราได้แนบ E-Certificate มาพร้อมกับอีเมลฉบับนี้</p>
        <p>หวังเป็นอย่างยิ่งว่าประสบการณ์ในครั้งนี้จะเป็นแรงบันดาลใจและเป็นประโยชน์ต่อก้าวต่อไปในอนาคตของคุณ แล้วพบกันใหม่ในโอกาสหน้า</p>
        <p>ขอแสดงความนับถือ</p>
        <p>ทีมงาน Chula Open House 2026</p>
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
    sending_topic = f"เกียรติบัตรการเข้าร่วมงาน Chula Open House 2026 - {name}"

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
            email = row['email'].lower().strip()
            name = row['name'].strip()
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