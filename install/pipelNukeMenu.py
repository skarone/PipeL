import nuke
import nukescripts
import nuk.general.SearchReplacePanel.SearchReplacePanel as SearchReplacePanel
menubar = nuke.menu( "Nuke" )
m = menubar.addMenu( 'PipeL' )
m.addCommand( 'Project Manager', 'import pipe.manager.managerUI as manUI; reload( manUI ); manUI.main();' )
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
 
#THIS LINE WILL REGISTER THE PANEL SO IT CAN BE RESTORED WITH LAYOUTS
nukescripts.registerPanel('com.ohufx.SearchReplace', addSRPanel)
