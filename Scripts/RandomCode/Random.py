##Just Random Code that I've used over the past few years.

#This is Required for all of them.
from cbapi.response import *
cb = CbResponseAPI()



#What computers have connected to sharefile.com domain.

#Serching Domain
query = cb.select(Process).where("domain:sharefile.com")
for proc in query:
	for netconn in proc.netconns:
		if re.match('.*sharefile.com',netconn.domain) is not None:
			print netconn.timestamp,",",proc.process_name,",", proc.process_pid,",", proc.username,",", proc.hostname,",", proc.comms_ip,",", netconn.domain,",", netconn.remote_ip,",", netconn.direction

'''
output
2018-11-28 19:05:33.385000 , fsliteupdater.exe , 70968 , User , Hostname , 10.152.122.72 , irm.sharefile.com , 34.237.215.227 , Outbound

'''

#Searching Filemods

import re
Filequery = cb.select(Process).where("filemod:.doc")
for proc in Filequery:
	for filemod in proc.filemods:
		if re.match('^.*?\.doc$',filemod.path) is not None and re.match('^Deleted$',filemod.type) is None:
			"{}, {}, {}, {}, {}, {}, {}, {}".format(filemod.timestamp,proc.process_name,proc.process_pid,proc.username,proc.hostname,proc.comms_ip,filemod.path,filemod.type)


 
#All Sensors with IP Range

query = cb.select(Sensor).where("network_adapters:192.168.50.*")
for pc in query:
	print pc
	

#Searching Network Connections
userquery = cb.select(Process).where("start:[2017-11-07T00:00:00 TO 2017-11-08T00:00:00]")
for proc in userquery:
	for netconn in proc.netconns:
			if netconn.local_port == 23880 or netconn.local_port == 32528:
				print proc.start, proc.hostname, proc.interface_ip, proc.username, proc.process_name, proc.process_pid, proc.cmdline, netconn.remote_ip, netconn.local_port, netconn.direction

#Searching md5
query = cb.select(Process).where("md5:34C537DC70EC8650E23B7753F58877DF or md5:6859B739E8206294F86066E5CB0448B1")

