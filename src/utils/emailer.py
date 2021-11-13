"""
# TODO: should place some nice text here...

This module is responsible for generating 
Authentification reports and forwarding them
via Email.
...

"""

from smtplib import SMTP_SSL

from config import config_loader
from email.message import EmailMessage

# load configuration
file_paths, email_settings = config_loader.load()


def send_auth_report(content: str):
    """
    Sends authentification report if one was not successfull.

    Parameters
    ----------
    content : str
        The report's email body content

    """

    EmailSender(
        "TwoPasswords Auth Report",
        content,
        email_settings["address"],
        email_settings["password"],
        file_paths["last_image"],
        email_settings["server"],
        email_settings["port"],
    ).send_email()


class EmailSender:
    """
    A class used to represent an Email report.

    Attributes
    ----------
    subject : str
        Email subject
    content : str
        Email content
    email_address : str
        Email account address
        Both 'From' and 'To'
    email_password: str
        Email account password
    attachment : str
        Email attachment file path
    server : str
        SMTP server address
    port: str
        SMTP server port

    Methods
    -------
    send_email
        Sends the Email with an attachment

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
    ):

        self.subject = subject
        self.content = content
        self.email_address = email_address
        self.email_password = email_password
        self.attachment = attachment
        self.server = server
        self.port = port

    def send_email(self) -> None:
        """
        Creates and sends email from and to user's email address.
        Last image taken by FaceAuth module is an attachment.

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
