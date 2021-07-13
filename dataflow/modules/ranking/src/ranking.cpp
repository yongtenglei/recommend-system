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
#include <string>
#include <fstream>
#include <numeric>
#include "cxxutil/exception.h"
#include <rapidjson/document.h>
#include <rapidjson/writer.h>
#include "ranking.hpp"

Ranking::Ranking(const std::string& model_path,
                 const std::string& func_name,
                 const std::string& uid_path,
                 const std::string& mid_path,
                 const std::string& cat_path,
                 int device_id)
                 : dev_id_(device_id) {
  //1.create dicts
  CreateWordDict(uid_path, &user_dicts_);
  CreateWordDict(mid_path, &item_dicts_);
  CreateWordDict(cat_path, &categories_dicts_);
  //2.load model
  std::shared_ptr<edk::ModelLoader> model_loder = std::make_shared<edk::ModelLoader>(model_path, func_name);

  //3.set mlu cnrt environment
  edk::MluContext context;
  context.SetDeviceId(dev_id_);
  context.ConfigureForThisThread();

  //4.create model_runner 
  model_runner_ = std::make_shared<ModelRunner>(model_loder, dev_id_);
}

Ranking::Ranking(const std::string& model_path, 
                 const std::string& func_name,
                 const std::string& uid_path,
                 const std::string& mid_path,
                 const std::string& cat_path,
                 const std::string& uid_embdding_path,
                 const std::string& mid_embdding_path,
                 const std::string& cat_embdding_path,
                 int device_id)
                 : dev_id_(device_id) {
  //1.create dicts
  CreateWordDict(uid_path, &user_dicts_);
  CreateWordDict(mid_path, &item_dicts_);
  CreateWordDict(cat_path, &categories_dicts_);

  //2.read embeidng layer weight
  LoadEmbeddingLayer(uid_embdding_path, &uid_embdding_weight_);
  LoadEmbeddingLayer(mid_embdding_path, &mid_embdding_weight_);
  LoadEmbeddingLayer(cat_embdding_path, &cat_embdding_weight_);

  //3.load model
  std::shared_ptr<edk::ModelLoader> model_loder = std::make_shared<edk::ModelLoader>(model_path, func_name);

  //std::cout << "1" << std::endl;
  //4.set mlu cnrt environment
  edk::MluContext context;
  context.SetDeviceId(dev_id_);
  context.ConfigureForThisThread();

  //5.create model_runner 
  model_runner_ = std::make_shared<ModelRunner>(model_loder, dev_id_);
}

Ranking::~Ranking() {
}

int Ranking::CreateWordDict(const std::string& file_path, std::unordered_map<std::string, uint32_t>* word_dict) {
  if (word_dict == nullptr) {
    return -1;
  }

  std::ifstream ifs(file_path);
  if (!ifs.is_open()) {
    std::cout << "Error Open: " << file_path << std::endl;
    return -1;
  }

  std::string jstr((std::istreambuf_iterator<char>(ifs)), std::istreambuf_iterator<char>());
  ifs.close();

  //parse
  rapidjson::Document doc;
  if (doc.Parse<rapidjson::kParseCommentsFlag>(jstr.c_str()).HasParseError()) {
    std::cout << "Error: Parse file: " << file_path + " error!" << std::endl;
    return -1;
  }

  rapidjson::Value::ConstMemberIterator iter;
  for (iter = doc.MemberBegin(); iter != doc.MemberEnd(); ++iter) {
    word_dict->insert(std::pair<std::string, uint32_t>(iter->name.GetString(), iter->value.GetUint()));
  }
  return 0;
}

int Ranking::LoadEmbeddingLayer(const std::string& weight_path, std::vector<std::vector<float>>* embdding_weight) {
  //1.read weight form json 
  std::ifstream ifs(weight_path);
  if (!ifs.is_open()) {
    std::cout << "Error Open: " << weight_path << std::endl;
    return -1;
  }
  std::string jstr((std::istreambuf_iterator<char>(ifs)), std::istreambuf_iterator<char>());
  ifs.close();

  rapidjson::Document doc;
  if (doc.Parse<rapidjson::kParseCommentsFlag>(jstr.c_str()).HasParseError()) {
    std::cout << "Error: Parse file: " << weight_path + " error!" << std::endl;
    return -1;
  }
 
  //2.create embdding_weight
  rapidjson::Value &WeightMat = doc;
  assert(WeightMat.IsArray());

  for (auto row_iter = WeightMat.Begin(); row_iter != WeightMat.End(); ++row_iter) {
    const rapidjson::Value& col = *row_iter;
    assert(col.IsArray());
    std::vector<float> row_val;
    for (auto col_iter = col.Begin(); col_iter != col.End(); ++col_iter) {     
      row_val.push_back(col_iter->GetFloat());
    }
    embdding_weight->emplace_back(row_val);
  }
  return 0;
}

std::vector<float> Ranking::Process(std::vector<UserInfo>& user_infos) {
  std::vector<NetInputs> net_inputs;
  std::vector<NetOutputs> net_outputs;
  std::vector<float> result(user_infos.size(), 0.0f);

  for (uint32_t i = 0; i < user_infos.size(); ++i) {
    std::vector<float*> net_input;
    if (2 == PreProc(user_infos[i], &net_input)) {
      result[i] = -1.0f;
    }
    net_inputs.push_back(net_input);
  }
  model_runner_->Run(net_inputs, &net_outputs);
  for (auto& net_input : net_inputs) {
    delete[] net_input[0];
  }
  for (uint32_t i = 0; i < net_outputs.size(); ++i) {
    if (result[i] < 0) {
      result[i] = 0;
      continue;
    }
    result[i] = PostProc(net_outputs[i]);
  }
  return result;
}

int Ranking::PreProc(const UserInfo& user_info, std::vector<float*>* net_input) {

  if (net_input == nullptr) {
    return -1;
  }

  auto GetEmbeddingIndex = [](std::unordered_map<std::string, uint32_t>& dict, std::string item) -> uint32_t {
    if (dict.find(item) != dict.end()) {
      return dict[item];
    }
    return 0;
  };

  uint32_t behav_size = user_info.history_behaviors.size();
  if (behav_size != HIS_LEN) {
    std::cout << "Error, behav_size is: "<< behav_size << ", only support behav_size = 5, please check your input parameter!" << std::endl;
    return -1;
  }

  std::vector<uint32_t> input_shape = {EMBEDING_DIM, EMBEDING_DIM, HIS_LEN * EMBEDING_DIM, HIS_LEN * EMBEDING_DIM, EMBEDING_DIM};

  float* data = new float[std::accumulate(input_shape.begin(), input_shape.end(), 0)];
  for (auto it : input_shape) {
    net_input->push_back(data);
    data += it;
  }
  auto& net_input_val = *net_input;
  uint32_t uid, mid, cat, his_mid, his_cat;
  uid = GetEmbeddingIndex(user_dicts_, user_info.user);
  mid = GetEmbeddingIndex(item_dicts_, user_info.item);
  cat = GetEmbeddingIndex(categories_dicts_, user_info.category);

  // If not found in dictionaries, fill value with 0, return value is 2
  if (user_dicts_[user_info.user] != uid || item_dicts_[user_info.item] != mid) {
    memset(net_input_val[0], 0, sizeof(float) * std::accumulate(input_shape.begin(), input_shape.end(), 0));
    return 2;
  }
  // fill with actual embedding value
  memcpy(net_input_val[4], uid_embdding_weight_[uid].data(), sizeof(float) * EMBEDING_DIM);
  memcpy(net_input_val[0], mid_embdding_weight_[mid].data(), sizeof(float) * EMBEDING_DIM);
  memcpy(net_input_val[1], cat_embdding_weight_[cat].data(), sizeof(float) * EMBEDING_DIM);

  for (uint32_t i = 0; i < behav_size; ++i) {
    std::string item = user_info.history_behaviors[i].first;
    std::string cat = user_info.history_behaviors[i].second;
    his_mid = GetEmbeddingIndex(item_dicts_, item);
    his_cat = GetEmbeddingIndex(categories_dicts_, cat);
    memcpy(net_input_val[2] + (i * EMBEDING_DIM), mid_embdding_weight_[his_mid].data(), sizeof(float) * EMBEDING_DIM);
    memcpy(net_input_val[3] + (i * EMBEDING_DIM), cat_embdding_weight_[his_cat].data(), sizeof(float) * EMBEDING_DIM);
  }
  return 0;
}

float Ranking::PostProc(const NetOutputs& outputs) {
  return outputs[0][0];
}

