import os
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

# Load environment variables from .env
# load_dotenv()
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

class MAIL:
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS") == "True"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL") == "True"

    @staticmethod
    def _create_server_connection():
        server = None
        if MAIL.MAIL_USE_SSL:
            server = smtplib.SMTP_SSL(MAIL.MAIL_SERVER, int( MAIL.MAIL_PORT))
        else:
            server = smtplib.SMTP(MAIL.MAIL_SERVER, int(MAIL.MAIL_PORT))
            if MAIL.MAIL_USE_TLS:
                server.starttls()
        server.login(MAIL.MAIL_USERNAME, MAIL.MAIL_PASSWORD)
        return server
    
    @staticmethod
    def sendmail(to, from_name, subject, body):
        msg = EmailMessage()
        msg["From"] = f"{from_name} <{MAIL.MAIL_USERNAME}>"
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        
        with MAIL._create_server_connection() as server:
            server.send_message(msg)
    
    @staticmethod
    def sendHtmlMail(to, from_name, subject, body, html):
        msg = EmailMessage()
        msg["From"] = f"{from_name} <{MAIL.MAIL_USERNAME}>"
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        msg.add_alternative(html, subtype='html')

        with MAIL._create_server_connection() as server:
            server.send_message(msg)
    
    @staticmethod
    def sendHtmlMailWithFiles(to, from_name, subject, body, html, files):
        msg = MIMEMultipart()
        msg["From"] = f"{from_name} <{MAIL.MAIL_USERNAME}>"
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        msg.attach(MIMEText(html, "html"))
        
        for file_path in files:
            with open(file_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
                msg.attach(part)
        
        with MAIL._create_server_connection() as server:
            server.send_message(msg)


# Example of Sending. 

# MAIL.sendmail("recipient@example.com", "Sender Name", "Test Subject", "Test Body")
# MAIL.sendHtmlMail("recipient@example.com", "Sender Name", "Test Subject", "Test Body", "<h1>Test HTML</h1>")
# MAIL.sendHtmlMailWithFiles(
#     "recipient@example.com", 
#     "Sender Name", 
#     "Test Subject with Attachment", 
#     "Test Body", 
#     "<h1>HTML with Attachment</h1>", 
#     ["path/to/file1.txt", "path/to/file2.pdf"]
# )

