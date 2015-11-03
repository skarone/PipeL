import maya.cmds as mc
#create ropes using ropeGenerator Plugin!

def createRopesForSelectedCurves():
    for n in mc.ls( sl = True, dag = True,ni = True, typ = "nurbsCurve" ):
        ropeGen = mc.createNode( "ropeGenerator" )
        mc.setAttr( ropeGen + '.tapper[0].tapper_FloatValue', 1 )
        mc.setAttr( ropeGen + '.twistRamp[0].twistRamp_FloatValue', 1 )
        mc.connectAttr( n + '.worldSpace[0]', ropeGen + '.inCurve' )
        mesh = mc.createNode( "mesh" )
        mc.connectAttr( ropeGen + '.outMesh', mesh + '.inMesh' )
        mc.sets( e = True, forceElement = "initialShadingGroup" )
