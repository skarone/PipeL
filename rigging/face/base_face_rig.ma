//Maya ASCII 2013 scene
//Name: base_head_rig.ma
//Last modified: Tue, Dec 10, 2013 04:35:00 PM
//Codeset: 1252
requires maya "2013";
requires "stereoCamera" "10.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2013";
fileInfo "version" "2013 x64";
fileInfo "cutIdentifier" "201202220241-825136";
fileInfo "osv" "Microsoft Windows 7 Ultimate Edition, 64-bit Windows 7 Service Pack 1 (Build 7601)\n";
createNode transform -n "base_head_rig_grp";
createNode transform -n "l_brow_crv" -p "base_head_rig_grp";
	addAttr -ci true -sn "controls_count" -ln "controls_count" -dv 1 -min 1 -at "long";
	addAttr -ci true -sn "use_tips" -ln "use_tips" -min 0 -max 1 -at "bool";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
	setAttr -k on ".controls_count" 3;
	setAttr -k on ".use_tips" yes;
createNode nurbsCurve -n "l_brow_crvShape" -p "l_brow_crv";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 1 0 no 3
		6 0 0 0 1 1 1
		4
		1.6321045597694095 111.79194320022475 10.910643373505895
		3.5486684425005852 111.96495178310821 11.024522450325312
		5.4738081040356947 111.84665758760298 9.4259231310448151
		6.7381357837704767 110.92590787894136 7.3531934972366031
		;
createNode transform -n "c_cheek_crv" -p "base_head_rig_grp";
	addAttr -ci true -sn "controls_count" -ln "controls_count" -dv 1 -min 1 -at "long";
	addAttr -ci true -sn "use_tips" -ln "use_tips" -min 0 -max 1 -at "bool";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
	setAttr -k on ".controls_count" 7;
	setAttr -k on ".use_tips" yes;
createNode nurbsCurve -n "c_cheek_crvShape" -p "c_cheek_crv";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 4 0 no 3
		9 0 0 0 1 2 3 4 4 4
		7
		3.4373942238814954 104.89549073055389 9.6171792628741599
		5.180981523323009 103.17629776872428 9.1171100078573701
		4.322610068539924 100.65373544853958 7.3679504165146463
		0 99.349877820948976 9.9161215171158155
		-4.322610068539924 100.65373544853958 7.3679504165146463
		-5.180981523323009 103.17629776872428 9.1171100078573701
		-3.4373942238814954 104.89549073055389 9.6171792628741599
		;
createNode nurbsCurve -n "c_cheek_crvShape2Original" -p "c_cheek_crv";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".cc" -type "nurbsCurve" 
		3 2 0 no 3
		7 0 0 0 1 2 2 2
		5
		3.4373942238814954 104.89549073055389 9.6171792628741599
		5.180981523323009 103.17629776872428 9.1171100078573701
		5.2423506556963 101.61712215511851 6.745146180517426
		3.6843777149547234 99.884669923686886 8.1978085425497706
		0.01673390820385906 98.758456331506622 8.2331669697921637
		;
createNode transform -n "r_brow_crv" -p "base_head_rig_grp";
	addAttr -ci true -sn "controls_count" -ln "controls_count" -dv 1 -min 1 -at "long";
	addAttr -ci true -sn "use_tips" -ln "use_tips" -min 0 -max 1 -at "bool";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr ".s" -type "double3" -1 1 1 ;
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
	setAttr -k on ".controls_count" 3;
	setAttr -k on ".use_tips" yes;
createNode nurbsCurve -n "r_brow_crvShape" -p "r_brow_crv";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 1 0 no 3
		6 0 0 0 1 1 1
		4
		1.6321045597694095 111.79194320022475 10.910643373505895
		3.5486684425005852 111.96495178310821 11.024522450325312
		5.4738081040356947 111.84665758760298 9.4259231310448151
		6.7381357837704767 110.92590787894136 7.3531934972366031
		;
createNode transform -n "l_nose_pnt" -p "base_head_rig_grp";
	setAttr ".t" -type "double3" 1.2913999557495117 105.93122863769531 10.861171722412109 ;
createNode locator -n "l_nose_pntShape" -p "l_nose_pnt";
	setAttr -k off ".v";
createNode transform -n "c_nose_pnt" -p "base_head_rig_grp";
	setAttr ".t" -type "double3" 0 105.83322143554687 11.953701019287109 ;
createNode locator -n "c_nose_pntShape" -p "c_nose_pnt";
	setAttr -k off ".v";
createNode transform -n "r_nose_pnt" -p "base_head_rig_grp";
	setAttr ".t" -type "double3" -1.291 105.93122863769531 10.861171722412109 ;
createNode locator -n "r_nose_pntShape" -p "r_nose_pnt";
	setAttr -k off ".v";
createNode transform -n "c_eyebrows_pnt" -p "base_head_rig_grp";
	setAttr ".t" -type "double3" 0 111.71549224853516 10.925433158874512 ;
createNode locator -n "c_eyebrows_pntShape" -p "c_eyebrows_pnt";
	setAttr -k off ".v";
createNode transform -n "l_eyeOuter_pnt" -p "base_head_rig_grp";
	setAttr ".t" -type "double3" 8.4656545848527021 109.02521198848069 4.4409172368433101 ;
createNode locator -n "l_eyeOuter_pntShape" -p "l_eyeOuter_pnt";
	setAttr -k off ".v";
createNode transform -n "r_eyeOuter_pnt" -p "base_head_rig_grp";
	setAttr ".t" -type "double3" -8.466 109.02521198848069 4.4409172368433101 ;
createNode locator -n "r_eyeOuter_pntShape" -p "r_eyeOuter_pnt";
	setAttr -k off ".v";
createNode transform -n "l_cheekOuter_pnt" -p "base_head_rig_grp";
	setAttr ".t" -type "double3" 7.0680632964474626 104.71007624030611 6.2532860249582463 ;
createNode locator -n "l_cheekOuter_pntShape" -p "l_cheekOuter_pnt";
	setAttr -k off ".v";
createNode transform -n "r_cheekOuter_pnt" -p "base_head_rig_grp";
	setAttr ".t" -type "double3" -7.068 104.71007624030611 6.2532860249582463 ;
createNode locator -n "r_cheekOuter_pntShape" -p "r_cheekOuter_pnt";
	setAttr -k off ".v";
createNode transform -n "c_chin_pnt" -p "base_head_rig_grp";
	setAttr ".t" -type "double3" 0 97.811729431152344 7.5456771850585938 ;
createNode locator -n "c_chin_pntShape" -p "c_chin_pnt";
	setAttr -k off ".v";
createNode transform -n "c_lower_mouth_crv" -p "base_head_rig_grp";
	addAttr -ci true -sn "controls_count" -ln "controls_count" -dv 1 -min 1 -at "long";
	addAttr -ci true -sn "use_tips" -ln "use_tips" -min 0 -max 1 -at "bool";
	setAttr ".ovdt" 2;
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
	setAttr ".it" no;
	setAttr -k on ".controls_count" 3;
	setAttr -k on ".use_tips";
createNode nurbsCurve -n "c_lower_mouth_crvShape" -p "c_lower_mouth_crv";
	setAttr -k off ".v";
	setAttr ".tw" yes;
	setAttr -s 5 ".cp[0:4]" -type "double3" -0.058415918407134004 0 0 
		0 -0.064674030785596415 0.19046574075791156 0 -0.40562164170950155 0.19046574075791156 
		0 -0.064674030785596415 0.19046574075791156 0.058415918407134004 0 0;
createNode nurbsCurve -n "c_lower_mouth_crvShape2Orig" -p "c_lower_mouth_crv";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".cc" -type "nurbsCurve" 
		3 2 0 no 3
		7 0 0 0 1 2 2 2
		5
		-1.8713817219362721 102.5708582990072 10.137053342026432
		-1.0459557787807523 102.49910822373415 10.760242877346744
		0 102.43674130995744 11.139950034852292
		1.046 102.49910822373415 10.760242877346744
		1.871 102.5708582990072 10.137053342026432
		;
createNode transform -n "c_upper_mouth_crv" -p "base_head_rig_grp";
	addAttr -ci true -sn "controls_count" -ln "controls_count" -dv 1 -min 1 -at "long";
	addAttr -ci true -sn "use_tips" -ln "use_tips" -min 0 -max 1 -at "bool";
	setAttr ".ovdt" 2;
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
	setAttr ".it" no;
	setAttr -k on ".controls_count" 5;
	setAttr -k on ".use_tips" yes;
createNode nurbsCurve -n "c_upper_mouth_crvShape" -p "c_upper_mouth_crv";
	setAttr -k off ".v";
	setAttr ".tw" yes;
	setAttr -s 5 ".cp[0:4]" -type "double3" -0.058415918407134004 0 0 
		0 0 0.19046574075791156 0 0.22427317035749184 0.19046574075791156 0 0 0.19046574075791156 
		0.058415918407134004 0 0;
createNode nurbsCurve -n "c_upper_mouth_crvShape1Orig" -p "c_upper_mouth_crv";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".cc" -type "nurbsCurve" 
		3 2 0 no 3
		7 0 0 0 1 2 2 2
		5
		-1.8713817219362721 102.5708582990072 10.137053342026432
		-1.0583492360233946 102.84263221335118 10.754520798307016
		0 102.87309065865472 11.157883905503525
		1.0580000000000001 102.84263221335118 10.754520798307016
		1.871 102.5708582990072 10.137053342026432
		;
select -ne :time1;
	setAttr ".o" 1;
	setAttr ".unw" 1;
select -ne :renderPartition;
	setAttr -s 4 ".st";
select -ne :initialShadingGroup;
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultShaderList1;
	setAttr -s 4 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
select -ne :renderGlobalsList1;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
select -ne :defaultHardwareRenderGlobals;
	setAttr ".fn" -type "string" "im";
	setAttr ".res" -type "string" "ntsc_4d 646 485 1.333";
connectAttr "c_lower_mouth_crvShape2Orig.ws" "c_lower_mouth_crvShape.cr";
connectAttr "c_upper_mouth_crvShape1Orig.ws" "c_upper_mouth_crvShape.cr";
// End of base_head_rig.ma
