from rankingTF import RankingTF
import numpy as np

def statisticConfusionMatrix(target_prob_pairs, threshold):
  P = 0.
  N = 0.
  TP = 0.
  FP = 0.
  TN = 0.
  FN = 0.
  for pair in target_prob_pairs:
    if pair[0] == '1':
      P += 1
      if pair[1] >= threshold:
        TP += 1
      else:
        FN += 1
    else:
      N += 1
      if pair[1] >= threshold:
        FP += 1
      else:
        TN += 1
  return  [P, N, TP, FP, TN, FN]

def calcPrecisionRecall(target_prob_pairs, threshold):
  P, N, TP, FP, TN, FN = statisticConfusionMatrix(target_prob_pairs, threshold)
  precision = TP / (TP + FP)
  recall = TP / (TP + FN)
  return [precision, recall]

def calcAccuracy(target_prob_pairs, threshold):
  P, N, TP, FP, TN, FN = statisticConfusionMatrix(target_prob_pairs, threshold)
  accuracy = (TP + TN) / (P + N)
  mean_accuracy = 0.5 * ((TP / P) + (TN / N))
  return [accuracy, mean_accuracy]

def calcAuc(target_prob_pairs):
  P, N = 0., 0.
  for pair in target_prob_pairs:
    if pair[0] == '1':
      P += 1
    else:
      N += 1
  sort_pairs = sorted(target_prob_pairs, key=lambda d:d[1], reverse=True)

  FP, TP = 0., 0.
  FPR, TPR = [], []
  for pair in sort_pairs:
    if pair[0] == '1':
      TP += 1.0
    else:
      FP += 1.0
    FPR.append(FP / N)
    TPR.append(TP / P)

  auc = 0.
  prev_x = 0.
  prev_y = 0.
  for x, y in zip(FPR, TPR):
    if x != prev_x:
      auc += ((x - prev_x) * (y + prev_y) / 2.)
      prev_x = x
      prev_y = y
  return auc

def tPerform(test_infer, test_file, his_max_len = 0):

  lines = []
  with open(test_file) as f:
    lines = f.readlines()

  samples = []
  for line in lines:
    #convert Amazon format to ours
    line = line.strip("\n").split("\t")
    converted_line = line[:4]

    his_mids = line[4].split("")
    his_cats = line[5].split("")
    his_mid_len = len(his_mids)
    his_cat_len = len(his_cats)
    his_infos = []
    if his_mid_len == 0 or his_cat_len == 0:
      continue
    elif his_mid_len < his_max_len:
      for i in range(his_max_len):
        i = i % his_mid_len
        his_infos.append((his_mids[i], his_cats[i]))
    elif his_mid_len >= his_max_len:
      for i in range(his_max_len):
        his_infos.append((his_mids[i], his_cats[i]))
    converted_line.append(his_infos)
    samples.append(converted_line)

  #infer 
  samples = np.array(samples)
  samples_len = len(samples)
  batch_size = 100
  batch_count = samples_len / batch_size
  batch_start = 0
  batch_end = 1
  prob = np.zeros(shape=(samples_len, 1))

  while batch_start < batch_count:
    temp_prob = test_infer.process(samples[batch_start * batch_size : batch_end * batch_size, 1:]) #samples[][0] : target
    temp_prob = np.array(temp_prob).reshape(len(temp_prob), 1)
    prob[batch_start * batch_size : batch_end * batch_size] = temp_prob
    batch_start += 1
    batch_end += 1

  if samples_len % batch_size != 0:
    temp_prob = test_infer.process(samples[batch_start * batch_size : samples_len, 1:])
    temp_prob = np.array(temp_prob).reshape(len(temp_prob), 1)
    prob[batch_start * batch_size : samples_len] = temp_prob[:]

  target = np.array(samples[:,0]).reshape(samples_len, 1)
  target_prob_pairs = np.concatenate((target, prob), axis=1)

  #calculate model performance
  #1.accuracy & mean accuracy
  accuracy, mean_accuracy = calcAccuracy(target_prob_pairs, 0.5)
  #2.precision & recall
  precision, recall = calcPrecisionRecall(target_prob_pairs, 0.5)
  #3.AUC
  auc = calcAuc(target_prob_pairs)
 
  return [accuracy, mean_accuracy, precision, recall, auc]

if __name__ == "__main__":

  model_name = "DIEN"  #DIEN / WIDE
  pb_path = "/opt/shared/recommend/DIEN.pb"
  uid_voc = "/opt/shared/recommend/uid_voc.json"
  mid_voc = "/opt/shared/recommend/mid_voc.json"
  cat_voc = "/opt/shared/recommend/cat_voc.json"
  test_file = "/opt/shared/recommend/local_test_splitByUser_250000"

  #init
  ranking = RankingTF(model_name, pb_path, uid_voc, mid_voc, cat_voc)
  accuracy, mean_accuracy, precision, recall, auc = tPerform(ranking, test_file, his_max_len = 5)
  print('\n accuracy: %.4f  mean_accuracy: %.4f\n precision: %.4f  recall: %.4f \n auc: %.4f\n' \
        %(accuracy, mean_accuracy, precision, recall , auc))

