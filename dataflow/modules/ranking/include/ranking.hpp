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
#ifndef MODULES_RANKING_INCLUDE_HPP_
#define MODULES_RANKING_INCLUDE_HPP_

#include <memory>
#include <vector>
#include <string>
#include <unordered_map>

#include "model_runner.hpp"

struct UserInfo{ 
  std::string user;
  std::string item;
  std::string category;
  std::vector<std::pair<std::string, std::string>> history_behaviors; 
};

class Ranking {
 public:
  explicit Ranking(const std::string& model_path, 
                   const std::string& func_name,
                   const std::string& uid_path,
                   const std::string& mid_path,
                   const std::string& cat_path,
                   int device_id = 0);
  explicit Ranking(const std::string& model_path, 
                   const std::string& func_name,
                   const std::string& uid_path,
                   const std::string& mid_path,
                   const std::string& cat_path,
                   const std::string& uid_embdding_path,
                   const std::string& mid_embdding_path,
                   const std::string& cat_embdding_path,
                   int device_id = 0);
  ~Ranking();
  std::vector<float> Process(std::vector<UserInfo> &usr_infos);
  
 private:
  int CreateWordDict(const std::string& file_path, std::unordered_map<std::string, uint32_t>* word_dict); 
  int LoadEmbeddingLayer(const std::string& weight_path, std::vector<std::vector<float>>* embdding_weight);
  int PreProc(const UserInfo& user_info, std::vector<float*>* net_input);
  float PostProc(const NetOutputs& outputs);

  int dev_id_ = 0;
  const uint32_t EMBEDING_DIM = 18; 
  const uint32_t HIS_LEN = 5;
  
  std::unordered_map<std::string, uint32_t> user_dicts_;
  std::unordered_map<std::string, uint32_t> item_dicts_;
  std::unordered_map<std::string, uint32_t> categories_dicts_;
  std::vector<std::vector<float>> uid_embdding_weight_; 
  std::vector<std::vector<float>> mid_embdding_weight_; 
  std::vector<std::vector<float>> cat_embdding_weight_; 
  std::shared_ptr<ModelRunner> model_runner_;
};

#endif // MODULES_RANKING_INCLUDE_HPP_
