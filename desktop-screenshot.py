#!/usr/bin/python


from subprocess import Popen, PIPE
from os import getcwd,path
from time import sleep, localtime, strftime,time
from sys import exit

try:
	import Image      # necessary for manipulation with images
except:
	print "Warning: Failed to load Image module!"
	print "PIL / Python Image Library should be available in repositories"
	print "of your distribution, please install it."
	exit()

# DIRECTORY TO STORE SCREENSHOTS
wdir=getcwd()
store_dir=wdir+"/scrndir/" 

#output formats
output_format="jpg" #script is not ready for other formats by now
jpg_quality=int(50)

# length of period (in seconds) between screenshots
# keep in mind that processing itself takes some negligible time too
period=int(60)


if not path.isdir(store_dir):
	print "Warning: Directory", store_dir, "doesn't exist. Quitting...."
	exit()


while True:
	
	#doing screenshot and converting it to bmp for further processing
	doScrn = Popen("xwd -root | convert xwd:- scrn.bmp"\
	,shell=True,stdout=PIPE,stderr=PIPE)
	doScrn.wait()

	# generating filename
	now = localtime(time())
	filename =str(strftime("%y-%m-%d_%H:%M:%S", now)+"."+output_format)
	
    print "Saving as:", filename
	
	# processing tmp screenshot image and saving final screenshot
	sleep(0.5) #just to relieve CPU
	scrn_raw = Image.open("scrn.bmp")
	scrn_raw.save(store_dir+filename,quality=jpg_quality)
	
	sleep(period)
