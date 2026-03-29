# Project-Certificate-Sender

**Disclaimer:** This project is intended for sending emails with the certificate for the CU Openhouse 2026 event only.

## Setup Instructions

1. **Prepare Recipient Data**
   - Copy `name.example.csv` to `name.csv` and fill in your real data.

2. **Configure Environment Variables**
   - Copy `.env.example` to `.env` and fill your value

3. **Add Attachment**
   - Replace `certificate_template.png` with your png file and name it `certificate.png`

4. **Install Dependencies**

   ```
   pip install resend python-dotenv
   ```

5. **Run the Program**
   ```
   python main.py
   ```

---

**Notes:**

- The script will send emails with the attachment to each recipient in `name.csv` and update the file with the sent status.
- You can set the maximum number of emails to send per run by changing the `MAX_COUNTER` variable in `main.py`.
