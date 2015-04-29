import maya.mel as mm
import maya.cmds as mc
import os

import pipe.manager.managerUI as manUI
reload( manUI )
import pipe.settings.settings as sti
reload( sti )

"""
#reload menu
import install.pipelMenu as pM
reload ( pM)
"""
gMainWindow = mm.eval( "$temp= $gMainWindow" )
PYFILEDIR = os.path.dirname( os.path.abspath( __file__ ) )
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
mc.menuItem( l = 'Cache Manager', c = "import pipe.cacheManager.cacheManager as chM;reload( chM );chM.main()" )
mc.menuItem( l = 'Asset Exporter', c = "import modeling.exporter.exporterUI as exUI; reload(exUI); exUI.main()" )
mc.menuItem( l = 'To Do List', c = "import general.toDoList.toDoList as todoUi; reload(todoUi); todoUi.main()" )
mc.setParent('..', menu = True )

#TOOLS
mc.menuItem( l = 'General', sm = True, to = True )
mc.menuItem( l = 'File Manager', c = "import pipe.mayaFile.mayaFilePropertiesUI as mflProp;reload(mflProp);mflProp.main()" )
mc.menuItem( l = 'Save', c = "import pipe.mayaFile.mayaFile as mfl;reload(mfl);curFile = mfl.currentFile();curFile.newVersion();curFile.save()" )
mc.menuItem( l = 'Curve Scatter', c = "import general.curveScatter.curveScatterUi as crvScatterUi;reload( crvScatterUi );crvScatterUi.main()" )
mc.menuItem( l = 'Multi-Attribute', c = "import general.multiAttribute.multiAttributeUi as maUI; reload( maUI ); maUI.main()" )
mc.menuItem( l = 'Select Duplicated Names', c = "import general.utils.utils as gutils;reload( gutils );gutils.selectDuplicatedNamesNodes()" )
mc.menuItem( l = 'Rename Selection', c = "import general.renamer.renamer as rn;reload( rn );rn.renameSelection()" )
mc.menuItem( l = 'Rename Similar', c = "import general.renamer.renamer as rn;reload( rn );rn.renameSimilarObjects()" )
mc.setParent('..', menu = True )

#MODELING
mc.menuItem( l = 'Modeling', sm = True, to = True )
mc.menuItem( l = 'Modeling Checker', c = "import modeling.check.check as chk; reload(chk); chk.main();" )
mc.menuItem( l = 'Mirror Selected Curve', c = "import modeling.curve.mirrorCurve.mirrorCurve as mCrv; reload( mCrv );mCrv.main();" )
mc.menuItem( l = 'Spider Web Creator', c = "import modeling.spiderWebCreator.spiderWebCreatorUi as spw; reload( spw ); spw.main();" )
mc.setParent('..', menu = True )

#ANIMATION
mc.menuItem( l = 'Animation', sm = True, to = True )
mc.menuItem( l = 'Playblast', c = "import animation.playblast.playblastUi as plb;reload(plb); plb.main();" )
mc.menuItem( l = 'Pose Man', c = 'import maya.mel as mm;mm.eval( \'source "'+PYFILEDIR.replace( '\\', '/' ).replace( 'install','animation/poseMan' ) +'/poseMan.mel";poseMan;\')' )
mc.menuItem( l = 'Pose Nach', c = 'import animation.poseMan.poseManUi as posUi;reload( posUi );posUi.main()' )
mc.setParent('..', menu = True )

#HAIR
mc.menuItem( l = 'Hair', sm = True, to = True )
mc.menuItem( l = 'Hair System Creator', c = "import hair.hairSystem.hairUi as hru;reload( hru );hru.main();" )
mc.setParent('..', menu = True )


#SHADING
mc.menuItem( l = 'Shading', sm = True, to = True )
mc.menuItem( l = 'Texture Manager', c = "import shading.textureManager.textureManagerUi as tmu;reload(tmu);tmu.main()" )
mc.menuItem( l = 'Gamma For Selection', c = "import shading.utils.utils as shu;reload(shu);shu.createGammaForSelectedNodes()" )
mc.setParent('..', menu = True )

#RIGGING
mc.menuItem( l = 'Rigging', sm = True, to = True )
mc.menuItem( l = 'BlendShapes Tool', c = "import rigging.blendshape.blendshapesUi as bld;reload( bld );bld.main()" )
mc.menuItem( l = 'Curved-Base Tool', c = "import rigging.curveBased.curveBasedUi as crvBaseUI;reload( crvBaseUI );crvBaseUI.main()" )
mc.menuItem( l = 'Wrap To Joints', c = "import rigging.utils.wrapToJoints.nmpWrapToJoints as wrpToJ;wrpToJ.nmpWrapToJoints()" )
mc.menuItem( l = 'Copy Soft Weights To Joint', c = "import rigging.utils.SoftModCluster.SoftModCluster as sfm;reload(sfm);sfm.copyWeightsToJointFromSelection();" )
mc.menuItem( l = 'Create Controls For Selection', c = "import rigging.utils.createControls.createControlsUi as ctlsUi;reload( ctlsUi );ctlsUi.main();" )
mc.menuItem( l = 'TF Smooth Skin', c = "import rigging.utils.tf_smoothSkinWeight as tf_smoothSkinWeight;tf_smoothSkinWeight.paint()" )
mc.menuItem( l = 'BBoxCurve For Selection', c = "import modeling.bBoxToCurve.bBoxToCurve as bbox;reload( bbox );bbox.BBoxToSel();" )
mc.menuItem( l = 'Rivet On Mesh', c = "import rigging.stickyControl.stickyControl as stk;reload( stk );stk.createRivetOnMesh( name = 'boton' );" )
mc.menuItem( l = 'Face Rig', c = "import rigging.face.faceUi as fcu;reload( fcu );fcu.main();" )
mc.menuItem( l = 'Eyelids Rig', c = "import rigging.eyelids.eyelidsUi as eyeLU; reload( eyeLU); eyeLU.main();" )
mc.menuItem( l = 'Transfer Skin Weights', c = "import rigging.utils.transferSkinWeights.transferSkinWeights as tfw;reload(tfw);tfw.main();" )
mc.menuItem( l = 'Add Selected Joints To Skin', c = "import rigging.utils.utils as rut;reload(rut);rut.addSelectedJointsToSelectedMesh();" )
mc.setParent('..', menu = True )

#LIGHTING
mc.menuItem( l = 'Lighting/Render', sm = True, to = True )
mc.menuItem( l = 'Light Rig', c = "import render.lightRig.lightRig as ltRig;reload( ltRig );ltRig.main()" )
mc.menuItem( l = 'Lighter Helper', c = "import render.lighterHelper.lighterHelperUI as litHelpUI; reload( litHelpUI ); litHelpUI.main()" )
mc.menuItem( l = 'Render Manager', c = "import render.renderManager.renderManager as rm;reload(rm);rm.main()" )
mc.menuItem( l = 'Mask AOV Create', c = 'import maya.mel as mm;mm.eval( \'source "'+PYFILEDIR.replace( '\\', '/' ).replace( 'install','render/mask' ) +'/AOVsArnoldMasker_1.0v.mel";\')' )
mc.setParent('..', menu = True )

#REFERENCES
mc.menuItem( l = 'References', sm = True, to = True )
mc.menuItem( l = 'Reload Selected', c = "import general.reference.reference as rf;reload(rf);rf.reloadSelected()" )
mc.menuItem( l = 'Unload Selected', c = "import general.reference.reference as rf;reload(rf);rf.unloadSelected()" )
mc.menuItem( l = 'Remove Selected', c = "import general.reference.reference as rf;reload(rf);rf.removeSelected()" )
mc.menuItem( l = 'Duplicate Selected', c = "import general.reference.reference as rf;reload(rf);rf.dupReferenceForSelectedObjects()" )
mc.menuItem( l = 'Make Selected For Shot', c = "import pipe.utils.utils as pipUtils;reload( pipUtils );pipUtils.makeAssetForShot()" )
mc.setParent('..', menu = True )

#RELOAD
mc.menuItem( divider = True )
mc.menuItem( l = 'Reload Menu', c = "import install.pipelMenu as pM;reload ( pM )" )
mc.setParent('..', menu = True )


#HELP
mc.menuItem( divider = True )
mc.menuItem( l = 'Help', c = 'import os;os.system(\'start ' + PYFILEDIR.replace( '\\', '/' ).replace( 'install','docs' ) + '/index.htm\')' ) 
mc.setParent('..', menu = True )

sett = sti.Settings()
gen = sett.General
if gen:
	if gen.has_key( 'autoload' ):
		autoLoad = gen[ "autoload" ]
		if autoLoad == 'True': 
			manUI.main()
if not sett.exists:
	manUI.main()





