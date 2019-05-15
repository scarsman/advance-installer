import hashlib
import os
import simplejson as json

BLOCKSIZE = 65536

class HashCreator:
	
	def __init__(self, exclude_dirs,exclude_files,exclude_ext):
		self.exclude_dirs = exclude_dirs
		self.exclude_files = exclude_files
		self.exclude_ext = exclude_ext
		
	def get_file_hash(self, file_path):
		
		hasher = hashlib.sha1()
		with open(file_path, 'rb') as afile:
			buf = afile.read(BLOCKSIZE)
			while len(buf) > 0:
				hasher.update(buf)
				buf = afile.read(BLOCKSIZE)
				
		return hasher.hexdigest()
			
	def parse(self, path):
		
		data = {}
		
		files = []
		dirs = []
		files_data = []
		dirs_data = []
		
		for x in os.listdir(path):
			fp = os.path.join(path,x)
			
			print(fp)
			
			if os.path.isdir(fp):
				
				if x not in self.exclude_dirs:
					dirs.append(fp)
				
			else:
				if x in self.exclude_files:
					continue
				
				ext = x[x.rfind("."):]
				
				if ext not in self.exclude_ext:
					files.append(fp)
			
		for f in files:	
			
			file_name = os.path.basename(f)
			hash = self.get_file_hash(f)
			f_data = {}
			f_data[file_name] = hash
			files_data.append(f_data)
				
		for dir in dirs:
			dir_name = os.path.basename(dir)
			result = self.parse(dir)
			dir_data = {}		
			dir_data[dir_name] = result
			dirs_data.append(dir_data)
			
				
		data["FILES"] = files_data
		data["DIRS"] = dirs_data
		
		return data
		

	def transform_to_relative_file_hash_map(self, hash,path):
		
		map = {}
		
		files = hash["FILES"]
		dirs = hash["DIRS"]
		
		for f in files:
			fn = list(f.keys())[0]
			fp = os.path.join(path,fn)
			map[fp] = f[fn]
			
		for 	d in dirs:
			dn = list(d.keys())[0]
			temp_path = os.path.join(path,dn)
			data = d[dn]
			temp_map = self.transform_to_relative_file_hash_map(data,temp_path)
			map.update(temp_map)	
			
		return map

if __name__ == "__main__":

	TARGET_DIR = "C:\\Users\\Administrator\\Desktop\\scl-scripts\\scl-app\\scl-installer"
	HASH_FILE_DIR = "C:\\Users\\Administrator\\Desktop\\scl-scripts\\scl-app\\scl-installer"
	HASH_FILE = "file_sigs.dat"
	EXCLUDE_DIRS = ["__pycache__"]
	EXCLUDE_FILES = ["file_sigs.dat","updater.log"]
	EXCLUDE_EXT = [".db",".pyc",".gitignore",".git"]

	d = HashCreator(EXCLUDE_DIRS, EXCLUDE_FILES,EXCLUDE_EXT)
	
	print(">>> CREATING HASH FILE")
	
	hash_data = d.parse(TARGET_DIR)

	print(json.dumps(hash_data,indent=2))
	
	with open(os.path.join(HASH_FILE_DIR, HASH_FILE),"w") as f:
		f.write(json.dumps(hash_data))
	
	print(">>> DONE")