import pymel.core as pm
import general.mayaNode.mayaNode as mn
import maya.cmds as mc
import maya.OpenMaya as om
import rigging.utils.utils as rut
reload(rut)

def createClusterFromSelectedSoft( shape = None ):
	softMo = mn.ls( sl = True, dag = True, typ = 'softModHandle' )
	if softMo:
		for s in softMo:
			softMoNode = SoftModCluster( s.name, shape )
			weights = softMoNode.weights
			mc.select( weights.keys() )
			clusBase = mc.cluster( n = softMoNode.name + '_CLU', envelope = 1 )
			clus = mn.Node( clusBase[1] )
			clus.a.scalePivot.v = softMoNode.a.origin.v[0]
			clus.a.rotatePivot.v = softMoNode.a.origin.v[0]
			clus.shape.a.origin.v = softMoNode.a.origin.v[0]
			for s in weights.keys():
				mc.select( s )
				mc.percent( clusBase[0], v=weights[s] )

def copyWeightsToJointFromSelection():
	"""select the soft, then de joint and then the mesh and run me :)"""
	sel = mc.ls( sl = True )
	if not len( sel ) == 3:
		print 'select the soft, then de joint and then the mesh and run me :)'
		return
	skins = rut.getSkinFromGeo( sel[2] )
	copyWeightsToJoint( sel[0], skins[0], sel[1], sel[2] )

def copyWeightsToJoint( softM, skin, join, mesh, finalMesh = '' ):
	"""copy the weights of the soft mod node to de joint"""
	softMoNode = SoftModCluster( softM, mesh )
	weights = softMoNode.weights
	for s in weights.keys():
		sfinal = s
		if finalMesh != '':
			sfinal = finalMesh +  s[s.rfind( '.' ):]
		mc.skinPercent( skin, sfinal, transformValue=[( join, weights[s])])

def createSoftModForOnSelected( shape ):
	"""create softMod in the position of the selected objects"""
	sel = mn.ls( sl = True )
	for s in sel:
		softMoNode = SoftModCluster( s.name, shape )
		softMoNode.create( s.worldPosition )


class SoftModCluster(mn.Node):
	def __init__( self, name, shape ):
		super(SoftModCluster,self).__init__( name )
		self.SoftMod_Handles = None
		self.SoftMod = None
		self.Pos = None
		self.Vtxs = None
		self.Radius = None
		self.Cluster = None
		self._shape = shape

	@property
	def shape(self):
		"""return the shape for the softmod"""
		return self._shape
	
	def create( self, position = [], vertexToRemove = [] ):
		"""create a Soft Mod with the name for the specific shape,
		position = use it to create a softMod in a specific location
		"""
		mc.select( self.shape )
		print self.name
		nodes  = mc.softMod( n = self.name, fc = position, falloffRadius = 15.165877 ,falloffMode = 0 , falloffBasedOnX = 1 ,falloffBasedOnY = 1 ,falloffBasedOnZ = 1 ,falloffAroundSelection = 0 ,falloffMasking = 1 )
		softM  = mn.Node( nodes[0] )
		handle  = mn.Node( nodes[1] )
		#nodes  = mc.softMod( n = self.name, fc = position, falloffRadius = 15.165877 ,falloffMode = 0 , curveValue = 0 ,curvePoint = 1 ,curveInterpolation = 2 ,falloffBasedOnX = 1 ,falloffBasedOnY = 1 ,falloffBasedOnZ = 1 ,falloffAroundSelection = 0 ,falloffMasking = 1 )
		if vertexToRemove:
			mc.sets( vertexToRemove, rm = softM.name + 'Set' )
		handle.a.falloffMode.add( at = "enum", en = "Volume:Surface:", keyable = True )
		softM.a.falloffMode << handle.a.falloffMode
		handle.a.falloffRadius.add( min = 0, keyable = True, dv = 5 )
		softM.a.falloffRadius << handle.a.falloffRadius
		return handle
		

	@property
	def shape(self):
		"""return the shape"""
		return self._shape

	def add_fallOff_attr(self):
		sels = pm.ls(sl=1,l=1)
		if sels:
			for sel in sels:
				try :
					pm.PyNode(sel.falloffRadius)
				except :
					pm.addAttr(sel,ln='falloffRadius',at='double')
					sel.falloffRadius.set(keyable=True)
				sel.falloffRadius.set(1)
				
				try :
					pm.PyNode(sel.falloffMode)
				except :
					pm.addAttr(sel,ln='falloffMode',at='enum',en='volume:surface')
					sel.falloffMode.set(keyable=True)
				sel.falloffMode.set('volume')
		
	def softMod_to_cluster(self):
		#
		sel = pm.ls(sl=1)
		softMod_handle_shapes = pm.ls(sl=1,dag=1,lf=1,type='softModHandle')
		#
		l = pm.spaceLocator()
		pm.select(sel[0],tgl=1)
		pm.mel.eval('align -atl -x Mid -y Mid -z Mid')
		
		pm.select(l,r=1)
		self.Pos = pm.xform(q=1,ws=1,t=1)
		
		if softMod_handle_shapes:
			for softMod_handle_shape in softMod_handle_shapes:
				print softMod_handle_shape
				softMod_handle = softMod_handle_shape.getParent()
				softMods = softMod_handle_shape.softModTransforms.connections(p=0,s=1)
				if softMods:
					softMod = softMods[0]
					if softMod :
						deform_sets = softMod.message.connections(p=0,s=1)
						self.Radius = softMod.falloffRadius.get()
						#pvt = softMod.falloffCenter.get()
						print deform_sets
						if deform_sets:
							deform_set = deform_sets[0]
							geometrys = deform_set.memberWireframeColor.connections(p=0,s=1)
							print geometrys
							pm.select(geometrys[0],r=1)
							pm.polySelectConstraint(m=3,t=1,d=1,db=(0,self.Radius),dp=self.Pos)
							vtxs = pm.ls(sl=1,fl=1)
							pm.polySelectConstraint(m=0)
							
							pm.mel.eval('newCluster \" -envelope 1\"')
							
							cluster_handle = pm.ls(sl=1)[0]
							cluster_shape = pm.ls(sl=1,dag=1,lf=1)[0]
							
							# Get cluster
							self.Cluster = cluster = cluster_shape.clusterTransforms.connections(p=0,d=1)[0]
							print 'cluster:',cluster
							
							cluster_shape.originX.set(0)
							cluster_shape.originY.set(0)
							cluster_shape.originZ.set(0)

							pm.select(cluster_handle,r=1)
							pm.move(self.Pos,r=1)
							
							pm.move(cluster_handle.scalePivot,self.Pos)
							pm.move(cluster_handle.rotatePivot,self.Pos)
							
							cluster_handle.tx.set(0)
							cluster_handle.ty.set(0)
							cluster_handle.tz.set(0)
							
							cluster_shape.originX.set(self.Pos[0])
							cluster_shape.originY.set(self.Pos[1])
							cluster_shape.originZ.set(self.Pos[2])
							
							pm.move(cluster_handle.scalePivot,self.Pos)
							pm.move(cluster_handle.rotatePivot,self.Pos)
							
							# set vtx weight
							
							#select $vtxs;
							#sets -add $deformSet; 
							pm.select(vtxs,r=1)
							pm.sets(deform_set,add=1)
							
							#$posSoftMod=`xform -q -ws -piv $softModHandle`;
							#move -r -ws 1 0 0 $softModHandle;
							print 'softMod_handle:',softMod_handle
							pos_softMod = pm.xform(softMod_handle,q=1,ws=1,piv=1)
							pm.move(1,0,0,softMod_handle,r=1,ws=1)
							print '\na'
							for vtx in vtxs:
								#setAttr ($softMod+".envelope") 0;
								#$posA=`xform -q -ws -t $vtxs[$i]`;
								#setAttr ($softMod+".envelope") 1;
								softMod.envelope.set(0)
								posA = pm.xform(vtx,q=1,ws=1,t=1)
								softMod.envelope.set(1)
								
								xRadius = softMod.falloffRadius.get()
								yRadius = softMod.falloffRadius.get()
								
								posBX=posBY=pm.xform(vtx,q=1,ws=1,t=1)
								#$vecX=$posA[0]-$posSoftMod[0];
								#$vecY=$posA[1]-$posSoftMod[1];
								vecX = posA[0] - pos_softMod[0]
								vecY = posA[1] - pos_softMod[1]
								
								#$magX=$posBX[0]-$posA[0];
								#$magY=$posBY[0]-$posA[0];
								magX = posBX[0] - posA[0]
								magY = posBY[0] - posA[0]
								mag = ((magX-pm.datatypes.abs(vecY*(1.0/(yRadius*2.0)))) \
									   + (magY-pm.datatypes.abs(vecX*(1.0/(xRadius*2.0)))))*0.5
								if mag < 0 :
									mag = 0
								print 'mag: ',mag
								#percent -v $mag $cluster $vtxs[$i]
								pm.select(vtx,r=1)
								pm.percent(cluster,v=mag)
							
							print softMod_handle
							pm.move(-1,0,0,softMod_handle,r=1,ws=1)
							
	def control_to_softMod(self):
		sels = pm.ls(sl=1)
		if len(sels) == 2 :
			control = sels[0]
			geometry = sels[1]
			falloff_radius = control.falloffRadius.get()
			falloff_mode = control.falloffMode.get()
			
			pos = t = pm.xform(control,q=1,ws=1,t=1)
			r = pm.xform(control,q=1,ws=1,ro=1)
			s = pm.xform(control,q=1,r=1,s=1)
			
			pm.select(geometry,r=1)
			#softMod -falloffMode 1 -falloffAroundSelection 0
			(softMod,softMod_handle) = pm.softMod(falloffMode=1, falloffAroundSelection=0)
			#rename $tempString[0] ("convertedSoftMod_"+$sel[0])
			pm.rename(softMod, ( 'convertedSoftMod_'+control.name() ) )
			pm.rename(softMod_handle, ( 'convertedSoftModHandle_'+control.name() ) )
			
			softMod.falloffRadius.set( falloff_radius )
			softMod.falloffMode.set( falloff_mode )
			#setAttr -type float3 ($softModHandle+"Shape.origin") ($pos[0]) $pos[1] $pos[2];
			softMod_handle.getShape().origin.set(pos)
			#setAttr ($softMod+".falloffCenter") ($pos[0]) $pos[1] $pos[2];
			softMod.falloffCenter.set(pos)
			
			#xform -piv ($pos[0]) $pos[1] $pos[2] $softModHandle;
			pm.xform(softMod_handle,piv=pos)
			#xform -ws -t ($t[0]-$pos[0]) ($t[1]-$pos[1]) ($t[2]-$pos[2]) -ro $r[0] $r[1] $r[2] -s $s[0] $s[1] $s[2] $softModHandle;
			pm.xform(softMod_handle,ws=1,t=((t[0]-pos[0]),(t[1]-pos[1]),(t[2]-pos[2])),ro=r,s=s)
			
			pm.select(softMod_handle)
			
		else:
			pm.warning('control_to_softMod:please select one control and one geometry first')

	@property
	def weights(self):
		"""return the weights of the verteces in the soft cluster"""
		selfParent = self.parent
		softPos = self.a.origin.v
		softModDeformerNode = self.a.softModTransforms.output
		if not softModDeformerNode:
			mc.error( 'THERE IS NO SOFT MOD DEFORMER CONNECTED TO THIS SOFTMOD HANDLE' )
			return
		if not self.shape:
			softModDeformerNode = softModDeformerNode[0].node
			mesh = softModDeformerNode.a.outputGeometry.output
			if not mesh:
				mc.error( 'THERE IS NO MESH CONNECTED TO THIS SOFT MOD DEFORMER' )
				return
			mesh = mesh[0].node
		else:
			mesh = mn.Node( self.shape )
		vtxs = mc.ls( mesh.name + '.vtx[*]', fl = True )
		weights = {}
		mc.refresh( su = True )
		#NEW STYLE
		selfParent.a.t.v = [0,1,0]
		finalPos = [ mc.xform(vtx,q=1,ws=1,t=1) for vtx in vtxs ]
		selfParent.a.t.v = [0,0,0]
		basePos = [ mc.xform(vtx,q=1,ws=1,t=1) for vtx in vtxs ]
		difPos = [ om.MVector( finalPos[p][0],finalPos[p][1],finalPos[p][2] ) - om.MVector( basePos[p][0],basePos[p][1],basePos[p][2] )  for p in range( len( basePos ) ) ]
		weights = {}
		for i,d in enumerate( difPos ):
			w = abs( d.length() )
			if w == 0:
				continue
			weights[ vtxs[i] ] = w
		mc.refresh( su = False )
		return weights

		
		
#    def set_cluster_weight_mel(self):
#        n1 = str( pm.PyNode(self.SoftMod).name() )
#        n2 = str( pm.PyNode(self.Cluster).name() )
#        print self.Vtxs
#        
#        cmd = 'softModCluster (\"' + n1 + '\",\"' + n2 + '\",{'  
#        i = 0
#        for v in self.Vtxs:
#            if i ==0 : 
#                cmd += '\"' + v.name() + '\"'
#            else:
#                cmd += ',\"' + v.name() + '\"'
#            i += 1
#        cmd += '})'
#        print cmd
#        pm.mel.eval( cmd )
		
def main():
	a = SoftModCluster()
	a.softMod_to_cluster()
	#a.add_fallOff_attr()
	#a.control_to_softMod()

if __name__ == '__main__' :
	main()

