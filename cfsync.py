api_username="YOUR_USERNAME_HERE"
api_key="YOUR_KEY_HERE"
# https://auth.api.rackspacecloud.com/v1.0 for the US 
# https://lon.auth.api.rackspacecloud.com/v1.0 for the UK
auth_url="https://lon.auth.api.rackspacecloud.com/v1.0"
dest_container="backups"

#############
## DO NOT EDIT AFTER THIS LINE
##############
import cloudfiles
import sys,os
import hashlib
local_file_list = sys.stdin.readlines()

#Setup the connection
cf = cloudfiles.get_connection(api_username, api_key, authurl=auth_url)

#Get a list of containers
containers = cf.get_all_containers()

# Lets setup the container
for container in containers:
    if container.name == dest_container:
            backup_container = container

#Create the container if it does not exsit
try:
    backup_container
except NameError:
    backup_container = cf.create_container(dest_container)

# We've now got our container, lets get a file list
def build_remote_file_list(container):
    remote_file_list = container.list_objects_info()
    remotefiles = {}
    for remote_file in remote_file_list:
        remotefiles[remote_file['name']] = remote_file
    return remotefiles

remote_file_list = build_remote_file_list(backup_container)
#from pprint import pprint as pp
#pp(remote_file_list)


def upload_cf(local_file):
    u = backup_container.create_object(local_file)
    u.load_from_filename(local_file)

for local_file in local_file_list:
        local_file_hash = hashlib.md5()
        local_file = local_file.rstrip()
        local_file_hash.update(open(local_file,'rb').read())
        local_file_size = os.stat(local_file).st_size/1024
        #check to see if we're in remote_file_list
        try:
	    if len(remote_file_list[local_file]['name']) > 0:
                #has it been modified
                if remote_file_list[local_file]['last_modified'] < os.stat(local_file).st_mtime :
                    print "Remote file is older, uploading %s (%dK) " % (local_file, local_file_size)
                    upload_cf(local_file)
                #is the md5 different locally to remotly
                elif remote_file_list[local_file]['hash'] != local_file_hash.hexdigest():
                    print "Remote file hash %s does not match local %s, uploading %s (%dK)" % (remote_file_list[local_file]['hash'], local_file_has.hexdigest(), local_file, local_file_size)
                    upload_cf(local_file)
                else:
                    print "Remote file hash and date match, skipping %s" % (local_file)
            else:
	        # You shouldn't get here! but lets upload, just incase
		print "this shouldn't have happened!"
	        upload_cf(local_file)
        except KeyError:
                print "Remote file does not exist, uploading %s (%dK)" % (local_file, local_file_size)
                upload_cf(local_file)
