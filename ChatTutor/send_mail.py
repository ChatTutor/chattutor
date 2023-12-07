import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content


# need to make sendgrid acc
my_sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))

# Change to your verified sender
from_email = Email("your_email@example.com")

# Change to your recipient
to_email = To("destination@example.com")

subject = "Lorem ipsum dolor sit amet"
content = Content("text/plain", "consectetur adipiscing elit")

mail = Mail(from_email, to_email, subject, content)

# Get a JSON-ready representation of the Mail object
mail_json = mail.get()

# Send an HTTP POST request to /mail/send
response = my_sg.client.mail.send.post(request_body=mail_json)