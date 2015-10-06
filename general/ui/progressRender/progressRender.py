from PySide import QtCore, QtGui
import subprocess
import os

def runBar( fileToRender ): 
	win = QtGui.QMainWindow()
	fileName = os.path.basename( fileToRender )
	win.setWindowTitle('Creating Preview for ' + fileName )
	win.setGeometry(300, 300, 405, 59)
	bar = QtGui.QProgressBar()
	bar.setRange(0, 100)
	bar.setValue(0)
	win.setCentralWidget(bar)
	win.show()
	
 
	#SUB PROCESS Render.exe
	proc = subprocess.Popen('C:/"Program Files"/Autodesk/Maya2015/bin/Render.exe ' + fileToRender,
							shell=True,
							stdout=subprocess.PIPE,
							)
 
	#UPDATE QProgressBar
	for i in range(2000):
		output = proc.stdout.readline()
 
		if "% done" in output:
			#Split the entire string into a list where % occurs and get the first element (since that's where our numbers lie)
			val = [a for a in output.split() if '%' in a]
			value = int( val[0].replace( '%', '') )
			#cast to int and set QProgressBars value
			print value
			bar.setValue(int(value))
 
		#Since we are looping 2000 times (we don't know for how long the render might be outputting for,
		#we have to do an early break if rendering is done and that happens when the exe closes and we can't get
		#any more information from it
		if output is "":
			print "RENDER IS DONE!"
			break
 
