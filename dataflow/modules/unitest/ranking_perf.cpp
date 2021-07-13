/*************************************************************************
 * Copyright (C) [2020] by Cambricon, Inc. All rights reserved
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 * OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 *************************************************************************/
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <algorithm>
#include <assert.h>
#include "ranking.hpp"

struct ConfusionMatrix {
  float P = 0;
  float N = 0;
  float TP = 0;
  float FP = 0;
  float TN = 0;
  float FN = 0;
};

ConfusionMatrix StatistiConfusionMatrix(std::vector<std::pair<int, float>> &target_prob_pairs, float threshold = 0.5) {  
  ConfusionMatrix confus_mat;
  for (auto &pair : target_prob_pairs) {
    if (pair.first == 1) {
      ++confus_mat.P;
      if (pair.second >= threshold) {
        ++confus_mat.TP;
      } else {
        ++confus_mat.FN;
      }
    } else {
      ++confus_mat.N;
      if (pair.second >= threshold) {
        ++confus_mat.FP;
      } else {
        ++confus_mat.TN;
      }
    }
  }
  return confus_mat;
}

std::pair<float, float> CalcAccuracy(const ConfusionMatrix& confus_mat) {
  std::pair<float, float> accuarcy_pair;
  float accuracy = (confus_mat.TP + confus_mat.TN) / (confus_mat.N + confus_mat.P);
  float mean_accuracy = 0.5 * ((confus_mat.TP / confus_mat.P) + (confus_mat.TN / confus_mat.N));
  accuarcy_pair.first = accuracy;
  accuarcy_pair.second = mean_accuracy;
  return accuarcy_pair;
}

std::pair<float, float> CalcPrecisionRecall(const ConfusionMatrix& confus_mat) {
  std::pair<float, float> precision_recall_pair;
  float precision = confus_mat.TP / (confus_mat.TP + confus_mat.FP);
  float recall = confus_mat.TP / (confus_mat.TP + confus_mat.FN);
  precision_recall_pair.first = precision;
  precision_recall_pair.second = recall;
  return precision_recall_pair;
}


bool PairCompare(std::pair<int, float>& pair1,std::pair<int, float>& pair2) { 
  return (pair1.second > pair2.second); 
}

float CalcAUC(std::vector<std::pair<int, float>>& target_prob_pairs, ConfusionMatrix& confus_mat){
  
  //from large to small
  std::vector<std::pair<int, float>> &sort_pairs = target_prob_pairs;
  std::sort(sort_pairs.begin(), sort_pairs.end(), PairCompare);

  //static ROC curve and comput AUC
  float TP = 0., FP = 0.;
  float TPR = 0., FPR = 0.;
  float N = confus_mat.N;
  float P = confus_mat.P;
  std::vector<std::pair<float, float>> xy_pairs; 
  float auc = 0.;

  //ROC curve
  for (auto &pair : sort_pairs) {
    //select thresh  == pair.second,each iter, the pair  is predicted to positive.
    if (pair.first == 1) {
      ++TP;
    } else {
      ++FP;
    }
    FPR = FP / N;
    TPR = TP / P;
    xy_pairs.push_back(std::make_pair(FPR, TPR));
  }

  //AUC
  std::pair<float, float> prev_xy(0., 0.);
  for (auto &xy : xy_pairs) {
    if (xy.first != prev_xy.first) {
      auc +=  (xy.second + prev_xy.second)  * (xy.first - prev_xy.first) * 0.5; //trapezoidal area
      prev_xy = xy;
    }
  }
  return auc;
}


std::vector<std::string> SplitString(const std::string& str, const char& pattern) {
  std::vector<std::string> res;
  std::stringstream input(str);  
  std::string temp;
  while(getline(input, temp, pattern)) {
    res.push_back(temp);
  }
  return res;
}


int main(void) {

  std::string uid_path("/opt/shared/recommend/uid_voc.json");
  std::string mid_path("/opt/shared/recommend/mid_voc.json");
  std::string cat_path("/opt/shared/recommend/cat_voc.json");
  std::string uid_embdding_path("/opt/shared/recommend/uid_embeddings.json");
  std::string mid_embdding_path("/opt/shared/recommend/mid_embeddings.json");
  std::string cat_embdding_path("/opt/shared/recommend/cat_embeddings.json");
  std::string model_path("/opt/shared/recommend/Wide.cambricon");
  std::string func_name("subnet0");
  std::string test_file_path("/opt/shared/recommend/local_test_splitByUser_250000");
  uint32_t batch_size = 1;
  const uint32_t his_max_len = 5;
  const int device_id = 0;
  
  Ranking rank(model_path, func_name, uid_path, mid_path, cat_path, uid_embdding_path, mid_embdding_path, cat_embdding_path, device_id);
  std::ifstream test_file(test_file_path);
  std::string user_info_line;
  std::vector<std::string> user_info_text;
  std::vector<std::string> his_mids,his_cats;
  std::vector<float> prob;
  std::vector<int> target;
  std::vector<std::pair<int, float>> target_prob_pairs;
  std::vector<float> temp_prob;
  std::vector<UserInfo> user_info_batch;
  if (test_file.is_open()) {
    //1.convert usr_info text to UserInfo struct and batch infer
    while (getline(test_file, user_info_line)) {  //getline discard '\n'
      UserInfo user_info;
      user_info_text = SplitString(user_info_line, '\t'); 
      target.push_back(std::stoi(user_info_text[0])); //target
      user_info.user = user_info_text[1]; //user
      user_info.item = user_info_text[2]; //item
      user_info.category = user_info_text[3]; //cat
      his_mids = SplitString(user_info_text[4], ''); //his_item
      his_cats = SplitString(user_info_text[5], ''); //his_cat
      
      if (his_mids.size() == 0 || his_cats.size() == 0) {
        continue;
      } else if (his_mids.size() < his_max_len) {
        uint32_t i = 0;
        while (user_info.history_behaviors.size() < his_max_len) {
          user_info.history_behaviors.push_back(std::make_pair(his_mids[i], his_cats[i]));
          i = (i + 1) % his_mids.size(); 
        }
      } else if (his_mids.size() >= his_max_len) {
        for (uint32_t i = 0; i < his_max_len; ++i) {
          user_info.history_behaviors.push_back(std::make_pair(his_mids[i], his_cats[i]));
        }
      }
      user_info_batch.push_back(user_info);

      if (user_info_batch.size() == batch_size) {
        //batch infer
        temp_prob = rank.Process(user_info_batch);
        //save result
        prob.insert(prob.end(), temp_prob.begin(), temp_prob.end());
        //clear user_info_batch
        user_info_batch.clear();
      }
    }

    if (user_info_batch.size() != 0) {
      temp_prob = rank.Process(user_info_batch);
      prob.insert(prob.end(), temp_prob.begin(), temp_prob.end());   
    }

    //2.make pair target and prob
    assert(target.size() == prob.size());
    auto target_iter = target.begin(), target_end = target.end();
    auto prob_iter = prob.begin();
    for (; target_iter != target_end;  ++target_iter,++prob_iter) {
      target_prob_pairs.emplace_back(*target_iter, *prob_iter);
    }
  } else {
    std::cout << "open " + test_file_path << "faile!" << std::endl;
    exit(1);
  }

  //3.statistic model perf
  ConfusionMatrix conf_mat = StatistiConfusionMatrix(target_prob_pairs, 0.5);
  std::pair<float, float> accuracy_pair = CalcAccuracy(conf_mat);
  std::pair<float, float> precision_recall_pair = CalcPrecisionRecall(conf_mat);
  float auc = CalcAUC(target_prob_pairs, conf_mat);

  //5.show perf
  printf("accuracy: %.4f mean_accuracy: %.4f\nprecision: %.4f recall: %.4f \nauc: %.4f\n" \
          ,accuracy_pair.first, accuracy_pair.second, precision_recall_pair.first, precision_recall_pair.second , auc);

  return 0;
}

