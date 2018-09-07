# CarbonBlackResponse
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
2. Installing Carbon Black Response API (cbapi) on Carbon Black Server
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

Todo
 1. Update with Crontab information

