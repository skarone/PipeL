//Maya ASCII 2013 scene
//Name: base_face_rig.ma
//Last modified: Mon, Aug 04, 2014 11:57:05 AM
//Codeset: 1252
requires maya "2013";
requires "Mayatomr" "2013.0 - 3.10.1.11 ";
requires "stereoCamera" "10.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2013";
fileInfo "version" "2013 x64";
fileInfo "cutIdentifier" "201209210409-845513";
fileInfo "osv" "Microsoft Windows 7 Business Edition, 64-bit Windows 7 Service Pack 1 (Build 7601)\n";
createNode transform -n "base_head_rig_grp";
	setAttr ".t" -type "double3" 0 -5.1294836540823887 -3.4723172682647032 ;
	setAttr ".s" -type "double3" 1.164760297692917 1.164760297692917 1.164760297692917 ;
	setAttr ".rp" -type "double3" 0.0017791223541715863 123.09441570831385 22.539988040924072 ;
	setAttr ".sp" -type "double3" 0.0015274579307824609 105.68218710075492 19.351610872700455 ;
	setAttr ".spt" -type "double3" 0.00025166442338912532 17.412228607558934 3.1883771682236168 ;
createNode transform -n "l_brow_crv" -p "base_head_rig_grp";
	addAttr -ci true -sn "controls_count" -ln "controls_count" -dv 1 -min 1 -at "long";
	addAttr -ci true -sn "use_tips" -ln "use_tips" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 0 8.3640283869147076 16.709231392487386 ;
	setAttr ".rp" -type "double3" 4.1851201717699444 111.44542983102478 9.1888579737809586 ;
	setAttr ".sp" -type "double3" 4.1851201717699444 111.44542983102478 9.1888579737809586 ;
	setAttr -k on ".controls_count" 3;
	setAttr -k on ".use_tips" yes;
createNode nurbsCurve -n "l_brow_crvShape" -p "l_brow_crv";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 1 0 no 3
		6 0 0 0 1 1 1
		4
		5.2120992040486209 109.13933472655148 7.4875828613649595
		8.6961661037997029 112.79576948049244 8.2694119815381342
		15.602202169186326 112.97484227790538 2.6386158287111883
		17.318622981378798 109.48243088118539 -0.3835857840051986
		;
createNode transform -n "c_cheek_crv" -p "base_head_rig_grp";
	addAttr -ci true -sn "controls_count" -ln "controls_count" -dv 1 -min 1 -at "long";
	addAttr -ci true -sn "use_tips" -ln "use_tips" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 0 -0.56952596124838784 19.335656431850904 ;
	setAttr ".rp" -type "double3" 0 102.12268427575142 8.6420359668152305 ;
	setAttr ".sp" -type "double3" 0 102.12268427575142 8.6420359668152305 ;
	setAttr -k on ".controls_count" 7;
	setAttr -k on ".use_tips" yes;
createNode nurbsCurve -n "c_cheek_crvShape" -p "c_cheek_crv";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 4 0 no 3
		9 0 0 0 1 2 3 4 4 4
		7
		6.0502206725614078 107.15369351590364 4.7997667061384934
		11.196475180780295 100.48210800684852 4.3900673036795395
		4.7968366451980851 94.714316410627802 4.6788861078213104
		0 95.472796412990121 5.0919732104213864
		-4.7968366451980851 94.714316410627802 4.6788861078213104
		-11.196475180780295 100.48210800684852 4.3900673036795395
		-6.0502206725614078 107.15369351590364 4.7997667061384934
		;
createNode nurbsCurve -n "c_cheek_crvShape2Original" -p "c_cheek_crv";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".cc" -type "nurbsCurve" 
		3 2 0 no 3
		7 0 0 0 1 2 2 2
		5
		3.4373942238814954 104.89549073055387 9.6171792628741599
		5.180981523323009 103.17629776872428 9.1171100078573701
		5.2423506556963 101.61712215511852 6.745146180517426
		3.684377714954723 99.884669923686886 8.1978085425497706
		0.01673390820385906 98.758456331506622 8.2331669697921637
		;
createNode transform -n "r_brow_crv" -p "base_head_rig_grp";
	addAttr -ci true -sn "controls_count" -ln "controls_count" -dv 1 -min 1 -at "long";
	addAttr -ci true -sn "use_tips" -ln "use_tips" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 2.0787440565186497 8.6740643108013558 17.701459507994937 ;
	setAttr ".s" -type "double3" -1 1 1 ;
	setAttr ".rp" -type "double3" -4.1851201717699444 111.44542983102478 9.1888579737809586 ;
	setAttr ".sp" -type "double3" 4.1851201717699444 111.44542983102478 9.1888579737809586 ;
	setAttr ".spt" -type "double3" -8.3702403435398871 0 0 ;
	setAttr -k on ".controls_count" 3;
	setAttr -k on ".use_tips" yes;
createNode nurbsCurve -n "r_brow_crvShape" -p "r_brow_crv";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 1 0 no 3
		6 0 0 0 1 1 1
		4
		7.2908432605672724 108.82929880266484 6.4953547458574086
		10.774910160318356 112.48573355660578 7.277183866030585
		17.680946225704975 112.66480635401872 1.6463877132036382
		19.39736703789745 109.17239495729876 -1.375813899512746
		;
createNode transform -n "c_lower_mouth_crv" -p "base_head_rig_grp";
	addAttr -ci true -sn "controls_count" -ln "controls_count" -dv 1 -min 1 -at "long";
	addAttr -ci true -sn "use_tips" -ln "use_tips" -min 0 -max 1 -at "bool";
	setAttr ".ovdt" 2;
	setAttr ".t" -type "double3" 6.0185310762101134e-036 -2.3714039086764105 17.812922502272805 ;
	setAttr ".rp" -type "double3" -0.00019086096813603071 102.30098898362758 10.733734558818318 ;
	setAttr ".sp" -type "double3" -0.00019086096813603071 102.30098898362758 10.733734558818318 ;
	setAttr -k on ".controls_count" 3;
	setAttr -k on ".use_tips";
createNode nurbsCurve -n "c_lower_mouth_crvShape" -p "c_lower_mouth_crv";
	setAttr -k off ".v";
	setAttr ".tw" yes;
	setAttr -s 5 ".cp[0:4]" -type "double3" -3.58838514982763 0.52039006655240883 
		-3.6649074494804417 -1.9844001643232121 -0.74314111377195502 -3.2749439642558471 
		0 -0.88995765003279803 0.095442137942978178 1.9844001643232121 -0.74314111377195502 
		-3.2749439642558471 3.5883851498276305 0.52039006655240883 -3.6649074494804417;
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
	setAttr ".t" -type "double3" 6.0185310762101134e-036 -3.1554436208840493e-030 15.519435612516563 ;
	setAttr ".rp" -type "double3" -0.00019086096813603071 102.8341110640097 10.742701494143931 ;
	setAttr ".sp" -type "double3" -0.00019086096813603071 102.8341110640097 10.742701494143931 ;
	setAttr -k on ".controls_count" 5;
	setAttr -k on ".use_tips" yes;
createNode nurbsCurve -n "c_upper_mouth_crvShape" -p "c_upper_mouth_crv";
	setAttr -k off ".v";
	setAttr ".tw" yes;
	setAttr -s 5 ".cp[0:4]" -type "double3" -3.58838514982763 -1.8510138421239759 
		-1.3714205597242 -1.8122051375642352 -1.5493191273139786 0.81069424424103076 0 -1.4003100193376239 
		1.0188457688209986 1.8122051375642352 -1.5493191273139786 0.81069424424103076 3.5883851498276305 
		-1.8510138421239759 -1.3714205597242;
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
createNode transform -n "l_nose_pnt" -p "base_head_rig_grp";
createNode locator -n "l_nose_pntShape" -p "l_nose_pnt";
	setAttr -k off ".v";
createNode transform -n "c_nose_pnt" -p "base_head_rig_grp";
	setAttr ".t" -type "double3" 1.0675584888206102e-018 106.63544475061602 28.808776728725253 ;
createNode locator -n "c_nose_pntShape" -p "c_nose_pnt";
	setAttr -k off ".v";
createNode transform -n "r_nose_pnt" -p "base_head_rig_grp";
	setAttr ".t" -type "double3" -2.1997164371126625 106.24302976370583 27.157357381551719 ;
createNode locator -n "r_nose_pntShape" -p "r_nose_pnt";
	setAttr -k off ".v";
createNode transform -n "c_eyebrows_pnt" -p "base_head_rig_grp";
	setAttr ".t" -type "double3" 0.00025710360131997456 116.7418091482614 25.325974997808327 ;
createNode locator -n "c_eyebrows_pntShape" -p "c_eyebrows_pnt";
	setAttr -k off ".v";
createNode transform -n "l_eyeOuter_pnt" -p "base_head_rig_grp";
createNode locator -n "l_eyeOuter_pntShape" -p "l_eyeOuter_pnt";
	setAttr -k off ".v";
createNode transform -n "r_eyeOuter_pnt" -p "base_head_rig_grp";
	setAttr ".t" -type "double3" -19.839530411359235 112.73920117247769 11.62925238790457 ;
createNode locator -n "r_eyeOuter_pntShape" -p "r_eyeOuter_pnt";
	setAttr -k off ".v";
createNode transform -n "l_cheekOuter_pnt" -p "base_head_rig_grp";
createNode locator -n "l_cheekOuter_pntShape" -p "l_cheekOuter_pnt";
	setAttr -k off ".v";
createNode transform -n "r_cheekOuter_pnt" -p "base_head_rig_grp";
	setAttr ".t" -type "double3" -17.365566767127074 99.060019137163252 14.75180299278947 ;
createNode locator -n "r_cheekOuter_pntShape" -p "r_cheekOuter_pnt";
	setAttr -k off ".v";
createNode transform -n "c_chin_pnt" -p "base_head_rig_grp";
	setAttr ".t" -type "double3" 0.0023725151872949126 89.564420117665605 20.688935828261435 ;
createNode locator -n "c_chin_pntShape" -p "c_chin_pnt";
	setAttr -k off ".v";
createNode multiplyDivide -n "multiplyDivide3";
	setAttr ".i2" -type "float3" -1 1 1 ;
createNode multiplyDivide -n "multiplyDivide1";
	setAttr ".i2" -type "float3" -1 1 1 ;
createNode multiplyDivide -n "multiplyDivide2";
	setAttr ".i2" -type "float3" -1 1 1 ;
select -ne :time1;
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".o" 1;
	setAttr -av ".unw" 1;
lockNode -l 1 ;
select -ne :renderPartition;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 14 ".st";
	setAttr -cb on ".an";
	setAttr -cb on ".pt";
lockNode -l 1 ;
select -ne :initialShadingGroup;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 20 ".dsm";
	setAttr -k on ".mwc";
	setAttr -cb on ".an";
	setAttr -cb on ".il";
	setAttr -cb on ".vo";
	setAttr -cb on ".eo";
	setAttr -cb on ".fo";
	setAttr -cb on ".epo";
	setAttr -k on ".ro" yes;
	setAttr -s 2 ".gn";
	setAttr -cb on ".mimt";
	setAttr -cb on ".miop";
	setAttr -cb on ".mise";
	setAttr -cb on ".mism";
	setAttr -cb on ".mice";
	setAttr -av -cb on ".micc";
	setAttr -cb on ".mica";
	setAttr -cb on ".micw";
	setAttr -cb on ".mirw";
lockNode -l 1 ;
select -ne :initialParticleSE;
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".mwc";
	setAttr -cb on ".an";
	setAttr -cb on ".il";
	setAttr -cb on ".vo";
	setAttr -cb on ".eo";
	setAttr -cb on ".fo";
	setAttr -cb on ".epo";
	setAttr -k on ".ro" yes;
	setAttr -cb on ".mimt";
	setAttr -cb on ".miop";
	setAttr -cb on ".mise";
	setAttr -cb on ".mism";
	setAttr -cb on ".mice";
	setAttr -av -cb on ".micc";
	setAttr -cb on ".mica";
	setAttr -av -cb on ".micw";
	setAttr -cb on ".mirw";
lockNode -l 1 ;
select -ne :defaultShaderList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 15 ".s";
lockNode -l 1 ;
select -ne :defaultTextureList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 20 ".tx";
select -ne :postProcessList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 2 ".p";
lockNode -l 1 ;
select -ne :defaultRenderUtilityList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 29 ".u";
lockNode -l 1 ;
select -ne :defaultRenderingList1;
lockNode -l 1 ;
select -ne :renderGlobalsList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
lockNode -l 1 ;
select -ne :defaultResolution;
	setAttr -av -k on ".cch";
	setAttr -k on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -k on ".bnm";
	setAttr -av -k on ".w";
	setAttr -av -k on ".h";
	setAttr -av -k on ".pa" 1;
	setAttr -av -k on ".al";
	setAttr -av -k on ".dar";
	setAttr -av -k on ".ldar";
	setAttr -k on ".dpi";
	setAttr -av -k on ".off";
	setAttr -av -k on ".fld";
	setAttr -av -k on ".zsl";
	setAttr -k on ".isu";
	setAttr -k on ".pdu";
select -ne :defaultLightSet;
	setAttr -k on ".cch";
	setAttr -k on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -k on ".bnm";
	setAttr -k on ".mwc";
	setAttr -k on ".an";
	setAttr -k on ".il";
	setAttr -k on ".vo";
	setAttr -k on ".eo";
	setAttr -k on ".fo";
	setAttr -k on ".epo";
	setAttr -k on ".ro" yes;
lockNode -l 1 ;
select -ne :defaultObjectSet;
	setAttr -k on ".cch";
	setAttr -k on ".ihi";
	setAttr -k on ".nds";
	setAttr -k on ".bnm";
	setAttr -k on ".mwc";
	setAttr -k on ".an";
	setAttr -k on ".il";
	setAttr -k on ".vo";
	setAttr -k on ".eo";
	setAttr -k on ".fo";
	setAttr -k on ".epo";
	setAttr ".ro" yes;
lockNode -l 1 ;
select -ne :hardwareRenderGlobals;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr ".ctrs" 256;
	setAttr -av ".btrs" 512;
	setAttr -k off ".fbfm";
	setAttr -k off -cb on ".ehql";
	setAttr -k off -cb on ".eams";
	setAttr -k off -cb on ".eeaa";
	setAttr -k off -cb on ".engm";
	setAttr -k off -cb on ".mes";
	setAttr -k off -cb on ".emb";
	setAttr -av -k off -cb on ".mbbf";
	setAttr -k off -cb on ".mbs";
	setAttr -k off -cb on ".trm";
	setAttr -k off -cb on ".tshc";
	setAttr -k off ".enpt";
	setAttr -k off -cb on ".clmt";
	setAttr -k off -cb on ".tcov";
	setAttr -k off -cb on ".lith";
	setAttr -k off -cb on ".sobc";
	setAttr -k off -cb on ".cuth";
	setAttr -k off -cb on ".hgcd";
	setAttr -k off -cb on ".hgci";
	setAttr -k off -cb on ".mgcs";
	setAttr -k off -cb on ".twa";
	setAttr -k off -cb on ".twz";
	setAttr -k on ".hwcc";
	setAttr -k on ".hwdp";
	setAttr -k on ".hwql";
	setAttr -k on ".hwfr";
	setAttr -k on ".soll";
	setAttr -k on ".sosl";
	setAttr -k on ".bswa";
	setAttr -k on ".shml";
	setAttr -k on ".hwel";
lockNode -l 1 ;
select -ne :defaultHardwareRenderGlobals;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -av -k on ".rp";
	setAttr -k on ".cai";
	setAttr -k on ".coi";
	setAttr -cb on ".bc";
	setAttr -av -k on ".bcb";
	setAttr -av -k on ".bcg";
	setAttr -av -k on ".bcr";
	setAttr -k on ".ei";
	setAttr -k on ".ex";
	setAttr -av -k on ".es";
	setAttr -av -k on ".ef";
	setAttr -av -k on ".bf";
	setAttr -k on ".fii";
	setAttr -av -k on ".sf";
	setAttr -k on ".gr";
	setAttr -k on ".li";
	setAttr -k on ".ls";
	setAttr -k on ".mb";
	setAttr -k on ".ti";
	setAttr -k on ".txt";
	setAttr -k on ".mpr";
	setAttr -k on ".wzd";
	setAttr -k on ".fn" -type "string" "im";
	setAttr -k on ".if";
	setAttr -k on ".res" -type "string" "ntsc_4d 646 485 1.333";
	setAttr -k on ".as";
	setAttr -k on ".ds";
	setAttr -k on ".lm";
	setAttr -k on ".fir";
	setAttr -k on ".aap";
	setAttr -k on ".gh";
	setAttr -cb on ".sd";
lockNode -l 1 ;
select -ne :ikSystem;
	setAttr -s 4 ".sol";
connectAttr "c_lower_mouth_crvShape2Orig.ws" "c_lower_mouth_crvShape.cr";
connectAttr "c_upper_mouth_crvShape1Orig.ws" "c_upper_mouth_crvShape.cr";
connectAttr "r_nose_pnt.ty" "l_nose_pnt.ty";
connectAttr "r_nose_pnt.tz" "l_nose_pnt.tz";
connectAttr "multiplyDivide3.ox" "l_nose_pnt.tx";
connectAttr "r_eyeOuter_pnt.ty" "l_eyeOuter_pnt.ty";
connectAttr "r_eyeOuter_pnt.tz" "l_eyeOuter_pnt.tz";
connectAttr "multiplyDivide1.ox" "l_eyeOuter_pnt.tx";
connectAttr "r_cheekOuter_pnt.ty" "l_cheekOuter_pnt.ty";
connectAttr "r_cheekOuter_pnt.tz" "l_cheekOuter_pnt.tz";
connectAttr "multiplyDivide2.ox" "l_cheekOuter_pnt.tx";
connectAttr "r_nose_pnt.tx" "multiplyDivide3.i1x";
connectAttr "r_eyeOuter_pnt.tx" "multiplyDivide1.i1x";
connectAttr "r_cheekOuter_pnt.tx" "multiplyDivide2.i1x";
connectAttr "multiplyDivide1.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "multiplyDivide2.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "multiplyDivide3.msg" ":defaultRenderUtilityList1.u" -na;
// End of base_face_rig.ma
