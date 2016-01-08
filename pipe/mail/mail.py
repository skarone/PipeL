import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

def sendMail( sender, recipient, message, subject, ip = '192.168.0.200', port= 25 ):
	msg = MIMEText(message)
	msg['Subject'] = subject
	msg['From'] = sender
	msg['To'] = ','.join(map(str, recipient))
	s = smtplib.SMTP( ip, port )
	s.set_debuglevel(1)
	s.sendmail(sender, recipient, msg.as_string())
	s.quit()

MAIL_MESSAGES = {
	'new_cache':{ 'message':'New Cache of Asset <AssetName> for Shot <ShotName>, by <UserName>','departments':['animation', 'lighting', 'producction']},
	'new_playblast':{'message':'New Playblast from Shot <ShotName> in Sequence <SequenceName>, by <UserName>','departments':['animation','producction']},
	'new_render':{'message':'New Render of layer <RenderLayer> for Shot <ShotName>, by <UserName>','departments':['composition', 'lighting', 'production']}
}

def replaceDataForMessage( message, data ):
	"""docstring for replaceDataForMessage"""
	for d in data.keys():
		message = message.replace( d, data[d] )
	return message

def getUsersInDepartments( departments ):
	"""docstring for getUsersInDepartments"""
	pass


def mailFromTool( mailMessageType, dataInMessageDict, sender, ip = '192.168.0.200', port= 25 ):
	"""mailMessageType: string corresponding to one of the MAIL_MESSAGES key values
	   dataInMessageDict: dict with AssetName, ShotName, UserName, SequenceName, RenderLayer
	   sender: string email of the person how send the mail
	   recipient: string array mails of person how will recieve mail"""
	message = replaceDataForMessage( MAIL_MESSAGES[ mailMessageType ][ 'message' ], dataInMessageDict )
	recipient = getUsersInDepartments( MAIL_MESSAGES[ mailMessageType ]['departments'] )
	sendMail( sender, recipient, message, mailMessageType, ip, port )


