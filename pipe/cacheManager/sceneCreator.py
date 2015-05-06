import pipe.shot.shot as sh
import pipe.project.project as prj
import pipe.sequence.sequence as sq
import pipe.asset.asset as ass
reload(ass )
try:
	import maya.cmds as mc
except:
	pass
import pipe.cacheFile.cacheFile as cfl
reload( cfl )
import general.mayaNode.mayaNode as mn
reload(mn)
import pipe.mayaFile.mayaFile as mfl


def createLitScene( projectName, sequenceName, shotName, serverPath = 'P:/' ):
	mc.refresh( su = True )
	proje = prj.Project( projectName, serverPath )
	sho = sh.Shot( shotName, sq.Sequence( sequenceName, proje ) )
	#load Cam
	shtCam = sho.poolCam
	shtCam.reference()
	#load Caches
	caches = sho.caches
	for s in caches.keys():
		for n in caches[s]:
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
	mc.playbackOptions( min = tim[ 'min' ],ast = tim[ 'ast' ], max = tim[ 'max' ], aet = tim[ 'aet' ] )
	mc.refresh( su = False )

def exportAllFromAnim( projectName, sequenceName, shotName, serverPath = 'P:/' ):
	"""docstring for exportAllFromAnim"""
	proje = prj.Project( projectName, serverPath )
	sho = sh.Shot( shotName, sq.Sequence( sequenceName, proje ) )
	#Export Camera
	cam = getCamera()
	if not len( cam ) == 1:
		print 'There are more than one camera or no camera to export... so I cant know what camera to export, delete other cameras or create one to export'
	else:
		exportCamera( cam, sho )
	#Export Rigs
	rigs = getRigsInScene()
	if rigs:
		exportCaches( rigs, sho )
	#Export Sets
	sets = getSetsInScene()
	if sets:
		exportSets( sets, sho )

def getSetsInScene():
	"""docstring for getSetsInScene"""
	mc.namespace( set=':' )
	refs = mc.namespaceInfo( lon = True )
	setsRefs = []
	for r in refs:
		if '_shading' in r.lower() or '_final' in r.lower():
			if not '_rig' in r.lower():
				setsRefs.append( r )
	return setsRefs

def getRigsInScene():
	"""docstring for getRigsInScene"""
	mc.namespace( set=':' )
	refs = mc.namespaceInfo( lon = True )
	rigRefs = []
	for r in refs:
		if '_rig' in r.lower():
			if not '_model' in r.lower() or not '_shading' in r.lower() or not '_final' in r.lower():
				rigRefs.append( r )
	return rigRefs

def exportCaches( rigs, sho ):
	"""docstring for exportCaches"""
	baseDir = sho.animCachesPath
	exportedAsset = []
	steps = 1.0
	nods = []
	for n in rigs:
		no = mc.ls( n + ':*', s = True, dag = True, ni = True )
		if no:
			nods.append( no[0] )
	nods = mn.Nodes( nods )
	for n in nods:
		baseName = n.name.split( ':' )[0]
		if baseName in exportedAsset:
			continue
		a = ass.getAssetFromNode( n, sho.project )
		cacFile = cfl.CacheFile( baseDir + '/' + baseName + '.abc', [n] )
		cacFile.exportAsset( a, False, False, steps )
		exportedAsset.append( baseName )


def exportCamera( cam, sho ):
	"""docstring for exportCamera"""
	cam[0]()
	mc.file( sho.poolCam.path, force = True, options = "v=0;", typ = "mayaAscii", pr = True, es = True )
	cacheFile = cfl.CacheFile( sho.poolCam.path.replace( '.ma', '.abc' ), cam )
	cacheFile.export()

def exportSets( sets, sho ):
	"""docstring for exportSets"""
	nods = []
	for s in sets:
		nods.extend( mc.ls( s + ':*', s = True, dag = True, ni = True ) )
	nods = mn.Nodes( nods )
	nods.select()
	maFile = mfl.mayaFile( sho.setsPath+ 'set.ma' )
	maFile.newVersion()
	mc.file( str( maFile.path ), preserveReferences=True, type='mayaAscii', exportSelected =True, prompt=True, force=True )

def getCamera():
	cams = mn.ls( typ = 'camera' )
	finalCam = []
	camsToIgnore = [
	'bottomShape',
	'frontShape',
	'leftShape',
	'perspShape',
	'rightShape',
	'sideShape',
	'topShape'
	]
	for c in cams:
		if c.isReference:
			continue
		if any( ca in c.name for ca in camsToIgnore ):
			continue
		finalCam.append( c )
	return finalCam
	    
