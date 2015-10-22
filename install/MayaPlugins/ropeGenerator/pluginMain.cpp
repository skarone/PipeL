#include "ropeGenerator.h"
#include <maya/MFnPlugin.h>

MStatus initializePlugin( MObject obj )
{
	MStatus status;
	MFnPlugin plugin( obj, "Ignacio Urruty", "", "Any" );

	status = plugin.registerNode( "ropeGenerator", 
									ropeGenerator::id,
									ropeGenerator::creator,
									ropeGenerator::initialize );

	if (!status){
		status.perror("registerNode");
		return status;
	}

	return status;
}

MStatus uninitializePlugin( MObject obj )
{
	MStatus status;
	MFnPlugin plugin( obj );
	status = plugin.deregisterNode( ropeGenerator::id );

	if (!status){
		status.perror("deregisterNode");
		return status;
	}

	return status;
}
