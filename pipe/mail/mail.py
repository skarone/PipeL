import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

# Open a plain text file for reading.  For this example, assume that
# the text file contains only ASCII characters.
# Create a text/plain message

def sendMail( sender, recipient, message, subject ):
	msg = MIMEText(message)
	msg['Subject'] = subject
	msg['From'] = sender
	msg['To'] = ','.join(map(str, recipient)) 
	print msg
	s = smtplib.SMTP('localhost')
	s.set_debuglevel(1)
	s.sendmail(sender, recipient, msg.as_string())
	s.quit()
