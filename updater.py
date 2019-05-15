import os
import requests
import simplejson as json

import psutil
import multiprocessing
from multiprocessing import Process, Semaphore
from threading import Thread
import time

from log_handler import *
from hash_creator import HashCreator

HASH_FILE = "file_sigs.dat"
IPNS_API = "http://ec2-52-32-143-69.us-west-2.compute.amazonaws.com:9000/ipfs/hash/latest"
#IPFS_REPO_BASE = "http://localhost:8080/ipfs"
IPFS_REPO_BASE = "http://ec2-52-32-143-69.us-west-2.compute.amazonaws.com:8080/ipfs"

#IPNS_REPO_ADD = "http://localhost:8080/ipns/QmUP9siChgPinuHkRrdihMDKNRJnXrxuLxTpnK9CmUWhVA"

# 1. retrieve latest ipfs hash from api
# 2. retrieve file signatures from remote repo using ipfs hash
# 3. compare retrieved file signatures with current signatures
# 4. identify deleted files, new files, modified files
# 5. delete deleted files
# 6. create necessary directories for new files and add new files
# 7. replace modified files

#rehashing comparison
# 1. rehash all the files every run of this updater

#Testing
APP_DIR = os.path.join(os.getcwd(),"test")
HASH_FILE_DIR = os.path.join(os.getcwd(),"test")

#APP_DIR = os.getcwd()
#HASH_FILE_DIR = os.getcwd()
EXCLUDE_DIRS = ["__pycache__"]
EXCLUDE_FILES = ["file_sigs.dat","updater.py","hash_creator.py","log_handler.py","updater.log","updater.exe"]
EXCLUDE_EXT = [".db"]

#hashing


#logging
log = get_logger("updater")

class EnvironmentMaster:
	
	def __init__(self,app_dir,ipfs_api,ipfs_repo, exclude_dirs,exclude_files, exclude_ext):
		self.app_dir = app_dir
		self.ipfs_api = ipfs_api
		self.ipfs_repo_base = ipfs_repo
		self.hash_creator = HashCreator(exclude_dirs,exclude_files, exclude_ext)
	
	def rehash(self):
		
		log.debug("REHASHING DOWNLOADED FILES")

		status = True
		try:
			hash_data = self.hash_creator.parse(self.app_dir)
			
			log.debug(json.dumps(hash_data,indent=2))
			
			log.debug("++++++++++++++++++++++++++++++++++++++++")
			
			with open(os.path.join(HASH_FILE_DIR, HASH_FILE),"w") as f:
				f.write(json.dumps(hash_data))
				
		except:
			status = False
			log.debug("Error in rehashing the downloaded files")
		
		return status
			
	def get_old_contents(self):
		
		status = self.rehash()
		
		if not status:
			self.rehash()
		
		old_contents = {} # { relative_path : file hash }
		
		log.debug("GETTING OLD CONTENTS")
		
			
				
		sig_file = os.path.join(self.app_dir,HASH_FILE)
		
		#log.debug(sig_file)
		
		if os.path.exists(sig_file):		
			with open(sig_file) as f:
				old_contents = json.loads(f.read())
			
		#log.debug(old_contents)
			
		return old_contents
		
	def get_new_contents(self,hash):
		
		new_contents = {} # { relative_path : file hash }
		
		log.debug("GETTING NEW CONTENTS")
		
		latest_hash_sig_url = "%s/%s/%s" %(self.ipfs_repo_base,hash,HASH_FILE)

		r = requests.get(latest_hash_sig_url,timeout=100)

		new_contents = json.loads(r.text)
		
		#log.debug(new_contents)
		
		return new_contents
		
	def download_file(self,file_path,url):

		with requests.get(url, stream=True) as r:
			with open(file_path, 'wb') as f:
				for chunk in r.iter_content(chunk_size=8192): 
					if chunk: # filter out keep-alive new chunks
						f.write(chunk)
						f.flush()
						
	def get_latest_hash(self):
		
		hash = None
		
		r = requests.get(self.ipfs_api)
		
		if r.status_code == 200:
			hash = r.text
			
		return hash
		
	def get_environment_status(self,old_contents,new_contents):
		
		deleted_files = []
		new_files = []
		modified_files = []		
		
		old_contents_files = set(old_contents.keys())
		new_contents_files = set(new_contents.keys())
		
		# identify deleted files 
		# some old files will not be found in the new environment	

		deleted_files = old_contents_files - new_contents_files
		deleted_files = list(deleted_files)

		# identify new files
		# some new files are not found in the old environment

		new_files = new_contents_files - old_contents_files
		new_files = list(new_files)

		# identify modified files
		# there are files found on both new and old that do not have the same signature

		common_files = old_contents_files  & new_contents_files
		
		for file in common_files:
			old_sig = old_contents[file]
			new_sig = new_contents[file]
			
			if old_sig != new_sig:
				modified_files.append(file)
				
		return deleted_files, new_files, modified_files
		
	def process_deleted_files(self, deleted_files):
		
		for f in deleted_files:
			
			fp = self.app_dir + f
			
			log.debug("DELETING FILE: %s" % fp)
			
			try:
				if os.path.exists(fp):
					os.remove(fp)
					log.debug("SUCCESS !")
				else:
					log.debug("PROCESS DELETED FILES ERROR : DOES NOT EXIST: %s" % fp)
			except:
				log.debug("PROCESS DELETED FILES ERROR: %s" % fp)
				
		
	def process_new_files(self, hash, new_files):
		
		def get_unique_directories(new_files,temp_path):
			
			directories = []
			
			for f in new_files:
				fp = os.path.join(temp_path,f)
				
				print(temp_path)
				print(f)
				
				last_ = fp[:fp.rfind(os.path.sep)]

				if last_ not in directories:
					directories.append(last_)
					
			return directories				
		
		#first extract unique dirs and create if necessary
		#get all files for a directory
		#parallel download files

		unique_dirs = get_unique_directories(new_files,self.app_dir)
		
		for dir in unique_dirs:
			if not os.path.isdir(dir):
				log.debug("DIRECTORY NOT FOUND. CREATING DIRECTORY %s" % dir)
				os.makedirs(dir)			
						
		worker_control = Semaphore(10)
		#worker_control = Semaphore(psutil.cpu_count())
		
		while  len(new_files) > 0:
			
			if worker_control.acquire(False):
				#launch download
				try:
					file_name = new_files.pop()
					w = DownloadWorker(self.ipfs_repo_base,self.app_dir,file_name,hash, worker_control)
					w.start()
				except:
					worker_control.release()
				
			time.sleep(0.10)
			
		
	def process_modified_files(self, hash, modified_files):
		
		def get_unique_directories(modified_files,temp_path):
			
			directories = []
			
			for f in modified_files:
				fp = os.path.join(temp_path,f)
				
				print(temp_path)
				print(f)
				
				last_ = fp[:fp.rfind(os.path.sep)]

				if last_ not in directories:
					directories.append(last_)
					
			return directories
		
		unique_dirs = get_unique_directories(modified_files, self.app_dir)
		
		for dir in unique_dirs:
			if not os.path.isdir(dir):
				log.debug("DIRECTORY NOT FOUND. CREATING DIRECTORY %s" % dir)
				os.makedirs(dir)			

		worker_control = Semaphore(10)
		#worker_control = Semaphore(psutil.cpu_count())
		
		while  len(modified_files) > 0:
			
			if worker_control.acquire(False):
				#launch download
				try:
					file_name = modified_files.pop()
					log.debug("UPDATING FILE: %s" % file_name)
					w = DownloadWorker(self.ipfs_repo_base,self.app_dir,file_name,hash, worker_control)
					w.start()
				except:
					worker_control.release()
				
			time.sleep(0.10)
				
	def update(self):
		latest_hash = self.get_latest_hash()
		
		if latest_hash:
			old_contents = self.get_old_contents()
			new_contents = self.get_new_contents(latest_hash)
			
			old_contents = self.hash_creator.transform_to_relative_file_hash_map(old_contents,"")
			new_contents = self.hash_creator.transform_to_relative_file_hash_map(new_contents,"")
				
			deleted_files, new_files, modified_files = self.get_environment_status(old_contents,new_contents)
			
			log.debug(">>> DELETED FILES")
			log.debug(deleted_files)
			log.debug(">>> NEW FILES")
			log.debug(new_files)
			log.debug(">>> MODIFIED FILES")
			log.debug(modified_files)
			log.debug("++++++++++++++++++++++++++++++++++++++++")
			
			self.process_deleted_files(deleted_files)
			self.process_new_files(latest_hash,new_files)

			
			self.process_modified_files(latest_hash,modified_files)
			
			# save latest signature
			sig_file_path = os.path.join(self.app_dir,HASH_FILE)
			latest_hash_sig_url = "%s/%s/%s" %(self.ipfs_repo_base,latest_hash,HASH_FILE)
			self.download_file(sig_file_path,latest_hash_sig_url)
			
		else:
			log.debug("UNABLE TO RETRIEVE LATEST ENVIRONMENT HASH")



class DownloadWorker(Thread):
	def __init__(self,repo_base,app_dir, file_name,hash,worker_control):
		Thread.__init__(self)
		self.repo_base = repo_base
		self.app_dir = app_dir
		self.file_name= file_name
		self.hash = hash
		self.worker_control = worker_control

	def download_file(self,file_path,url):
		print("%s - %s" %(file_path, url))
		with requests.get(url, stream=True) as r:
			with open(file_path, 'wb') as f:
				for chunk in r.iter_content(chunk_size=8192): 
					if chunk: # filter out keep-alive new chunks
						f.write(chunk)
						f.flush()
						
	def run(self):
		
		print("-- WORKER ONLINE : %s" % self.file_name)
		
		url = "%s/%s%s" % (self.repo_base, self.hash, self.file_name) 
		fp = os.path.join(self.app_dir,self.file_name)
		self.download_file(fp,url)
		self.worker_control.release()
		print("-- FINISHED")
			
		
		


		
if __name__ == "__main__":

	# APP_DIR or TARGET_DIR = use environment variable
	u = EnvironmentMaster(APP_DIR,IPNS_API,IPFS_REPO_BASE,EXCLUDE_DIRS,EXCLUDE_FILES, EXCLUDE_EXT)
	u.update()
	