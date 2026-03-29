# Project-Certificate-Sender

**Disclaimer:** This project is specifically used for sending emails with the certificate in the CU Openhouse 2026 event...

## Setup Instructions

1. **Prepare Recipient Data**
   - Copy `name.example.csv` to `name.csv` and fill in your real data.

2. **Configure Environment Variables**
   - Copy `.env.example` to `.env` and fill your values

3. **Add Attachment**
   - Replace `certificate_template.png` with your png file and name it `certificate.png`

4. **Install Dependencies**

   ```
   pip install resend python-dotenv pillow img2pdf
   ```

5. **Run the Program**
   ```
   python main.py
   ```

---

**Notes:**

- The script will send emails with the attachment to each recipient in `name.csv` and update the file with the sent status.
