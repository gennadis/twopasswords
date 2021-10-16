import os
import smtplib
import dotenv
from email.message import EmailMessage


dotenv.load_dotenv()
email_address = os.environ.get("LOGIN")
email_password = os.environ.get("PASSWORD")
last_image_file = os.environ.get("LAST_IMAGE_PATH")


class Email:
    def __init__(self, subject: str, content: str, attachment: str) -> None:
        self.subject = subject
        self.content = content
        self.attachment = attachment

    def send_email(self) -> None:
        msg = EmailMessage()
        msg["Subject"] = self.subject
        msg["From"] = email_address
        msg["To"] = email_address
        msg.set_content(self.content)

        with open(self.attachment, "rb") as attach:
            msg.add_attachment(
                attach.read(),
                maintype="application",
                subtype="octet-stream",
                filename=attach.name,
            )

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(email_address, email_password)
            smtp.send_message(msg)
