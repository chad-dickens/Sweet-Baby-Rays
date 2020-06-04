"""
Email Module - Contains functions for use with sending and retrieving emails
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os.path
import datetime


def send_email_365(email_recipient, email_subject, email_message,
                   email_sender, email_password, attachments=tuple()):
    """
    Function to send emails using office 365
    :param email_recipient: string for who will receive the email.
    For multiple recipients combine them with spaces and commas.
    :param email_subject: string subject
    :param email_message: string message
    :param email_sender: string email address
    :param email_password: string password
    :param attachments: tuple containing string file names
    :return: Will return a tuple containing two elements. The first element will be a boolean value
    of whether the email was sent successfully or not. The second element will be a
    string of what happened with timestamp.
    """

    # Creating timestamp
    time_zone = datetime.datetime.now().astimezone().tzinfo
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    time_stamp = '{} {}'.format(current_time, time_zone)

    # Creating email
    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = email_recipient
    msg['Subject'] = email_subject
    msg.attach(MIMEText(email_message))

    # Adding attachments
    try:
        for item in attachments:
            part = MIMEBase('application', "octet-stream")
            with open(item, 'rb') as file:
                part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                            'attachment; filename="{}"'.format(os.path.basename(item)))
            msg.attach(part)

    except Exception as err:
        return (False, '{}\nUnable to add attachments {} to email.\n'
                'Error Description: {}.\n'.format(time_stamp, attachments, err))

    # Connecting to server and sending our email
    try:
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login(email_sender, email_password)
        server.sendmail(email_sender, email_recipient, msg.as_string())
        server.quit()

    except Exception as err:
        return (False, '{}\nUnable to send email to {}.\n'
                'Error Description: {}.\n'.format(time_stamp, email_recipient, err))

    # Confirming if successful
    else:
        return (True, '{}\nEmail sent successfully to recipient {} with attachments {}.\n'
                .format(time_stamp, email_recipient, attachments))
