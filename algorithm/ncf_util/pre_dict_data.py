import json

def trans2Dirc(dir_data):
	open_file = open(dir_data, "r")
	uid_dict = {}
	mid_dict = {}
	for line in open_file:
		arr = line.strip("\n").split("\t") 
		uid = arr[0]
		mid = arr[1]
		if uid not in uid_dict:
			uid_dict[uid] = 0
		uid_dict[uid] += 1
		if mid not in mid_dict:
			mid_dict[mid] = 0
		mid_dict[mid] += 1

	uid_voc = {}
	index = 0
	for key, value in uid_dict.items():
		if value > 19:
			uid_voc[key] = index
			index += 1

	mid_voc = {}
	mid_voc["default_mid"] = 0
	index = 1
	for key, value in mid_dict.items():
		mid_voc[key] = index
		index += 1
	
	new_mid = {}
	index_new = 0

	open_file = open(dir_data, "r")
	for line in open_file:
		arr1 = line.strip("\n").split("\t")
		if arr1[0] in uid_voc and arr1[1] in mid_voc:
			if arr1[1] not in new_mid:
				new_mid[arr1[1]] = index_new
				index_new += 1

	with open("ranking_user.json","w") as f:
		json.dump(uid_voc,f)
	with open("ranking_item.json","w") as f:
		json.dump(new_mid,f)

if __name__ == '__main__':
	dir_data = 'out'
	trans2Dirc(dir_data)