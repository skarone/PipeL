import smtplib
import pipe.file.file as fl

# Import the email modules we'll need
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

MAIL_MESSAGES = {
	'new_cache':{
		'message':'New Cache<br>Asset: <AssetName><br>Sequence: <SequenceName><br>Shot: <ShotName><br>User: <UserName>',
		'departments':['animation', 'lighting', 'production','vfx'],
		'subject':'[CACHE] [<ProjectName>] [<SequenceName>] [<ShotName>] [<AssetName>]'},
	'new_playblast':{
		'message':'New Playblast<br>Sequence: <SequenceName><br>Shot: <ShotName><br>User: <UserName><br>File: <a href="<Path>"><Path></a>',
		'departments':['animation','production'],
		'subject':'[PLAYBLAST] [<ProjectName>] [<SequenceName>] [<ShotName>]'},
	'new_render':{
		'message':'New Render<br>Renderlayer: <RenderLayer><br>Sequence: <SequenceName><br>Shot: <ShotName><br>User: <UserName>',
		'departments':['compo', 'lighting', 'production'],
		'subject':'[RENDER] [<ProjectName>] [<SequenceName>] [<ShotName>] [<RenderLayer>]'},
	'new_asset_publish':{
		'message':'New Final Asset Published<br>Asset: <AssetName><br>User: <UserName>',
		'departments':['lighting', 'production','vfx'],
		'subject':'[ASSET] [FINAL] [<ProjectName>] [<AssetName>]'}
}

def sendMail( sender, recipient, message, subject, ip = '192.168.0.1', port= 25 ):

	html = """\
	<html>
	<head></head>
	<body>
		<p>""" + message + """
		</p>
	</body>
	</html>
	"""
	msg = MIMEText(html, 'html')
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


