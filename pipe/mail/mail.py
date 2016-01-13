import smtplib
import pipe.file.file as fl

# Import the email modules we'll need
from email.mime.text import MIMEText

MAIL_MESSAGES = {
	'new_cache':{
		'message':'\bNew Cache\nAsset: <AssetName>\nSequence: <SequenceName>\nShot: <ShotName>\nUser: <UserName>',
		'departments':['animation', 'lighting', 'production'],
		'subject':'[CACHE] [<ProjectName>] [<SequenceName>] [<ShotName>] [<AssetName>]'},
	'new_playblast':{
		'message':'New Playblast\nSequence: <SequenceName>\nShot: <ShotName>\nUser: <UserName>',
		'departments':['animation','production'],
		'subject':'[PLAYBLAST] [<ProjectName>] [<SequenceName>] [<ShotName>]'},
	'new_render':{
		'message':'New Render\nRenderlayer: <RenderLayer>\nSequence: <SequenceName>\nShot: <ShotName>\nUser: <UserName>',
		'departments':['compo', 'lighting', 'production'],
		'subject':'[RENDER] [<ProjectName>] [<SequenceName>] [<ShotName>] [<RenderLayer>]'}
}

def sendMail( sender, recipient, message, subject, ip = '192.168.0.1', port= 25 ):
	msg = MIMEText(message)
	msg['Subject'] = subject
	msg['From'] = sender
	msg['To'] = ','.join(map(str, recipient))
	s = smtplib.SMTP( ip, port )
	s.set_debuglevel(1)
	s.sendmail(sender, recipient, msg.as_string())
	s.quit()

def replaceDataForMessage( message, data ):
	"""docstring for replaceDataForMessage"""
	mes = message['message']
	subject = message['subject']
	for d in data.keys():
		mes = mes.replace( d, data[d] )
		subject = subject.replace( d, data[d] )
	return mes, subject

def getUsersInDepartments( departments, departmentsFilesPaths ):
	"""docstring for getUsersInDepartments"""
	fils = [a for a in fl.filesInDir( departmentsFilesPaths, True, '.mails' ) if any( [ a.name == d for d in departments ] )]
	mails = []
	for f in fils:
		mails += f.data.replace( '\r\n','' ).split( ',' )
	mails += ['iurruty@bitt.com']
	return list(set(mails))

def mailFromTool( mailMessageType, dataInMessageDict, sender, departmentsFilesPaths, ip = '192.168.0.1', port= 25 ):
	"""mailMessageType: string corresponding to one of the MAIL_MESSAGES key values
	   dataInMessageDict: dict with AssetName, ShotName, UserName, SequenceName, RenderLayer
	   sender: string email of the person how send the mail
	   recipient: string array mails of person how will recieve mail"""
	message, subject = replaceDataForMessage( MAIL_MESSAGES[ mailMessageType ], dataInMessageDict )
	recipient = getUsersInDepartments( MAIL_MESSAGES[ mailMessageType ]['departments'], departmentsFilesPaths )
	sendMail( sender, recipient, message, subject, ip, port )


