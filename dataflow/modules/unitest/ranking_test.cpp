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
#include <string>

#include "ranking.hpp"

int main(void) {
  std::string uid_path("/opt/shared/recommend/uid_voc.json");
  std::string mid_path("/opt/shared/recommend/mid_voc.json");
  std::string cat_path("/opt/shared/recommend/cat_voc.json");
  std::string uid_embdding_path("/opt/shared/recommend/uid_embeddings.json");
  std::string mid_embdding_path("/opt/shared/recommend/mid_embeddings.json");
  std::string cat_embdding_path("/opt/shared/recommend/cat_embeddings.json");
  std::string model_path("/opt/shared/recommend/Wide.cambricon");
  std::string func_name("subnet0");
  uint32_t test_number = 10;
  //1.create infer
  Ranking rank(model_path, func_name, uid_path, mid_path, cat_path, uid_embdding_path, mid_embdding_path, cat_embdding_path,0);

  //2.input data
  std::string user = "A2YII0ICP99QYQ";
  std::string item1 = "B00CUSSKUM";
  std::string category1 = "Contemporary Women";
  std::vector<std::pair<std::string, std::string>> history_behaviors = {
                std::pair<std::string, std::string>("B004U3SWB2", "Basic Cases"), 
                std::pair<std::string, std::string>("B005SJBIVI", "Screen Protectors"),
                std::pair<std::string, std::string>("B005SUHRVC", "Basic Cases"),
                std::pair<std::string, std::string>("B006VWV956", "Data Cables"),
                std::pair<std::string, std::string>("B008C6ASV0", "Basic Cases"),
              };
  std::string item2 = "B005SUHRVC";
  std::string category2 = "Basic Cases";

  std::vector<UserInfo> user_infos;

  UserInfo userinfo;
  userinfo.user = user;
  userinfo.item = item1;
  userinfo.category = category1;
  userinfo.history_behaviors = history_behaviors;
  user_infos.push_back(userinfo);

  userinfo.user = user;
  userinfo.item = item2;
  userinfo.category = category2;
  userinfo.history_behaviors = history_behaviors;
  user_infos.push_back(userinfo);

  for (uint32_t i = 0; i < test_number; ++i) {
    UserInfo userinfo;
    userinfo.user = user;
    userinfo.item = item1;
    userinfo.category = category1;
    userinfo.history_behaviors = history_behaviors;
    user_infos.push_back(userinfo);
  }

  //3.infer
  std::vector<float> result = rank.Process(user_infos);
  for (uint32_t i = 0; i < result.size(); ++i) {
    std::cout << "User: " << user_infos[i].user << ", Item: "<< user_infos[i].item << ", CTR is: " <<result[i] << std::endl;
  }
  return 0;
}
