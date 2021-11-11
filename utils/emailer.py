from smtplib import SMTP_SSL

from config import config_loader
from email.message import EmailMessage


"""
------------------
IT"S ALL GOOD HERE
------------------
"""

file_paths, email_settings = config_loader.load()


class EmailSender:
    """
    Class for sending emails via Gmail service
    """

    def __init__(
        self,
        subject: str,
        content: str,
        email_address: str,
        email_password: str,
        attachment: str,
        server: str,
        port: int,
    ) -> None:

        self.subject = subject
        self.content = content
        self.email_address = email_address
        self.email_password = email_password
        self.attachment = attachment
        self.server = server
        self.port = port

    def send_email(self) -> None:
        """
        Compose and send an email with an attachment
        """
        message = EmailMessage()
        message["Subject"] = self.subject
        message["From"] = self.email_address
        message["To"] = self.email_address
        message.set_content(self.content)

        with open(self.attachment, "rb") as attach:
            message.add_attachment(
                attach.read(),
                maintype="application",
                subtype="octet-stream",
                filename=attach.name,
            )

        with SMTP_SSL(self.server, self.port) as smtp:
            smtp.login(self.email_address, self.email_password)
            smtp.send_message(message)


def send_auth_report(content: str):
    EmailSender(
        "TwoPasswords Auth Report",
        content,
        email_settings["address"],
        email_settings["password"],
        file_paths["last_image"],
        email_settings["server"],
        email_settings["port"],
    ).send_email()
