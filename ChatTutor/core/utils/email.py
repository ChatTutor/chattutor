import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from numpy import random
from core.data import DataBase
from core.data.DataBase import VerificationCodeModel
import uuid


def random_with_N_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10**n) - 1
    return random.randint(range_start, range_end)


def random_code():
    return f"{uuid.uuid4()}"


class EmailSender:
    def __init__(self) -> None:
        self.password = os.getenv("VERITAI_EMAIL_PASSWD")
        self.sender_email = os.getenv(
            "VERITAI_EMAIL"
        )  # This must be the verified sender identity in your SendGrid account

    def send(self, user, add_to_db=True):
        base_url = os.getenv("SERVICE_BASE_URL")
        receiver_email = user.email
        message = MIMEMultipart("alternative")
        message["Subject"] = "Subject Here"
        message["From"] = self.sender_email
        message["To"] = receiver_email

        code = random_code()
        # Plain-text and HTML versions of the message
        text = f"""\
        <h1> VeritAI </h1>
        
        <h2> Welcome, {user.email}! </h2>
        
        <p>Verify your account <a clicktracking='off' href='{base_url}users/verify/{code}'> here! </a> </p>
        <br/>
        <p> Thank you! </p>
        """

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "html")

        # Attach parts into message container
        message.attach(part1)

        # Send the email
        try:
            with smtplib.SMTP_SSL("smtp.sendgrid.net", 465) as server:
                server.login("apikey", self.password)  # Note: the username is always 'apikey'
                server.sendmail(self.sender_email, receiver_email, message.as_string())
                DataBase().insert_verif(VerificationCodeModel(id=code, user_id=user.user_id))
                return code, True
        except Exception as e:
            print(f"Error sending email or adding to db: {e}")
            return 0, False
