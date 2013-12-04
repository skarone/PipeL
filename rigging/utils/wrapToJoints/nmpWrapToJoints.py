'''
Created by: Nicklas Puetz
website: www.puetz3d.com
email: puetznicklas@gmail.com
Version 1.0: October 2008

To Run: nmpWrapToJoints()

Script Summary: Calculates and Converts Wrap Deformer Weights to SkinCluster Weights. Allows for the Accuracy
                of a Wrap Deformer, but Without the Speed Hindrance. Great for Clothing or Other Accessories on a Character.
                Can Also be Used to Transfer Weights from Nurbs Surfaces to Mesh Surfaces.

Instructions:   Create Wrap Deformer/s for Each Polygonal Object. All Wraps Currently Need to be Connected to the same Source/Driver Geometry.
                Select the Wrapped Geo's and Run Script. You Can Increase the Speed of Initial Calculation by Limiting Wich Verts on the Source
                Geometry Influence the Wrapped Geometry. To do This, First Select all the Verts on the Source Geomtery that Fall within the
                Immediate and Surrounding Area of the Wrapped Geo and THAN Select the Wraped Geometry and Run the Script.
'''

import math
import maya.cmds as cmds
import maya.mel  as mel

#================================================================================================================================================
#                                                   UnHold All SkinCluster Influences Function
#================================================================================================================================================
def nmpHoldUnholdInfluences(skinCluster, onOff=0):
    ''' Holds/Unholds All Influences on the Given SkinCluster '''
    influences = cmds.skinCluster(skinCluster, q=True, inf=True)
    for inf in influences:
        cmds.setAttr(inf + '.liw', onOff)      
#================================================================================================================================================
#                                                   Get Skin From Geo Function
#================================================================================================================================================        
def nmpGetSkinFromGeo(geo):
    ''' Finds and Returns the SkinCluster on the Given Geometry '''
    skinCluster = []
    vertHistory = cmds.listHistory(geo, il=1, pdo=True)
    skinCluster = cmds.ls(vertHistory, type='skinCluster')
    if skinCluster:
        return skinCluster[0]

#================================================================================================================================================
#                                                   Extract Weights Function
#================================================================================================================================================
def nmpExtractWeights(cluster, joint, skinCluster, geoName):
    ''' Calculates the Weighting of Every Joint on Inderectly Connected Wrapped Geometry.
        Weight is Determined By Translating the Master Object and Calculating the Distance
        Changed in 3D Space on Every Vert. Returns list of list of [transform, value]'''
    verts = cmds.ls(geoName + '.vtx[*]', flatten=True)
    values      = []
    cmds.waitCursor( state=True )
    start = cmds.timerX()
    originalPos = [ cmds.xform(vert, q=True, ws=True, t=True) for vert in verts ]
    cmds.setAttr(cluster + '.tz', 1)
    deformPos   = [ cmds.xform(vert, q=True, ws=True, t=True) for vert in verts ]
    cmds.setAttr(cluster + '.tz', 0)
       
    for i in range(0,len(deformPos)):
        difference = [ deformPos[i][0]-originalPos[i][0], deformPos[i][1]-originalPos[i][1], deformPos[i][2]-originalPos[i][2] ]
        distance   = math.sqrt( pow(difference[0],2) + pow(difference[1],2) + pow(difference[2],2) )
        values.append([joint, distance])

    cmds.waitCursor( state=False )
    return values

#================================================================================================================================================
#                                                   nmpExrapWrapWeightsWrapper Function
#================================================================================================================================================
def nmpWrapToJoints():
    ''' Main Function for Extracting the Wrap Weights to Each Joint '''
    # Query Selected Geo with Wrap Deformer --- Get Geo Verts
    objects     = cmds.ls(sl=True, flatten=True)
    
    if not objects:
        raise Exception, 'Please Select Geometry'
    sourceVerts = []
    geoNames    = []
    
    # Separate SourceVerts from Wrapped Geos
    for obj in objects:
        if '.vtx' in obj:
            sourceVerts.append(obj)
        else:
            geoNames.append(obj)
    
    #----------------------------------------------------------------------------------------
    
    # Check for Wrap Deformer --- Retrieve Source Geo from Wrap
    wraps = []
    for geoName in geoNames:
        geoHistory = cmds.listHistory(geoName)
        wrap       = cmds.ls(geoHistory, type='wrap')
        destSkinCluster = nmpGetSkinFromGeo(geoName)
        if destSkinCluster:
            cmds.delete(destSkinCluster)
        if wrap:
            wraps.append(wrap[0])
        else:
            raise Exception, 'No Wrap Deformer Found on ' + geoName
            
    sourceGeo  = cmds.connectionInfo(wraps[0] + '.inflType[0]', sfd=True).split('.')[0]
    
    # If SourceGeo Wasn't Found Try Nurbs Surface Connection
    if not sourceGeo:
        sourceGeoShape  = cmds.connectionInfo(wraps[0] + '.driverPoints[0]', sfd=True).split('.')[0]
        sourceGeo = cmds.listRelatives(sourceGeoShape, p=True)[0]
        sourceVerts = cmds.ls(sourceGeo + '.cv[*]', flatten=True)
        
    #----------------------------------------------------------------------------------------
    
    # Get SkinCluster + Joints of SourceGeo
    indexes = []
    joints = []
    sourceSkinCluster = ''
    try:
        sourceSkinCluster = nmpGetSkinFromGeo(sourceGeo)            
    except:
        raise Exception, 'No SkinCluster Found on Source Geometry'
    
    nmpHoldUnholdInfluences(sourceSkinCluster)
    joints = cmds.skinCluster(sourceSkinCluster, q=True, inf=True)
       
    # If Source Verts Were Selected -> Find Out Which Joints are Affecting those Verts Only to Increase Speed
    if sourceVerts:
        weightedJoints = []      
        for vert in sourceVerts:
            valuesAll = cmds.skinPercent(sourceSkinCluster, vert, q=True, v=True)
            values = cmds.skinPercent(sourceSkinCluster, vert, q=True, v=True, ib=.0001)
            indexes = [ valuesAll.index(value) for value in values if value ]
            
            for i in indexes:
                if joints[i] not in weightedJoints:
                    weightedJoints.append( joints[i] )
                    
        #print 'Weighted Joints = ' + str(weightedJoints)
        indexes = [ joints.index(joint) for joint in weightedJoints ]
        joints = weightedJoints
    
    else:
        sourceVerts = cmds.ls(sourceGeo + '.vtx[*]', flatten=True)
        indexes = [ i for i in range(len(joints)) ]
    
    # Create A Cluster for Every Joint/Influence Object
    clusters, clusterHandles = [], []
    for joint in joints:
        cluster, clusterHan = cmds.cluster(sourceVerts)
        worldPos = cmds.xform(joint, q=True, ws=True, rp=True)
        cmds.xform(clusterHan, ws=True, rp=worldPos)
        cmds.setAttr(clusterHan + '.origin', worldPos[0],worldPos[1], worldPos[2])
        clusters.append(cluster)
        clusterHandles.append(clusterHan)
        
    length = len(sourceVerts)
    amount = 0
    cmds.progressWindow(title='Transferring Wrap Weights', progress=amount, status='Retrieving Joint Weights', isInterruptable=True )

    #----------------------------------------------------------------------------------------
    
    # Retrieve Joint Weights for Each Vert --> apply Those to each corresponding Cluster
    for a,vert in enumerate(sourceVerts):
        values = cmds.skinPercent(sourceSkinCluster, vert, q=True, v=True)
        
        for i,cluster in enumerate(clusters):
            cmds.percent(cluster, vert, v=values[indexes[i]])
            
        if cmds.progressWindow( query=True, isCancelled=True ) : break
        amount = int( str( a/float(length) * 100 ).split('.')[0] )
        cmds.progressWindow( edit=True, progress=amount, status=('Retrieving Joint Weights: ' + `amount` + '%' ) )
    
    #----------------------------------------------------------------------------------------
    
    # Check Each Joint in Source SkinCluster ---> Separate by type Joints and Influence Objects
    bindJoints = []
    influenceObjects = []
    for joint in joints:
        if cmds.nodeType(joint) == 'joint':
            bindJoints.append(joint)
        else:
            influenceObjects.append(joint)
    if not bindJoints:
        bindJoints.append( cmds.joint(p=[0,0,0], n='nmpTempJoint') )
                
    # Iterate Through Each Piece of Wrapped Geo --> Assign Skin Weights
    for i,geoName in enumerate(geoNames):
        destSkinCluster = cmds.skinCluster(bindJoints, geoName)[0]
        
        # Add Influence Objects To SkinCluster if They Exist in sourceSkinCluster
        if influenceObjects:
            cmds.skinCluster(destSkinCluster, e=True, ai=influenceObjects)
        
        # Get Weights for Each Joint - Return Value Per Cluster = [ [joint, distance], [joint, distance], ....... ]
        length = len(clusterHandles)
        amount = 0
        cmds.progressWindow(e=True, progress=amount, status= 'Calculating Wrap Weights...', isInterruptable=True )
        values = []
        for i,clusterHan in enumerate(clusterHandles):
            values.append( nmpExtractWeights(clusterHan, joints[i], destSkinCluster, geoName) )
            if cmds.progressWindow( query=True, isCancelled=True ) : break
            amount = int( str( i/float(length) * 100 ).split('.')[0] )
            cmds.progressWindow( edit=True, progress=amount, status=('Calculating Wrap Weights : %s...' % geoName  + `amount` + '%' ) )
    
        #----------------------------------------------------------------------------------------
    
        # Create List of Lists of Each Verts weights --- [ [transform, value] ]  --- Reduces Amount of skinPercent Calls
        vertWeights = [  ]
        verts = cmds.ls(geoName + '.vtx[*]', flatten=True)
        for i in range( len(verts) ):
            appendObj = []
            for i2 in range( len(values) ):
                appendObj.append( [ values[i2][0][0], values[i2][i][1] ])
                
            vertWeights.append(appendObj)
    
        length = len(verts)
        amount = 0
        cmds.progressWindow(e=True, progress=amount, status='Assigning Weights: ' + geoName, isInterruptable=True )
        
        # Clear All Weights to Avoid "Greater Than 1.0 Weight" Error
        cmds.setAttr(destSkinCluster + '.normalizeWeights', 0)
        cmds.skinPercent(destSkinCluster, geoName, pruneWeights=1.0 )
    
        #----------------------------------------------------------------------------------------
        
        # Assign SkinWeights
        for i,vert in enumerate(verts):
            cmds.skinPercent(destSkinCluster, vert, tv=vertWeights[i] )
            if cmds.progressWindow( query=True, isCancelled=True ) : break
            amount = int( str( i/float(length) * 100 ).split('.')[0] )
            cmds.progressWindow( edit=True, progress=amount, status=('Assigning Weights: ' + geoName + '  ' + `amount` + '%' ) )
        
        # Prune off any small excess weighting that normalizeing missed
        cmds.setAttr(destSkinCluster + '.normalizeWeights', 1)
        cmds.skinPercent(destSkinCluster, geoName, pruneWeights=.005 )

    cmds.delete(clusters, clusterHandles, wraps)
    try: cmds.delete('nmpTempJoint')
    except: pass
    cmds.progressWindow(endProgress=1)
    
    #----------------------------------------------------------------------------------------
    
    print 'Wrap Weights Transfered !!!',      