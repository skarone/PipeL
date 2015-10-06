import nuke
import pipe.project.project as prj
import pipe.sequence.sequence as sq
import pipe.shot.shot as sh
import pipe.sequenceFile.sequenceFile as sqFil
import pipe.settings.settings as sti
reload( sti )

def getOutDatedReads():
	"""docstring for getOutDatedReads"""
	fileKnobNodes = [i for i in nuke.allNodes() if i.Class() == "Read"]
	outDatedReads = ''
	settings = sti.Settings()
	gen = settings.General
	if gen:
		basePath = gen[ "basepath" ]
		if basePath:
			if basePath.endswith( '\\' ):
				basePath = basePath[:-1]
			prj.BASE_PATH = basePath.replace( '\\', '/' )
		renderPath = gen[ "renderpath" ]
	for node in fileKnobNodes:
		if node.knob('_version'):
			print 'shotSel!', node[ 'shotSel' ].value()
			if not node[ 'shotSel' ].value() == '0' or not node[ 'shotSel' ].value() == '' or not node[ 'shotSel' ].value() == 0:
				currentVersion = node[ '_version' ].value()
				node[ '_version' ].setValues( sh.Shot( node[ 'shotSel' ].value(),sq.Sequence( node[ 'seqSel' ].value(), prj.Project( node[ 'projectSel' ].value() ))).renderedLayerVersions( renderPath, node[ 'layerSel' ].value() ) )
				node[ '_version' ].setValue( currentVersion )
				vers = sorted( node[ '_version' ].values() )
				if vers:
					if not vers[-1] ==  currentVersion:
						outDatedReads += node['name'].value() + ', '
	if outDatedReads:
		nuke.message('The following READS are outdated!\n' + outDatedReads )
	else:
		nuke.message('Everything is updated! :)'  )

