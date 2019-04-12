from modulefinder import ModuleFinder
import os
import ast
from collections import namedtuple

target_dir = "/home/hperpo/PROJECTS/scl/repo/scl-winapp/scl_backend"
ignore_dirs = ["__pycache__","__Archive","Archive","venv","vagrant"]
ignore_files = ["__init__.py"]

Import = namedtuple("Import", ["module", "name", "alias"])

def get_modules(start_dir_path,ignore_dirs,ignore_files):
	
	def get_imports(path):
		with open(path) as fh:        
			root = ast.parse(fh.read(), path)

		for node in ast.iter_child_nodes(root):
			if isinstance(node, ast.Import):
				module = []
			elif isinstance(node, ast.ImportFrom):  
				module = node.module.split('.')
			else:
				continue

			for n in node.names:
				yield Import(module, n.name.split('.'), n.asname)
			
	def is_to_be_ignored(path,ignore_list):
		
		is_ignore = False
		
		for ignore_item in ignore_list:
			if path.find(ignore_item) > -1:
				is_ignore = True
				break
			
		return is_ignore
	
	results = []
	
	finder = ModuleFinder()
	
	for path, dirs, files in os.walk(start_dir_path):
		
		print ("==================")
		
		print ("DIR : %s" % path)
		
		if not is_to_be_ignored(path,ignore_dirs):
			
			for f in files:
				
				if f[-3:] == ".py" :
					
					# construct full file path
					full_file_path = os.path.join(path,f)
					
					if is_to_be_ignored(full_file_path,ignore_files):
						continue
						
					print(full_file_path)
					
					for r in get_imports(full_file_path):
						print(r)
						
						str_module = ".".join(r.module)
						str_name = r.name[0]
						
						entry = ""
						
						if str_module != '':
							entry = str_module
						else:
							entry = str_name
						
						if entry not in results:
							results.append(entry)
						
	results.sort()
	
	return results

if __name__ == "__main__":
	
	modules = get_modules(target_dir,ignore_dirs,ignore_files)
	
	print("==================================")
	
	for m in modules:
		print(m)
