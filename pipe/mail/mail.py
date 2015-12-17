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
	s = smtplib.SMTP('10.0.2.15',25 )
	s.set_debuglevel(1)
	s.sendmail(sender, recipient, msg)
	s.quit()

MAIL_MESSAGES = {
	'new_cache':'New Cache of Asset <AssetName> for Shot <ShotName>, by <UserName>',
	'new_playblast':'New Playblast from Shot <ShotName> in Sequence <SequenceName>, by <UserName>',
	'new_render':'New Render of layer <RenderLayer> for Shot <ShotName>, by <UserName>'
}
