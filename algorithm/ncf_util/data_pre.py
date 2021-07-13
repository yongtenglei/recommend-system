import pickle
import numpy as np
import random
import sys
import os


file_review = open(sys.argv[1], "r")
user_map = {}
file_out = open("reviews-info", "w")
for line in file_review:
	obj = eval(line)
	userID = obj["reviewerID"]
	itemID = obj["asin"]
	print(userID + "\t" + itemID + "\t",file = file_out)

out = open("out","w")
print(''.join(sorted(open('reviews-info'), key=lambda s: s.split()[0],reverse=1)),file = out)

out_del = open("out","rb+")
out_del.seek(-1 ,os.SEEK_END)
if out_del.next() == "\n":
	out_del.seek(-1 ,os.SEEK_END)
	out_del.truncate()
out_del.close()


f_train = open("out", "r")
uid_dict = {}
mid_dict = {}

iddd = 0
for line in f_train:
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
for key, value in uid_dict.iteritems():
	if value > 19:
		uid_voc[key] = index
		index += 1

mid_voc = {}
mid_voc["default_mid"] = 0
index = 1
for key, value in mid_dict.iteritems():
	mid_voc[key] = index
	index += 1


out_file = open("ncf.train.rating","w")
file1 = open("out", "r")
file_new = open("new_mid","w")
new_mid = {}
index_new = 0
for line in file1:
	arr1 = line.strip("\n").split("\t")
	if arr1[0] in uid_voc and arr1[1] in mid_voc:
		if arr1[1] not in new_mid:
			new_mid[arr1[1]] = index_new
			index_new += 1

get_test_uid = {}
get_test_mid = {}

for key,value in uid_voc.iteritems():
	if key not in get_test_uid:
		get_test_uid[key] = 0
for key,value in new_mid.iteritems():    
	if key not in get_test_mid:
		get_test_mid[key] = 0

randomlist = []
for key,value in get_test_mid.iteritems():
	randomlist.append(key)

file_out = open("out", "r")

for line in file_out:
	count = 0
	getlist = []
	arr1 = line.strip("\n").split("\t")
	if arr1[0] in uid_voc and arr1[1] in mid_voc:
		if get_test_uid[arr1[0]] == 0:
			get_test_uid[arr1[0]] +=1
		else:
			print(str(uid_voc[arr1[0]])+ "\t" + str(new_mid[arr1[1]]),file = out_file)
     


out_train = open("ncf.train.rating_sort","w")
print(''.join(sorted(open('ncf.train.rating'), key=lambda s : int(s.split()[0]))),file=out_train)

train_del = open("ncf.train.rating_sort","rb+")
train_del.seek(-1 ,os.SEEK_END)
if train_del.next() == "\n":
	train_del.seek(-1 ,os.SEEK_END)
	train_del.truncate()
train_del.close()

open_file = open("ncf.train.rating_sort","r")
ratings = open("ratings.dat","w")
for line in open_file:
	arr = line.strip("\n").split("\t")
	print(str(int(arr[0])+1)+ "::" + str(arr[1]),file=ratings)