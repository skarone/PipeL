import general.mayaNode.mayaNode as mn
import random as rd
import maya.cmds as mc
rbfNode = mn.createNode( 'rbfSolver' )
baseSphere = mn.Node( 'pSphere1' )
sha = baseSphere.shader.a.surfaceShader.input.node
distance = 30
samples = mn.createNode( 'transform' )
samples.name = 'samples'
samplesCount = 30
centersCount = 5
for n in range(samplesCount):
    newSphere = baseSphere.duplicate()
    newSha = sha.duplicate()
    newSphere.a.t.v = [rd.uniform( -(distance),distance ),
                        rd.uniform( -(distance),distance ),
                        rd.uniform( -(distance),distance )]
    newSha.a.outColor.v = [rd.uniform(0,1),
                            rd.uniform(0,1),
                            rd.uniform(0,1)]
    mc.select( newSphere )
    mc.hyperShade( a = newSha )
    newSphere.a.t >> rbfNode.attr( "inPos[" + str( n ) + "]" )
    newSha.a.outColorR >> rbfNode.attr( "inValues[" + str( n ) + "].inValue[0]" )
    newSha.a.outColorG >> rbfNode.attr( "inValues[" + str( n ) + "].inValue[1]" )
    newSha.a.outColorB >> rbfNode.attr( "inValues[" + str( n ) + "].inValue[2]" )
    newSphere.parent = samples

centers = mn.createNode( 'transform' )
centers.name = 'centers_grp'
for n in range(centersCount):
    newSphere = baseSphere.duplicate()
    newSha = sha.duplicate()
    newSphere.a.t.v = [rd.uniform( -(distance),distance ),
                        rd.uniform( -(distance),distance ),
                        rd.uniform( -(distance),distance )]
    newSphere.a.s.v = [2.5,2.5,2.5]
    mc.select( newSphere )
    mc.hyperShade( a = newSha )
    newSphere.parent = centers
    newSphere.a.t >> rbfNode.attr( "inCenter[" + str( n ) + "]" )
    rbfNode.attr( "outValues[" + str( n ) + "].outValue[0]" ) >> newSha.a.outColorR
    rbfNode.attr( "outValues[" + str( n ) + "].outValue[1]" ) >> newSha.a.outColorG
    rbfNode.attr( "outValues[" + str( n ) + "].outValue[2]" ) >> newSha.a.outColorB
rbfNode()


"""
#Test with sphere
import general.mayaNode.mayaNode as mn
import random as rd
import maya.cmds as mc
import maya.mel as mm
rbfNode = mn.createNode( 'rbfSolver' )
baseSphere = mn.Node( 'pSphere1' )
sha = baseSphere.shader.a.surfaceShader.input.node
distance = 60
samples = mn.createNode( 'transform' )
samples.name = 'samples'
samplesCount = 120
centersCount = 5

for n in range( samplesCount ):
    rt = mm.eval( "unit(sphrand(1))" )
    #rt = rt*15
    newSphere = baseSphere.duplicate()
    newSha = sha.duplicate()
    newSphere.a.t.v = [rt[0]*15,rt[1]*15,rt[2]*15]
    newSha.a.outColor.v = [rd.uniform(0,1),
                            rd.uniform(0,1),
                            rd.uniform(0,1)]
    mc.select( newSphere )
    mc.hyperShade( a = newSha )
    newSphere.a.t >> rbfNode.attr( "inPos[" + str( n ) + "]" )
    newSha.a.outColorR >> rbfNode.attr( "inValues[" + str( n ) + "].inValue[0]" )
    newSha.a.outColorG >> rbfNode.attr( "inValues[" + str( n ) + "].inValue[1]" )
    newSha.a.outColorB >> rbfNode.attr( "inValues[" + str( n ) + "].inValue[2]" )
    newSphere.parent = samples
mn.Node("pSphereShape2").a.outMesh >> rbfNode.a.inputMesh
print rbfNode.attr( "outValues[0].outValue[0]" ).v
mc.select( "pSphereShape2" )
for n in range(mc.polyEvaluate( v=True )):
    col = rbfNode.attr( "outValues[" + str( n )+ "].outValue" ).v
    mc.select( "pSphereShape2.vtx[" + str(n) +  "]" )
    mc.polyColorPerVertex( rgb=(col[0][0], col[0][1], col[0][2]),cdo = True )
"""

