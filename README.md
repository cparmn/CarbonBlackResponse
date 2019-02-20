# Carbon Black Response Scripts
Scripts created and used with Carbon Black Response

## Scripts
**Partition.py**
Manages Carbon Black Response Warm partitions and cold (archive) storage

Goals:
1. Separate storage location for achieved
2. Compression of archived files
3. Manage
4. Logging to File-system
5. Log rotation creation


Requirements:
1. Side loading Python 2.7 on Carbon Black Response Server
2. Installing Carbon Black  API (cbapi) on Carbon Black Server
3. Updating variables for storage location (see below)

Before running this script please ensure the following variables are configured for your network, this script is meant to run as a cronjob, so it does not take any parameters 



WStorage (String)  This is the location of warm storage.
WSize (Integer)    If free space is below this number in GB Warm Storage will be archived.
CStorage (String) This is the location for archived events
CSize (Integer) If free space is below this  number in GB oldest archived file will be deleted.

Example:
```python
#Define Warm Storage Location
WStorage = '/var/cb/data/solr5/cbevents'
#If currently free space is below this number in GB Warm Storage will be archived.
WSize = 500
#Define Cold Storage Location 
CStorage = '/var/cb/data/solr5/_cbevents'
#If currently free space is below this number in GB Cold Storage will be deleted 
CSize = 100
```


**msijar.py**

Requirements:
1. Installing Carbon Black API (cbapi) on Carbon Black Server

This script finds the filemods of MSI files with jar extensions and then look for any execution with this method with the file name.  The CSV output is delimited via @ 
```
python msijar.py 
Please enter number of days to search or all:[All]60 
Enter File name:[msijar.csv]msijar.csv 
Overwrite the file msijar.csv? Yes/No [Yes]: 
Creating a csv file msijar.csv
```
```
cat msijar.csv 
Timestamp@WebURL@Process Name@Process PID@Process Unique ID@Parent Process@Parent PID@Parent Unique ID@Command Line@Username@Hostname@IP Address@File Path@File MD5@Number of Network Connections@Number of Child Processes
2019-01-17 21:02:29.631000@https://ServerName.com/#/analyze/000000175-7777-1774-9999-999999-00000/7623@explorer.exe@6004@00000175-7777-1774-9999-999999-00000@userinit.exe@5932@00000175-0001@C:\Windows\Explorer.EXE@computername\username@ccomputername@0.0.0.0@c:\users\tbrady\desktop\malware.jar@d07fa3f1ace1936e3f7@0@4
2019-01-17 21:02:29.631000@https://ServerName.com/#/analyze/00992/84@javaw.exe@4336@000-0000-10f0-01d4-a999888-27823604825763@explorer.exe@6004@0000-0000-10f0-01d4-a999888-27823604825763@"C:\Program Files\Java\jre1.8.0_191\bin\javaw.exe" -jar "C:\Users\Username\Desktop\Malware.jar" @Hostname\Username@hostname@0.0.0.0@c:\users\username\desktop\malware.jar@d07fa3f1ace1936e3f7@0@6
```


