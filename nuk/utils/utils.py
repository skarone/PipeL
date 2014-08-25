import nuke

def turnHeavyNodesOnOff():
	"""Turn off and on all heavy nodes to compute"""
	nodesTypes = [ 'Median', 
					'Defocus',
					'Grain2',
					'VectorBlur',
					'ZBlur',
					'ZDefocus2',
					'OFXcom.frischluft.openfx.depthoffield_v1',
					'OFXcom.frischluft.openfx.outoffocus_v1',
					'OFXuk.co.thefoundry.furnace.f_regrain_v403'
				]
	nodes = []
	for nT  in nodesTypes:
		nodes.extend( nuke.allNodes( nT ) )
	if not nodes:
		return
	n = nodes[0]
	val = n.knob( 'disable' ).value()

	for a in nodes:
			a.knob( 'disable' ).setValue( not val )
