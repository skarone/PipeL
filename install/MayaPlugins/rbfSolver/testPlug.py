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

