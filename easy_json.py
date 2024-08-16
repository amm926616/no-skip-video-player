import json 

# open file, read value, edit value and close the file. I can't write these steps again and again. So, I create easy_json for it

def edit_value(key, value, file_path):
	# take key of value which needs to be updated
	with open(file_path, 'r') as f:
		data = json.load(f)
	data[key] = value
	with open(file_path, 'w') as f:
		json.dump(data, f)

def get_value(key, file_path):
	# give it a key, it will return the value
	with open(file_path, 'r') as f:
		data = json.load(f)
	return data[key]