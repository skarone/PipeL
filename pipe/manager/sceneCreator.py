import pipe.shot.shot as sh
import pipe.project.project as prj
import pipe.sequence.sequence as sq
import pipe.asset.asset as ass
import maya.cmds as mc

def createLitScene( projectName, sequenceName, shotName, serverPath = 'P:/' ):
	proje = prj.Project( 'Domestos_Bathroom_Blitz', serverPath )
	sho = sh.Shot( 's005_T05', sq.Sequence( 'Btahroom_Blitz', proje ) )
	#load Cam
	shtCam = sho.poolCam
	shtCam.reference()
	#load Caches
	caches = sho.caches
	for s in caches.keys():
		for n in caches[s]:
		print n.name
		if '_' in n.name:
			n.importForAsset( ass.Asset( n.name[:n.name.rindex( '_' )], proje ), 1, n.name, True, False, None )
		else:
			n.imp()
	#load set
	for n in sho.sets:
		n.reference()
	#copy Time Settings
	tim = sho.animPath.time
	mc.currentUnit( time=tim['tim'], linear = tim['lin'], angle = tim[ 'angle' ] )
	mc.playbackOptions( min = tim[ 'min' ],
						ast = tim[ 'ast' ], 
						max = tim[ 'max' ], 
						aet = tim[ 'aet' ] )
	    
