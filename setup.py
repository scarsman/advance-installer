import setuptools
import os
from setuptools import setup
from setuptools.extension import Extension
from setuptools.command.build_ext import build_ext

target_dir = "E:\\advance-installer\\scl-app\\backend"
ignore_dirs = ["__pycache__","_Archive","Archive","vagrant","venv","scl_client_server_com","Tests"]
ignore_files = ["__init__.py"]

def get_setup_package_config(start_dir_path,ignore_dirs,ignore_files):
	
	def is_to_be_ignored(path,ignore_list):
		
		is_ignore = False
		
		for ignore_item in ignore_list:
			if path.find(ignore_item) > -1:
				is_ignore = True
				break
			
		return is_ignore
	
	results = []
	
	start_dir_path_dirs = start_dir_path.split(os.path.sep)
	prev_dir_path = os.path.sep.join(start_dir_path_dirs[:-1])
	#print prev_dir_path
	start_dir = start_dir_path.split(os.path.sep)[-1]
	
	#print(start_dir)

	for path, dirs, files in os.walk(start_dir_path):
		
		print ("==================")
		
		print ("DIR : %s" % path)
		
		dir_name = os.path.split(path)[1]
		
		if not is_to_be_ignored(path,ignore_dirs):
		
			is_python_file_detected = False
			
			#check if python file exists
			for f in files:
				if f[-3:] == ".py":
					is_python_file_detected = True
					break
			
			# check if __init__.py exists
			if is_python_file_detected:
				print("PYTHON FILES DETECTED")
				
				if "__init__.py" in files:
					print ("__init__.py found...ok")
				else:
					print ("__init__.py found...not ok")
			else:
				print ("NO PYTHON FILES DETECTED")
				
			# create setup configuration	
			
			if is_python_file_detected:
				for f in files:
					
					if f[-3:] == ".py":
						
						# construct full file path
						full_file_path = os.path.join(path,f)
						#print full_file_path
						
						if is_to_be_ignored(full_file_path,ignore_files):
							print("ignore: %s" % full_file_path)
							continue
						else:	
							print("adding: %s" % full_file_path)
							
						# construct the package structure
						
						tmp_path = path.replace(prev_dir_path,"")
						relevant_packages = tmp_path.split(os.path.sep)[1:]
							
						#print relevant_packages
						
						if len(relevant_packages) > 0:
						
							# get package from filename
							
							package_name = f.split(".")[0]
							
							relevant_packages.append(package_name)
							
							package_structure = ".".join(relevant_packages)
							package_path = os.path.sep.join(relevant_packages) + ".py"
														
							#print((package_structure,package_path))
							
							results.append((package_structure,package_path))
		else:
			print("IGNORING")
	
	return results
	
	
	
if __name__ == "__main__":

	modules = []

	"""
	modules = [
	    Extension("acme.foo", sources=["acme/foo.py"]),
	    Extension("acme.bar", sources=["acme/bar.py"]),
	    Extension("acme.pkg1.foo", sources=["acme/pkg1/foo.py"]),
	    Extension("acme.pkg1.bar", sources=["acme/pkg1/bar.py"]),
	]
	"""
	print("> parsing directory ...")
	package_info = get_setup_package_config(target_dir,ignore_dirs,ignore_files)
	
	print("----------------------------")	

	for info in package_info:
		
		package_structure, filename = info
		
		entry = Extension(package_structure, sources=[filename])
		
		print(info)

		modules.append(entry)


	setup(
	    name = 'XXXX',
	    cmdclass = {'build_ext': build_ext},
	    packages = setuptools.find_packages(),
	    ext_modules = modules
	)

#run as to execute
#python setup.py build_ext -b new-app	
