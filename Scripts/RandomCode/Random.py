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


smtp = open('/root/smtp.txt','w') 
query = cb.select(Process).where("ipport:25 and -hostname:hostname -hostname:hostname -hostname:hostname start:-1440m")
smtp.write('TimeStamp, Process Name, Process Hash,Process PID, Username, Hostname, Host IP Address, Local Port, Remote Domain, Remote IP, Remote Port, Direction,cmdline\n')
for proc in query:
	for netconn in proc.netconns:
		if (proc.hostname != netconn.domain):
			if (proc.comms_ip != netconn.remote_ip):
				smtp.write('{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(netconn.timestamp,proc.process_name,proc.process_md5, proc.process_pid, proc.username, proc.hostname, proc.comms_ip,netconn.local_port, netconn.domain, netconn.remote_ip, netconn.remote_port, netconn.direction,proc.cmdline))
smtp.close()



from cbapi.response import *
cb = CbResponseAPI()
query = cb.select(Process).where("sensor_id:4029")
for proc in query:
	if (str(proc.process_pid) == '9708'):
		print('{},{},{},{},{},{}'.format(proc.start,proc.username,proc.process_name,proc.process_pid,proc.cmdline,proc.parent_pid))




from cbapi.response import *
cb = CbResponseAPI()
query = cb.select(Process).where("internal_name:cmd -process_name:cmd.exe AND -md5:742d854c5880c3c20a991b5a15160dd7 AND -md5:6fd5ee95e24596ceab0d0fcc47036290 hostname:hdopswkstn")
for proc in query:
	print ('Parent Process:{0} Spawned Process:{2} at {5} on Host:{1} With the User Account:{4} and command line:{3}\n'.format(proc.parent_name,proc.hostname,proc.process_name,proc.cmdline,proc.username,proc.start))





from cbapi.response import *
cb = CbResponseAPI()
query = cb.select(Process).where("internal_name:toolbox-cmd hostname:hostname process_name:cmd.exe parent_name:wmiprvse.exe cmdline:vmware")
for proc in query:
	SearchQuery= 'process_name:{0} childproc_name:{1} hostname:{2}'.format(proc.parent_name,proc.process_name,proc.hostname)
	queryParent = cb.select(Process).where(SearchQuery)
	for parentProc in queryParent:
		if parentProc.id == proc.parent_id:
			Parent=parentProc.process_name
			while Parent != 'svchost.exe':
				ParentSearchQuery= 'process_name:{0} childproc_name:{1} hostname:{2}'.format(parentProc.parent_name,parentProc.process_name,parentProc.hostname)
				queryParentParent = cb.select(Process).where(ParentSearchQuery)
				for ParentParentProc in queryParentParent:
					if ParentParentProc.id == parentProc.parent_id:
						print ParentParentProc.process_name, ParentParentProc.process_pid
						Parent=ParentParentProc.process_name

			print parentProc.start, parentProc.process_name, parentProc.process_pid,parentProc.cmdline,parentProc.netconn_count 
			for netconn in parentProc.netconns:
				print parentProc.start, parentProc.process_name, parentProc.process_pid,parentProc.cmdline, netconn.local_port, netconn.domain, netconn.remote_ip, netconn.remote_port, netconn.direction


				
				
~~~~~~~
##Parent Process Seaching

from cbapi.response import *
cb = CbResponseAPI()

def proc_callback(parent_proc, depth):
	if depth == 0:
	    print('Depth:{0}>>Process Name:{1}\t Parent Process Name:{2}\n'.format(depth, proc.process_name,parent_proc.process_name)) 
	else:
		print ('Depth:{0}>Parent Process Name:{1}\t CommandLine:{2}\n'.format(depth,parent_proc.process_name,parent_proc.cmdline,parent_proc.net)) 



query = cb.select(Process).where('internal_name:toolbox-cmd hostname:hdopswkstn process_name:cmd.exe parent_name:wmiprvse.exe cmdline:vmware')
for proc in query:
	proc.walk_parents(proc_callback, max_depth=5)

process_obj = cb.select(Process).where('process_name:svchost.exe')[0]
print (process_obj.sensor.computer_dns_name)



####
~~~~~





from cbapi.response import *
cb = CbResponseAPI()
computers=set([])
usernames=set([])
query = cb.select(Process).where("process_name:regasm.exe and cmdline:Office_Rules.tmp")
for proc in query:
	computers.add(proc.hostname)
	usernames.add(proc.username)
	
	
from cbapi.response import *
cb = CbResponseAPI()
query = cb.select(Process).where("process_name:mshta.exe and cmdline:HR_Complaint*")
for proc in query:
	print proc.parent_md5




