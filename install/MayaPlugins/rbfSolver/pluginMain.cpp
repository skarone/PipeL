#include "rbfSolver.h"
#include <maya/MFnPlugin.h>

MStatus initializePlugin( MObject obj )
{
	MStatus status;
	MFnPlugin plugin( obj, "Ignacio Urruty", "", "Any" );

	status = plugin.registerNode( "rbfSolver", 
									rbfSolver::id,
									rbfSolver::creator,
									rbfSolver::initialize );

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
	status = plugin.deregisterNode( rbfSolver::id );

	if (!status){
		status.perror("deregisterNode");
		return status;
	}

	return status;
}