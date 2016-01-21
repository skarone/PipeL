import sys
import os
import maya.standalone as std
std.initialize(name='python')
import maya.cmds as mc
import general.mayaNode.mayaNode as mn
sys.path.append('C:/solidangle/mtoadeploy/' + mc.about( v = True ) + '/scripts')

def createPreview( shaderPath ):
	"""open shader template, import and assing shader and render preview"""
	templatePath = os.path.dirname(os.path.abspath(__file__)) + '/shaderTemplate.ma'
	mc.file( templatePath, force=True, open=True )
	mc.file( shaderPath, i = True, type = "mayaAscii" ,ignoreVersion = True, mergeNamespacesOnClash = False ,rpr = "rojo", options = "v=0;" ,pr = True )
	shaderName = os.path.basename(shaderPath).split( '.' )[0]
	shaderName = mn.Node(shaderName)
	mc.sets( 'base_square_MSKShape', edit=True, forceElement=shaderName.shader.name )
	mc.sets( 'outer_sphere_MSKShape', edit=True, forceElement=shaderName.shader.name )
	de = mn.Node( 'defaultRenderGlobals' )
	de.a.imageFilePrefix.v = os.path.dirname( shaderPath ) +'/'+ shaderName.name
	mc.file( rename = shaderPath.replace( '.ma', 'Preview.ma' ) )
	print shaderPath
	mc.file(save=True, force=True, type = "mayaAscii")

shaderPath = sys.argv[1]
mc.loadPlugin( 'mtoa' )
createPreview( shaderPath )

