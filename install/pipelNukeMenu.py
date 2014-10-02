import nuke
import nukescripts
import nuk.general.SearchReplacePanel.SearchReplacePanel as SearchReplacePanel
import nuk.general.read
menubar = nuke.menu( "Nuke" )
m = menubar.addMenu( 'PipeL' )
m.addCommand( 'Project Manager', 'import pipe.manager.managerUI as manUI; reload( manUI ); manUI.main();' )
m.addCommand( 'Load All Layers', 'import nuk.general.readAllLayers.readAllLayers as readUI; reload( readUI ); readUI.main();' )
m.addCommand( 'Turn ON|OFF Heavy Nodes', 'import nuk.utils.utils as ut;reload(ut);ut.turnHeavyNodesOnOff();' )
m.addSeparator()
m.addCommand( 'Submit To Deadline', 'import nuk.deadline.SubmitToDeadline as deadline; deadline.main();') 
m.addSeparator()
m.addCommand( 'Reload Menu', 'import install.pipelNukeMenu as pNM; reload( pNM );' )

def addSRPanel():
	'''Run the panel script and add it as a tab into the pane it is called from'''
	myPanel = SearchReplacePanel.SearchReplacePanel()
	return myPanel.addToPane()
 
#THIS LINE WILL ADD THE NEW ENTRY TO THE PANE MENU
nuke.menu('Pane').addCommand('SearchReplace', addSRPanel)

# CREATE A READ NODE AND OPEN THE "DB" TAB
def customRead():
	n = nuke.createNode( 'Read' )
	n['PipeL'].setFlag( 0 )
	return n

nuke.menu( 'Nodes' ).addCommand( 'Image/Read', customRead, 'r' )

nuke.addOnUserCreate( nuk.general.read.createVersionKnobs, nodeClass='Read' )
nuke.addKnobChanged( nuk.general.read.updateVersionKnob, nodeClass='Read' )

nuke.addOnScriptLoad( nuk.general.read.checkVersions )
nuke.addOnScriptSave( nuk.general.read.checkVersions )
"""
import nuk.general.read
import nuke
nuke.removeOnScriptLoad(nuk.general.read.checkVersions)
nuke.removeOnScriptSave(nuk.general.read.checkVersions)
"""

def mergeColor():
	n = nuke.thisNode()
	k = nuke.thisKnob()
	if k.name() == "mix":
		v = k.value()
		green = v
		red = 1 - int(v)
		r = red
		g = green
		b = 0
		hexColour = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,1),16)
		n["tile_color"].setValue(hexColour)

nuke.addKnobChanged(mergeColor, nodeClass="Merge2")
 
#THIS LINE WILL REGISTER THE PANEL SO IT CAN BE RESTORED WITH LAYOUTS
nukescripts.registerPanel('com.ohufx.SearchReplace', addSRPanel)
