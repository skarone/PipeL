"""
Proxy smtp to a starttls server with authentication, from a local
connection.
"""
from pipe.mail.inbox import Inbox
from smtplib import SMTP

inbox = Inbox(address='0.0.0.0', port=4467)

SMTP_HOST = 'mail.example.com'
SMTP_USERNAME = 'username'
SMTP_PASSWORD = 'password'

@inbox.collate
def handle(to='iniaki84@gmail.com', sender = 'coco@mail.example.com', body = 'mierda'):
    """
    Forward a message via an authenticated SMTP connection with
    starttls.
    """
    conn = SMTP(SMTP_HOST, 25, 'localhost')

    conn.starttls()
    conn.ehlo_or_helo_if_needed()
    conn.login(SMTP_USERNAME, SMTP_PASSWORD)
    conn.sendmail(sender, to, body)
    conn.quit()
if __name__ == '__main__':
    inbox.dispatch()
#inbox.serve(address='0.0.0.0', port=4467)
