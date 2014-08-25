import os, sys
import nuke, nukescripts

def main():
	# Get the repository root
	try:
		stdout = None
		if os.path.exists( "/Applications/Deadline/Resources/bin/deadlinecommand" ):
			stdout = os.popen( "/Applications/Deadline/Resources/bin/deadlinecommand GetRepositoryRoot" )
		else:
			stdout = os.popen( "deadlinecommand GetRepositoryRoot" )
		path = stdout.read()
		stdout.close()
		
		if path == "" or path == None:
			nuke.message( "The SubmitNukeToDeadline.py script could not be found in the Deadline Repository. Please make sure that the Deadline Client has been installed on this machine, that the Deadline Client bin folder is in your PATH, and that the Deadline Client has been configured to point to a valid Repository." )
		else:
			path += "/submission/Nuke"
			path = path.replace("\n","").replace( "\\", "/" )
			
			# Add the path to the system path
			print "Appending \"" + path + "\" to system path to import SubmitNukeToDeadline module"
			sys.path.append( path )

			# Import the script and call the main() function
			import SubmitNukeToDeadline
			SubmitNukeToDeadline.SubmitToDeadline( path )
	except IOError:
		nuke.message( "An error occurred while getting the repository root from Deadline. Please try again, or if this is a persistent problem, contact Deadline Support." )
