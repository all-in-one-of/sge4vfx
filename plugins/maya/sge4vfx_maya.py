import os, shutil, re
import maya.cmds as mc
from datetime import datetime
from subprocess import Popen,PIPE

class renderDialog:
	priorities = { "Normal" : "0", "Low" : "-300", "Whenever" : "-600" }
	gigPerSlot = 2

	def __init__(self):
		# Load the QT Designer UI file
		relPath = os.path.dirname(os.path.realpath(__file__))
		self.UIElements = {}
		self.UIElements["window"] = mc.loadUI(uiFile = relPath + '/dialog.ui')
		# Get the list of renderers available and fill the combo box
		for renderer in mc.renderer(query=True, namesOfAvailableRenderers=True):
			mc.menuItem(label=renderer, parent="rendererComboBox")
		for camera in mc.listCameras(orthographic=True, perspective=True):
			mc.menuItem(label=camera, parent="cameraComboBox")
		# Fill in the start and end frames along with the batch number
		mc.textField("startFrameLineEdit", edit=True, text=
			str(int(mc.getAttr('defaultRenderGlobals.startFrame'))))
		mc.textField("endFrameLineEdit", edit=True, text=
			str(int(mc.getAttr('defaultRenderGlobals.endFrame'))))
		mc.textField("batchSizeLineEdit", edit=True, text="1")
		# Show the window
		mc.showWindow(self.UIElements["window"])
	
	# Build a date string to save off the SGE submission stuff
	def buildDateTime():
		return datetime.now().strftime("%Y%m%d-%H%M%S")
	
	# Write out the Maya command file
	def writeMayaCmdFile(sgePath, mayaCmd):
		mf = open(sgePath + "/mayaCommand.sh", "w")
		
		mf.write("#!/bin/bash\n\n")
		mf.write("#$ -o " + sgePath + "/logs/o.$TASK_ID\n")
		mf.write("#$ -e " + sgePath + "/logs/e.$TASK_ID\n\n")
		mf.write("> $SGE_STDOUT_PATH\n")
		mf.write("> $SGE_STDERR_PATH\n\n")
		# I put the batch endframe calculation stuff into the script
		# either way.  If it's not a batch job, ENDFRAME will just never
		# be used by the Maya command on the following lines
		mf.write("let ENDFRAME=${SGE_TASK_ID}+${SGE_TASK_STEPSIZE}-1\n")
		mf.write("if [ ${ENDFRAME} -gt ${SGE_TASK_LAST} ]; then\n")
		mf.write("	ENDFRAME=${SGE_TASK_LAST}\n")
		mf.write("fi\n\n")
		mf.write(mayaCmd + "\n")
		mf.write("\n# Write return code for epilog script\n")
		mf.write("echo $? > /tmp/${JOB_ID}-${SGE_TASK_ID}-return\n")
		mf.close()
		
		os.chmod(sgePath + "/mayaCommand.sh", 0755)
	
	# Write out the SGE command file
	def writeSGECmdFile(sgePath, sgeCmd):
		sf = open(sgePath + "/sgeMaya.sh", "w")
		
		sf.write("#!/bin/bash\n\n")
		sf.write(sgeCmd + "\n")
		sf.close()
		
		os.chmod(sgePath + "/sgeMaya.sh", 0755)
	
	# Dump the shell environment
	def writeEnvFile(sgePath):
		ef = open(sgePath + "/theEnv", "w")
		
		for param in os.environ.keys():
			if os.environ[param].find('*') == -1:
				ef.write("%s=%s\n" % (param,os.environ[param]))
		ef.close()
	
	# Get the list of cameras so we can choose which one to render
	def getCameras():
		print "Hello"
	
	# If it's been set, send a mail
	def jobExtraEMail(theJobID):
		# Do the gridextra command to add the output_path info
        	previewCmd = ("gridextra " + theJobID + " email yes")
	        os.system(previewCmd)
	
	# Run this if OK is pressed
	def ok(arg):
		print mc.optionMenu("rendererComboBox", q=True, v=True)
