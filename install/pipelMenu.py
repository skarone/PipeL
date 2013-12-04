import maya.mel as mm
import maya.cmds as mc

"""
#reload menu
import install.pipelMenu as pM
reload ( pM)
"""
gMainWindow = mm.eval( "$temp= $gMainWindow" )

mainMenu = 'ccPipelMenu'
if( mc.menu( mainMenu, q = True, exists = True ) ):
	mc.menu( mainMenu, e = True, dai = True )
else:
	mc.setParent( gMainWindow )
	mc.menu( mainMenu, l = 'PipeL', p = gMainWindow, to = True )

mc.setParent(mainMenu, menu = True )

#PROJECT
mc.menuItem( l = 'Project', sm = True, to = True )
mc.menuItem( l = 'Manager', c = "import pipe.manager.managerUI as manUI; reload( manUI ); manUI.main()" )
mc.menuItem( l = 'Asset Exporter', c = "import modeling.exporter.exporterUI as exUI; reload(exUI); exUI.main()" )
mc.setParent('..', menu = True )

#TOOLS
mc.menuItem( l = 'Tools', sm = True, to = True )
mc.menuItem( l = 'Multi-Attribute', c = "import general.multiAttribute.multiAttributeUi as maUI; reload( maUI ); maUI.main()" )
mc.menuItem( l = 'Rename Selection', c = "import general.renamer.renamer as rn;reload( rn );rn.renameSelection()" )
mc.menuItem( l = 'Rename Similar', c = "import general.renamer.renamer as rn;reload( rn );rn.renameSimilarObjects()" )
mc.setParent('..', menu = True )


#LIGHTING
mc.menuItem( l = 'Lighting', sm = True, to = True )
mc.menuItem( l = 'Lighter Helper', c = "import render.lighterHelper.lighterHelperUI as litHelpUI; reload( litHelpUI ); litHelpUI.main()" )
mc.setParent('..', menu = True )

#REFERENCES
mc.menuItem( l = 'References', sm = True, to = True )
mc.menuItem( l = 'Reload Selected', c = "import general.reference.reference as rf;rf.reloadSelected()" )
mc.menuItem( l = 'Unload Selected', c = "import general.reference.reference as rf;rf.unloadSelected()" )
mc.setParent('..', menu = True )

#RELOAD
mc.menuItem( divider = True )
mc.menuItem( l = 'Reload Menu', c = "import install.pipelMenu as pM;reload ( pM )" )
mc.setParent('..', menu = True )



