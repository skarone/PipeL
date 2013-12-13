# -----------------------------------------------------------------------------------
# AUTHOR:     Tom Ferstl
#             t.ferstl@gmx.net
#
# INSTALL:    copy script to your maya scripts directory (i.e. C:\Users\xx\Documents\maya\2011\scripts )
#
# USAGE:      select a skinned mesh and execute the following python commands (without # and whitespace):
#             import tf_smoothSkinWeight
#             tf_smoothSkinWeight.paint()
# -----------------------------------------------------------------------------------

import maya.cmds as mc
import maya.mel as mm
import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma

# -----------------------------------------------------------------------------------
# define mel procedures for the scripted brush
# -----------------------------------------------------------------------------------
def initPaint():
  cmd = '''
    global string $tf_skinSmoothPatin_selection[];

    global proc tf_smoothBrush( string $context )
    {
      artUserPaintCtx -e -ic "tf_init_smoothBrush" -svc "tf_set_smoothBrushValue"
      -fc "" -gvc "" -gsc "" -gac "" -tcc "" $context;
    }

    global proc tf_init_smoothBrush( string $name )
    {
        global string $tf_skinSmoothPatin_selection[];
        
        $tf_skinSmoothPatin_selection = {};
        string $sel[] = `ls -sl -fl`;
        string $obj[] = `ls -sl -o`;
        $objName = $obj[0];
        
        int $i = 0;
        for($vtx in $sel)
        {
            string $buffer[];
            int $number = `tokenize $vtx ".[]" $buffer`;
            $tf_skinSmoothPatin_selection[$i] = $buffer[2];
            $i++;
            if ($number != 0)
                $objName = $buffer[0];
        }
        
        python("paint = tf_smoothSkinWeight.smoothPaintClass()"); 
    }

    global proc tf_set_smoothBrushValue( int $slot, int $index, float $val )        
    {
        global string $tf_skinSmoothPatin_selection[];

            if($tf_skinSmoothPatin_selection[0] != "")
            {
                if( stringArrayContains($index, $tf_skinSmoothPatin_selection) )
                    python("paint.setWeight("+$index+","+$val+")"); 
            }
            else
                python("paint.setWeight("+$index+","+$val+")");        
    }
  '''
  mm.eval(cmd)

# -----------------------------------------------------------------------------------
# execute the scripted brush tool and setup the tf_smoothBrush command
# -----------------------------------------------------------------------------------
def paint():
  cmd = '''
    ScriptPaintTool;
    artUserPaintCtx -e -tsc "tf_smoothBrush" `currentCtx`;
  '''
  mm.eval(cmd)

# -----------------------------------------------------------------------------------
# execute the mel procedures for the scripted brush
# -----------------------------------------------------------------------------------
initPaint()

# -----------------------------------------------------------------------------------
# class for holding initializing skincluster relevant stuff
# -----------------------------------------------------------------------------------
class smoothPaintClass():
  
  def __init__(self):
    self.skinCluster = ''
    self.obj = ''
    self.mitVex = ''
    
    # select the skinned geo
    selection = om.MSelectionList()
    om.MGlobal.getActiveSelectionList( selection )

    # get dag path for selection
    dagPath = om.MDagPath()
    components = om.MObject()
    array = om.MIntArray()
    selection.getDagPath( 0, dagPath, components )
    self.obj = dagPath
    dagPath.extendToShape()
    
    # currentNode is MObject to your mesh
    currentNode = dagPath.node()
    self.mitVtx = om.MItMeshVertex (dagPath)
    
    # get skincluster from shape
    try:
      itDG = om.MItDependencyGraph(currentNode, om.MFn.kSkinClusterFilter, om.MItDependencyGraph.kUpstream)
      while not itDG.isDone():
        oCurrentItem = itDG.currentItem()
        fnSkin = oma.MFnSkinCluster(oCurrentItem)
        self.skinCluster = fnSkin
        break
    except:
      om.MGlobal.displayError("No SkinCluster to paint on")
    
  # -----------------------------------------------------------------------------------
  # function to read, average, and set all influence weights on the vertex
  # vtx     (int)     current vertex index
  # value   (float)   weight value from the artisan brush
  # -----------------------------------------------------------------------------------
  def setWeight(self, vtx, value):    
    dagPath = self.obj
    fnSkin = self.skinCluster
    mitVtx = self.mitVtx
    
    if not fnSkin:      # error out when there is no skinCluster defined
      om.MGlobal.displayError("No SkinCluster to paint on")
    else:
      component = om.MFnSingleIndexedComponent().create(om.MFn.kMeshVertComponent)
      om.MFnSingleIndexedComponent(component).addElement( vtx )
      
      oldWeights = om.MDoubleArray()
      surrWeights = om.MDoubleArray()
      infCount = om.MScriptUtil()
      int = infCount.asUintPtr()
      surrVtxArray = om.MIntArray()
      newWeights = om.MDoubleArray()
      infIndices = om.MIntArray()
      prevVtxUtil = om.MScriptUtil( )
      prevVtx = prevVtxUtil.asIntPtr()
      
      # create mesh iterator and get conneted vertices for averaging
      mitVtx = om.MItMeshVertex (dagPath, component)
      mitVtx.getConnectedVertices(surrVtxArray)
      surrVtxCount = len(surrVtxArray)
            
      surrComponents = om.MFnSingleIndexedComponent().create(om.MFn.kMeshVertComponent)
      om.MFnSingleIndexedComponent(surrComponents).addElements( surrVtxArray )
      
      # read weight from single vertex (oldWeights) and from the surrounding vertices (surrWeights)
      fnSkin.getWeights(dagPath, component, oldWeights, int)
      fnSkin.getWeights(dagPath, surrComponents, surrWeights, int)
      influenceCount = om.MScriptUtil.getUint(int)
      
      # average all the surrounding vertex weights and multiply and blend it over the origWeight with the weight from the artisan brush
      for i in range(influenceCount):
        infIndices.append( i )
        newWeights.append( 0.0 )
        for j in range(i,len(surrWeights),influenceCount):
          newWeights[i] += (((surrWeights[j] / surrVtxCount) * value) + ((oldWeights[i] / surrVtxCount) * (1-value)))
      
      # set the final weights throught the skinCluster again
      fnSkin.setWeights( dagPath, component, infIndices, newWeights, 1, oldWeights)