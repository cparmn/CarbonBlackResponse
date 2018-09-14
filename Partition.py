# -*- coding: utf-8 -*-
#!/usr/local/bin/python2.7

#API Partition Mounting/un-mounting Requires python 2.7  
#Side loaded Python 2.7 at /usr/local/bin/python2.7  
#Casey Parman
#9-6-2018
#Version 1.0 

#the goal of this script is to move WARM partitions to COLD and move the data to _cbevents (COLD Storage)

#Import All Requirements 
from cbapi.response import *
import os, re, logging, tarfile, glob, fnmatch, shutil, traceback, sys
from datetime import datetime,date,timedelta

#Define Warm Storage Location
WStorage = '/var/cb/data/solr5/cbevents'
#If currently free space is below this number in GB Warm Storage will be archived.
WSize = 500
#Define Cold Storage Location 
CStorage = '/var/cb/data/solr5/_cbevents'
#If currently free space is below this number in GB Cold Storage will be deleted 
CSize = 100


##Make Logrotate config it if doesn't exist.###

LogRotateFile='/etc/logrotate.d/partition'
if not os.path.isfile(LogRotateFile):
	f = open(LogRotateFile, "w")
	f.write("/var/log/partition/partition.log {\n\tmissingok\n\tnotifempty\n\tcompress\n\tdaily\n}\n")
	f.close()

##LOGGING###
LogFolder='/var/log/partition/'

if not os.path.exists(LogFolder):
	try:
		os.makedirs(LogFolder)
		logging.info("Folder {} Created".format(LogFolder))
	except Exception as error:
		logging.error("Unable to make Folder {}".format(LogFolder))


LFILE="partition.log"
LogFile=LogFolder + LFILE
logging.basicConfig(filename=LogFile,level=logging.INFO,format='%(asctime)s %(levelname)-8s %(message)s',datefmt='%a, %d %b %Y %H:%M:%S')
#Verify that Cold Storage and Warm Storage exist on the disk, if not exit with Warning log
if not os.path.exists(WStorage) or not os.path.exists(CStorage):
	logging.warning("One of the required folders does not exist or are not correctly defined. {} or {} ".format(WStorage, CStorage))
	sys.exit()

##########
#No Global Variable below here

'''
Functions

info 	: Function
	Queries Carbon Black API for partition information
	returns dictionary of partition information including
	storing date, directory, and size

tarball : function
	Creates compressed .tar.gz files & test results 

space 	:
	Get the space on disk of path specified 

hbytes	:
	Return the given bytes as a human readable string because we all cant convert
	bytes on the fly we will use this information later to see if the storage 
	is more then 200 GB Cold Storage needs to be more than 700 GB free. 

DeletePartition :
	Determine if there is enough free space on the server
	if storage is fine it will return '10' otherwise  it returns the directory

unmount_partiton :
	unmounts partition provided

Main 	:
	main Function of the script

'''

##Function to Gather Partition information. 

def info(status):
	'''
	Pulls Partition information with CB API to get both the oldest storage partition (cold or warm)

	Parameters
	``````````
	status : string = Warm Or Cold 
		The mounted status of the Carbon Black Partition.
		

	Local Variable (attributes)
	``````````````
	cb : object 
		CB Response REST API object 
	
	partition : class
		cb Response REST API class For storage Partitions 

	info : Unicode information
		Information from variable partition, including the following  
		sizeInBytes
		startDate
		partitionId
		endDate
		deletedDocs
		maxDoc
		userMounted
		isLegacy
		segmentCount
		numDocs
		dir
		schema

	spartition : dictionary
		Custom dictionary from cb response rest api class (partition) storing date, directory and size. 

	DATE : String
		Date associated with the partition.info. This is the key for spartition 

	Global Variables
	````````````````
	 None 

	Imports Required for Function
	`````````````````````````````
	from cbapi.response import *
	import re
	

	'''
	#Define CB API 
	cb = CbResponseAPI()
	#Create Empty Dictionary 
	spartition = {}
	for partition in cb.select(StoragePartition).where("status:"+status):
		for info in partition.info:
			if info == 'startDate':
				logging.debug(partition.name)
				DATE=re.search('^\d{4}-\d{2}-\d{2}',partition.info[info])
				logging.debug("Date: {}".format(DATE.group(0)))
				spartition[DATE.group(0)] = {} 
		for info in partition.info:
			if info == 'sizeInBytes':
				logging.debug("Partition Size: {}".format(partition.info[info]))
				spartition[DATE.group(0)]['size'] = partition.info[info]
			if info == 'dir':
				logging.debug("Directory ={}".format(partition.info[info]))
				spartition[DATE.group(0)]['name'] = partition.name
				spartition[DATE.group(0)]['dir'] = partition.info[info]
	return spartition


def tarball(archive_name,source_path):
	'''
	Creates compressed .tar.gz files & test results 

	Parameters
	``````````
	archive_name : String   | Example CStorage, + min(spartition),+".tar.gz"
		Full Path for tar.gz file

	source_path : String  | Example WStorage, + min(spartition)
		Full Path for contents that will be compressed in the Tarball.
		

	Local Variable (attributes)
	``````````````
	tar : object (file)
		Write-able Tar Object file that will be opened to add contents

	rtar : object (file)
		Read Existing Tar archive 

	file_name : string
		contents of source_path
	le : int
		Length of tarinfo.name 

	tarinfo : object
		A TarInfo object represents one member in a TarFile. Aside from storing all required 
		attributes of a file (like file type, size, time, permissions, owner etc.),
		it provides some useful methods to determine its type. It does not contain 
		the file’s data itself.

	matches : dictionary
		OS Walk output for uncompressed files to compare tarball
	match : individual objects from the matches dictionary 

	matches	: integer
		Number of files that match, to be logged and emailed.

	NumberOfMatches : Number of files that size match 

	NumberOfFiles 	:	Number of files in the archive
	
	Global Variables
	````````````````

	Imports Required for Function
	`````````````````````````````

	import tarfile
	import glob
	import os
	import fnmatch
	import re
	'''
	#Debug Information - 
	logging.debug("Compressing files to {0}".format(archive_name), exc_info=True)
	#Opens Tarfile
	tar = tarfile.open(archive_name, "w:gz")
	#Add All Items in source_path to tarfile
	for file_name in glob.glob(os.path.join(source_path, "*")):
		#Debug Information - 
	    logging.debug(" Adding {0} to {1}".format(file_name, archive_name))
	    tar.add(file_name, os.path.basename(file_name))
	 #Close Tarfile
	tar.close()
	#Compare contents of Tar file to Contents of the Directory. 
	#Read the contents 
	matches = []
	for root, dirnames, filenames in os.walk(source_path):
		for filename in fnmatch.filter(filenames, "*"):
			matches.append(os.path.join(root, filename))
	
	rtar = tarfile.open(archive_name, "r:gz")
	NumberOfFiles=0
	NumberOfMatches=0
	for tarinfo in rtar:
		if tarinfo.isfile() is True:
			for match in matches:
				if match.find(tarinfo.name) != -1:
					NumberOfFiles += 1
					logging.debug("{0} Full Path for Match".format(match))
					logging.debug("{0} Tarbar matched file".format(tarinfo.name))
					le=len(tarinfo.name)
					logging.debug("Length of filename = {}".format(le))
					regex='.{'+str(le)+'}$'
					logging.debug("Regex for matching files= {}".format(regex))
					f = re.search(regex ,match)
					logging.debug("Filename thats is being matched against = {}".format(f.group(0)))
					if f.group(0) == tarinfo.name:
						if os.path.getsize(match) == tarinfo.size:
							NumberOfMatches += 1
							logging.debug("{0} is the same as {1}".format(tarinfo.name, match))
						else:
							logging.debug("{0} and {1} and not the same".format(tarinfo.name, match))
	logging.info("Number of matches:{} and number of files:{}".format(NumberOfMatches,NumberOfFiles))
	rtar.close()
	if NumberOfMatches == NumberOfFiles:
		logging.info("Delete Folder: {}".format(source_path))
		try:
			shutil.rmtree(source_path)
		except Exception as error:
			logging.warning("Error deleting folder {} Error:{}".format(source_path, str(error)), exc_info=True)

def space(p):
	'''
	Get the space on disk of path specified 

	Parameters
	``````````
	p: string
		Path to search for disk space.

	Local Variable (attributes)
	``````````````
	
	s : postix.statvfs_results

		All Storage information for p 
		Example:
		posix.statvfs_result(f_bsize=4096, f_frsize=x, f_blocks=7259174, f_bfree=2507533, f_bavail=2507533, f_files=29050880, f_ffree=28823706, f_favail=28823706, f_flag=4096, f_namemax=255)

	
	
	Global Variables
	````````````````
	None

	Imports Required for Function
	``````````````````````````````
	import os

	'''
	s = os.statvfs(p)
	return s.f_frsize * s.f_bavail


def hbytes(B):
   '''
   Return the given bytes as a human readable string because we all cant convert
   bytes on the fly we will use this information later to see if the storage 
   is more then 200 GB Cold Storage needs to be more than 700 GB free. 

	Parameters
	``````````
	B : integer
		bytes to convert


	Local Variables
	```````````````
	KB : integer
		Bytes converted to Kilobytes

	MB : integer
		Bytes converted to Megabytes

	GB : integer
		Bytes converted to Gigabytes

	TB : integer
		Bytes converted to Terra-bytes


   '''
   B = float(B)
   KB = float(1024)
   MB = float(KB ** 2) 
   GB = float(KB ** 3) 
   TB = float(KB ** 4) 
   #
   if B < KB:
      return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
   elif KB <= B < MB:
      return '{0:.0f} KB'.format(B/KB)
   elif MB <= B < GB:
      return '{0:.0f} MB'.format(B/MB)
   elif GB <= B < TB:
      return '{0:.0f} GB'.format(B/GB)
   elif TB <= B:
      return '{0:.0f} TB'.format(B/TB)


def DeletePartition(storage, status):
	'''
	Determine if there is enough free space on the server
	if storage is fine it will return '10' otherwise  it returns the directory

	Parameters
	``````````
	storage : integer
		bytes to convert

	status :  list or dict 
		Warm Storage partition information (list) created from info() or Cold Storage Tarballs (dict)

	Local Variables
	```````````````
	KB : integer
		Bytes converted to Kilobytes	

	Global Variables
	````````````````
	WSize : Integer
		Size of Warm storage in GB before archive

	CSize : Integer
		Size of Cold Storage before deletion of oldest file.
	'''
	global WSize
	global CSize

	if re.search('.{2}$',hbytes(storage)).group(0) == 'TB':
		#print "Size in TB"
		logging.info("Current Free Space: {size}TB. {place} will not be deleted.".format(size=re.sub(' TB$', '', hbytes(storage)), place=status[min(status)]['dir'] if type(status) == dict else min(status)))
		#print "DONT DELETE"
		return 10
	elif re.search('.{2}$',hbytes(storage)).group(0) == 'GB':
		logging.info("Current Free Space: {size}GB on {place}".format(size=re.sub(' GB$', '', hbytes(storage)),place=status[min(status)]['dir'] if type(status) == dict else min(status)))
		if type(status) == dict:
			if int(re.sub(' GB$', '', hbytes(storage))) >= WSize:
				logging.info("{}GB of free space, No files need to be removed".format(int(re.sub(' GB$', '', hbytes(storage)))))
				return 10
			else:
				logging.info("Only {}GB of Free space, files {} will being archived and deleted".format(int(re.sub(' GB$', '', hbytes(storage))),status[min(status)]['dir']))
				return status[min(status)]['dir']
		elif type(status) == list:
			if int(re.sub(' GB$', '', hbytes(storage))) >= CSize:
				logging.info("{}GB of free space, No files need to be removed".format(int(re.sub(' GB$', '', hbytes(storage)))))
				return 10
			else:
				logging.info("Only {}GB of free space, files {} will being archived and deleted".format(int(re.sub(' GB$', '', hbytes(storage))),storage_type(status,storage)))
				storage_type(status,storage)
	elif re.search('.{2}$',hbytes(storage)).group(0) == 'MB':
		#print "Size in MB"
		#print "Delete OLDEST"
		#return int(re.sub(' MB$', '', hbytes(storage)))
		logging.info("Only {}MB of free space, Files {} will being archived and deleted".format(int(re.sub(' GB$', '', hbytes(storage))),storage_type(status,storage)))
		storage_type(status,storage)
	elif re.search('.{2}$',hbytes(storage)).group(0) == 'KB':
		#print "Size in KB"
		#return int(re.sub(' MB$', '', hbytes(storage)))
		#print "Delete OLDEST"
		logging.info("Only {}KB of free space, Files {} will being archived and deleted".format(int(re.sub(' GB$', '', hbytes(storage))),storage_type(status,storage)))
		storage_type(status,storage)

def storage_type(stor_type,size):
	'''
	Checks if Warm or Cold Storage

	Local Variables
	```````````````
	stor_type :  list or dict 
		Warm Storage partition information (list) created from info() or Cold Storage Tarballs (dict)

	'''
	if type(stor_type) == dict:
		return stor_type[min(stor_type)]['dir']
	elif type(stor_type) == list:
		try:
			return min(stor_type)
		except:
			logging.error("Not enough space on drive without any archives to delete, current size available: {} ".format(hbytes(size)))
			sys.exit()
			return 30


def unmount_partition(partitions):
	'''
	unmounts partition provided
	Parameters
	``````````

	partitions : LIST
		List of Warm Storage partition information created from info()

	Local Variable (attributes)
	``````````````	

	cb :  API CB Response Object used for searching CBR via API.

	partition : CB Response API Object
	will be used to get the oldest partition


	Global Variables
	````````````````

	Imports Required for Function
	`````````````````````````````
	from cbapi.response import *  - lets be honest we dont need all of cbapi, but i'm being lazy.

	'''
	try:
		cb = CbResponseAPI()
		partition = cb.select(StoragePartition, partitions[min(partitions)]['name'])
		logging.info("Unmounting partition {}".format(partition.name))
		partition.unmount()
	except Exception as error:
		logging.error("Error unmounting partition {0}: {1}".format(partitions[min(partitions)]['name'], str(error)), exc_info=True)
		##EMAIL Error QUITE PRgoram###
	else:
		logging.info("Successfully unmounted partition {0}".format(partitions[min(partitions)]['name']))


def main():
	'''
	Main Function for the Program.

	Parameters
	``````````
	
	

	
	
	

	Local Variable (attributes)
	``````````````
	COLD : dictionary 
		Returned value from info function 

	COLD_SPACE : integer 
	
	OLD_COLD : 
	
	WARM :

	WARM_SPACE : 
	
	OLD_WARM : 
	
	DELETE_COLD	: string

	
	
	Global Variables
	````````````````
	WStorage
	CStorage

	Imports Required for Function
	`````````````````````````````
	import shutil
	import os

CStorage='/var/log/partition'

	'''
	##Define Global Variable 
	global WStorage
	global CStorage

	#Get Cold Storage Space
	COLD_SPACE=space(CStorage)
	#Get Oldest Cold Storage Partition
	COLD=os.listdir(CStorage)

	try:
		OLD_COLD=min(COLD)
	except Exception as error:
		logging.info("Unable to get oldest file from {}, {} likely empty ".format(CStorage, COLD), exc_info=True)

#Remove everything from the list that is not cbevents, because I dont want to remove them.
	for i in COLD:
		if re.match('^cbevents_',i) is None:
			COLD.remove(i)
#NOW COLD is only cbevents
#This is where we'll need to do it with the os instead of the partition API calls COLD=info('cold')
#This is where we'll need to do it with the os instead of the partition API calls OLD_COLD = min(COLD)
	#
	#Get Warm Storage Space
	WARM_SPACE=space(WStorage)
	#Get Oldest Warm Storage Partition
	WARM=info('warm')
	OLD_WARM = min(WARM)
	#If Warm Storage Space is less then 200 GB
	DELETE_WARM = "{}".format(DeletePartition(WARM_SPACE, WARM))
	if DELETE_WARM == '10':
		#If there is more than 300GB in Warm Storage we dont need to do anything.
		logging.info("More than 500GB free, Cleanup not required")
		sys.exit()
	else:
		DELETE_COLD = "{}".format(DeletePartition(COLD_SPACE, COLD))
		if DELETE_COLD == '10':
			logging.info("unmount partition {}".format(min(WARM)))
			unmount_partition(WARM)
			logging.info("Creating tarball from {}".format(WARM[OLD_WARM]['name']))
			tarball(CStorage+'/'+WARM[OLD_WARM]['name']+'.tar.gz',WARM[OLD_WARM]['dir'])
		else:
			logging.info("deleting the oldest cold partition {}".format(OLD_COLD))
			if os.path.isfile(CStorage+'/'+OLD_COLD):
				logging.info("deleted File {0}".format(OLD_COLD))
				os.remove(CStorage+'/'+OLD_COLD)
			logging.info("unmount partition {0}".format(WARM[min(WARM)]['dir']))
			unmount_partition(WARM)
			logging.info("Creating tarball from {}".format(WARM[OLD_WARM]['name']))
			tarball(CStorage+'/'+WARM[OLD_WARM]['name']+'.tar.gz',WARM[OLD_WARM]['dir'])


if __name__ == '__main__':
    main()
