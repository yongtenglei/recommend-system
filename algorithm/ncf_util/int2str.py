import json

uid_dict = json.load(open('/opt/shared/recommend/ncf/ranking_user.json',"r"))
mid_dict = json.load(open('/opt/shared/recommend/ncf/ranking_item.json',"r"))
user_string_list = list(uid_dict.keys())
item_string_list = list(mid_dict.keys())

file_path = "/opt/shared/recommend/ncf/testratings.dat"
open_file = open(file_path, "r")
out_file = open("str_test_file.dat", "w")
for line in open_file:
  arr = line.strip("\n").split("::")
  print(user_string_list[int(arr[0])]+ "::" + item_string_list[int(arr[1])],file = out_file)

test_file = open("testfile_str.dat","w")
print(''.join(sorted(open('str_test_file.dat'), key=lambda s: s.split()[0],reverse=0)),file = test_file)

