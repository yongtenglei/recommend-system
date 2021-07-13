from ncfTF import NCF
import numpy as np
import pandas as pd
import tensorflow as tf
import os
import sys
import random
import json
import time


def mrr(gt_item, pred_items):
  if gt_item in pred_items:
    index = np.where(pred_items == gt_item)[0][0]
    return float(np.reciprocal(float(index + 1)))
  else:
    return 0
        
def hit(gt_item, pred_items):
  if gt_item in pred_items:
    return 1
  return 0


def ndcg(gt_item, pred_items):
  if gt_item in pred_items:
    index = np.where(pred_items == gt_item)[0][0]
    return float(np.reciprocal(np.log2(index + 2)))
  return 0


def prePreocess(testfile_path):
  open_file = open(testfile_path, "r")
  uid_dict, mid_dict = {}, {}
  user_item_list = []
  for line in open_file:
    arr = line.strip("\n").split("::")
    uid = arr[0]
    mid = arr[1]
    if uid not in uid_dict:
      uid_dict[uid] = 0
      temp = [uid,mid]
      user_item_list.append(temp)
      
  return user_item_list


def t_test(ncf, testfile_path):
  """
    HR 衡量召回率指标，举个简单的例子，
      三个用户在测试集中的商品个数分别是10，12，8，模型得到的top-10推荐列表中，分别有6个，5个，4个在测试集中
      那么此时HR的值是(6+5+4)/(10+12+8) = 0.5

    MRR 正确检索结果值在检索结果中的排名来评估检索系统的性能
      举个例子：假如检索三次的结果如下，需要的结果（cat，torus，virus）分别排在3,2,1的话，此系统地MRR为（1/3 + 1/2 + 1)/3 = 11/18


    NDCG 累积增益CG
      结果是要按照位置给一个折扣，此处是乘以一个1/log2i，来计
  """
  HR,MRR,NDCG = [],[],[]
  user_item_list = prePreocess(testfile_path)
  for i in range(len(user_item_list)):
    userid = user_item_list[i][0]
    itemid = user_item_list[i][1]
    print(userid,itemid)
    result = ncf.process(userid,itemid)
    HR.append(hit(itemid, np.array(result)))
    MRR.append(mrr(itemid, np.array(result)))
    NDCG.append(ndcg(itemid, np.array(result)))

    # top-5
    if i > 5:
      break
  
  return np.array(HR).mean(), np.array(MRR).mean(), np.array(NDCG).mean()


if __name__ == '__main__':
    
  testfile_path = '/opt/shared/recommend/ncf/str_test_file.dat'
  rating_path = '/opt/shared/recommend/ncf/ratings.dat'
  model_path = '/opt/shared/recommend/ncf/ncf.pb'
  user_dict_path = '/opt/shared/recommend/ncf/ranking_user.json'
  item_dict_path = '/opt/shared/recommend/ncf/ranking_item.json'

  ncf = NCF(rating_path, model_path, user_dict_path, item_dict_path)
  
  print("HR is %.3f, MRR is %.3f, NDCG is %.3f" % (t_test(ncf, testfile_path)))

