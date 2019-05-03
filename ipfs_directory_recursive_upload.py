import requests
import simplejson as json
import os

def upload_file(file_path, server_details):
	status = True
	hash = None

	try:
		api_port = server_details["api_port"]
		
		entries = []
		
		path_tokens = file_path.split(os.path.sep)
		temp_tokens = path_tokens[:-1]
		outer_path = os.path.sep.join(temp_tokens)
	
		
		for path, dirs, files in os.walk(file_path):
			
			for f in files:
				#print(path)
				fp = os.path.join(path, f)
				#print(fp)
				t_path = fp.replace(outer_path,"")
				#print(t_path)
				entry = ("file",(t_path,(open(fp,"rb"))))
				
				entries.append(entry)
		
		params = {'recursive': "true","chunker":"size-262144","wrap-with-directory":"true"}
		
		r = requests.post("http://127.0.0.1:%s/api/v0/add" % api_port, params=params,files=entries)
		
		print(r.text.strip())
		
		
		
		if r.status_code == 200:
			dict = r.text.strip()
			
			string_tokens = dict.split("\n")
			
			last_string = string_tokens[-1]
			
			print(last_string)
			
			temp_dic = json.loads(last_string)
			
			hash = temp_dic['Hash']
			
			
		else:
			raise Exception("IPFA FILE UPLOAD FAILED")

	except Exception as err:
		print(err)
		status = False

	return (status, hash)



# UPLOAD FILE
print("UPLOAD FILE")

fqp = '/home/hperpo/go-ipfs'

server_details = {"api_port":5001}

status,hash = upload_file(fqp, server_details)

print(status)
print(hash)
