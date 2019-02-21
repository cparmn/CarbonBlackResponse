#!/usr/bin/env python3
'''
Carbon Black TAU - Casey Parman 2-20-19
Created to search for filemods of jar files that are identified as compound documents 
The MIT License (MIT)

Copyright (c) 2018 Carbon Black

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import re, csv, os, ntpath

try:
	from cbapi.response import *
except ImportError as error:
	exit('\033[1;31;40mUnable to import cbapi Please ensure its installed, more information can be found https://cbapi.readthedocs.io/en/latest/installation.html\033[0m')

def ask_user(file):
    '''
	Fuction to for asking users if they want to overwrite files

    Parameters
	``````````
	file : string
		Filename that already exist on the system

	Local Variable (attributes)
	``````````````	
    response : String
        Answer from the user 
	Global Variables
	````````````````
	Imports Required for Function
	`````````````````````````````
	'''

    response = ''
    while response.lower() not in {"yes", "no"}:
        response = input("Overwrite the file {}? Yes/No [Yes]:".format(file)) or "yes"
    return response.lower() == "yes"

def main():
	'''
	Main function of the program this is where all the magic happens. 

	Parameters
	``````````

	Local Variable (attributes)
	``````````````	
	I'm being lazy sometime i'll go back and document all these variables 

	Global Variables
	````````````````
	Imports Required for Function
	`````````````````````````````
	all the imports...
	'''

	cb = CbResponseAPI()
	while True:
		string = input("Please enter number of days to search or all:[All]") or "all"
		try:
			if string.lower() == 'all':
				days = string.lower()
				print("\033[1;31;40mWarning: Searching all event data can take extended periods of time\033[0m")
				break
			else:
				days = abs(int(string))
				break
		except ValueError:
			print("This was not a number, please try again.")
	if days != 'all':
		hours = str(int(days) * 24)
	FilewriteFilename =  input("Enter File name:[msijar.csv]") or "msijar.csv"
	if os.path.exists(FilewriteFilename):
		if ask_user(FilewriteFilename):
			print("Creating a csv file {}".format(FilewriteFilename))
		else:
			exit("File {} exist".format(FilewriteFilename))
	if days == 'all':
		Filequery = cb.select(Process).where("filemod:.jar")
	else:
		Filequery = cb.select(Process).where("filemod:.jar start:-"+hours+"h")
	with open(FilewriteFilename, 'w') as csvfile:
		FileModExport = csv.writer(csvfile, delimiter='@',
						quotechar='|', quoting=csv.QUOTE_MINIMAL)
		FileModExport.writerow(['Timestamp','WebURL','Process Name','Process PID','Process Unique ID',"Parent Process","Parent PID",'Parent Unique ID','Command Line','Username','Hostname','IP Address','File Path','File MD5','Number of Network Connections','Number of Child Processes'])
		for proc in Filequery:
			for filemod in proc.filemods:
				if re.match('^.*?\.jar$',filemod.path) is not None and filemod.filetype == 'DOC':
					FileModExport.writerow([filemod.timestamp,cb.url+'/#/analyze/'+str(re.match('[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}',proc.unique_id).group(0))+'/'+str(proc.segment_id),proc.process_name,proc.process_pid,proc.unique_id,proc.parent_name,proc.parent_pid,proc.parent_unique_id,proc.cmdline,proc.username,proc.hostname,proc.interface_ip,filemod.path,filemod.md5,proc.netconn_count,proc.childproc_count])
					if days == 'all':
						JarExecution = cb.select(Process).where("cmdline:"+ntpath.basename(filemod.path))
					else:
						JarExecution = cb.select(Process).where("cmdline:"+ntpath.basename(filemod.path)+" start:-"+hours+"h")
					for execute in JarExecution:
						FileModExport.writerow([filemod.timestamp,cb.url+'/#/analyze/'+str(re.match('[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}',execute.unique_id).group(0))+'/'+str(execute.segment_id),execute.process_name,execute.process_pid,execute.unique_id,execute.parent_name,execute.parent_pid,execute.parent_unique_id,execute.cmdline,execute.username,execute.hostname,execute.interface_ip,filemod.path,filemod.md5,execute.netconn_count,execute.childproc_count])

if __name__ == '__main__':
    main()
