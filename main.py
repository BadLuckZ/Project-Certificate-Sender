import os
import csv
import base64
from datetime import datetime
import resend
from dotenv import load_dotenv

CSV_FILE = "name.csv"
MAX_COUNTER = 1

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

def send_email(to_email, name):
    html_content = f"""
        <h1>Hello {name}!</h1>
        <p>This is the email sending system powered by Resend.</p>
        <p>Sent to: {to_email}</p>
        <p>Sent at: {datetime.now().isoformat()}</p>
    """
    attachment_path = "certificate.png"
    try:
        with open(attachment_path, "rb") as f:
            file_content = f.read()
        attachment = {
            "filename": attachment_path,
            "content": base64.b64encode(file_content).decode(),
        }
    except Exception as e:
        print(f"Error reading attachment: {e}")
        attachment = None
        
    sender_name = os.environ.get("SENDER_NAME", "Sender")
    sender_email = os.environ.get("SENDER_EMAIL", "test@example.com")
    sending_topic = os.environ.get("SENDING_TOPIC", "No Subject")

    try:
        payload = {
            "from": f"{sender_name} <{sender_email}>",
            "to": [to_email],
            "subject": sending_topic,
            "html": html_content,
        }
        if attachment:
            payload["attachments"] = [attachment]
            
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
            if send_email(email, name):
                row['sent'] = 'TRUE'
                updated = True
                counter += 1
                print("Success!")
            else:
                row['sent'] = 'FALSE'
                print("Fail!")
                
    if updated:
        fieldnames = list(rows[0].keys())
        write_csv(CSV_FILE, rows, fieldnames)

env = os.environ.get("NODE_ENV", "development")
resend.api_key = os.environ.get(f"RESEND_API_{env.upper()}", "")

load_dotenv()
env = os.environ.get("NODE_ENV", "development")
resend.api_key = os.environ.get(f"RESEND_API_{env.upper()}", "")

main()