import os
from subprocess import Popen, PIPE
import subprocess
import simplejson as json
import platform
import shlex

IPFS_CONFIG_FILE = "config"

class IPFSServer:
	
	def __init__(self, param_dir, param_swarm_port, param_api_port, param_gateway_port, is_private):
		
		self.target_dir = param_dir
		self.swarm_port = param_swarm_port
		self.api_port = param_api_port
		self.gateway_port = param_gateway_port
		self.is_private = is_private
		
	def launch(self):
		
		env_vars = os.environ.copy()
		env_vars["IPFS_PATH"] = self.target_dir
		
		# init the repo
		
		config_file = os.path.join(self.target_dir,IPFS_CONFIG_FILE)
		
		if not os.path.exists(config_file):
			
			print("INITIALIZING IPFS REPO: %s" % self.target_dir)			
			ipfs = os.path.join(os.getcwd(),"ipfs","ipfs.exe")
			cmd = "%s init" %ipfs
			cmd_tokens = cmd.split(" ")
			shell = Popen(cmd_tokens, cwd=self.target_dir, env=env_vars, stdin=PIPE, stdout=PIPE,stderr=PIPE)
			shell.communicate()
			
		# reconfigure the configuration
		
		config_data = {}
		
		with open(config_file) as f:
			config_data = json.loads(f.read())
			
		swarm_addresses = config_data["Addresses"]["Swarm"]
		api_address = config_data["Addresses"]["API"]
		gateway_address = config_data["Addresses"]["Gateway"]
		
		
		# modify swarm_addresses
		swarm_port = swarm_addresses[0].split("/")[-1]
		modified_swarm_addresses = []
		for sa in swarm_addresses:
			temp_sa = sa.replace(swarm_port,str(self.swarm_port))
			modified_swarm_addresses.append(temp_sa)
		
		config_data["Addresses"]["Swarm"] = modified_swarm_addresses

		# modify api_address		
		api_port = api_address.split("/")[-1]
		api_address = api_address.replace(api_port,str(self.api_port))
		
		config_data["Addresses"]["API"] = api_address
		
		# modify api_address		
		gateway_port = gateway_address.split("/")[-1]
		gateway_address = gateway_address.replace(gateway_port,str(self.gateway_port))
		
		config_data["Addresses"]["Gateway"] = gateway_address
		
		
		config_data["API"]["HTTPHeaders"]["Access-Control-Allow-Credentials"] = ["true"]
		config_data["API"]["HTTPHeaders"]["Access-Control-Allow-Methods"] = ["PUT", "GET", "POST"]
		config_data["API"]["HTTPHeaders"]["Access-Control-Allow-Origin"] = []
		config_data["API"]["HTTPHeaders"]["Access-Control-Allow-Origin"].append("http://127.0.0.1:%s" % self.api_port)
		config_data["API"]["HTTPHeaders"]["Access-Control-Allow-Origin"].append("https://webui.ipfs.io")
	
		# modify bootstrap list
		if self.is_private:
			pass
			#config_data["Bootstrap"] = []			
		
		with open(config_file,"w") as f:
			config_str = json.dumps(config_data)
			f.write(config_str)
		
		# launch the ipfs server		
		operating_system = platform.system()
		
		if operating_system == "Windows":
			print("WINDOWS DETECTED")
			si = subprocess.STARTUPINFO()
			si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
			ipfs = os.path.join(os.getcwd(),"ipfs","ipfs.exe")
			cmd = "%s daemon" %ipfs
			cmd_tokens = cmd.split(" ")
			pid = Popen(cmd_tokens, cwd=self.target_dir, env=env_vars, startupinfo=si, stdin=PIPE, stdout=PIPE, stderr=PIPE)
			
		elif operating_system == "Linux":
			print("LINUX DETECTED")
			cmd = "ipfs.exe daemon" 
			cmd_tokens = cmd.split(" ")
			pid = Popen(cmd_tokens, cwd=self.target_dir, env=env_vars).pid
		else:
			pass
			
if __name__ == "__main__":
	
	tmp_dir = os.path.join(os.environ['LOCALAPPDATA'],"testipfs")
	#tmp_dir = "C:\\Users\\Administrator\\AppData\\Local\\testipfs"
	
	i = IPFSServer(tmp_dir, 4007, 5007, 8087, True)
	i.launch()
	
