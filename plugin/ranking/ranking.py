##########################################################################
#
# Copyright (C) [2020] by Cambricon, Inc. All rights reserved
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.
###########################################################################

import dataflow


class Ranking:
    def __init__(self, config, using_pb=False):
        self.__using_pb = using_pb
        if not using_pb:
            self.infer_ = dataflow.Ranking(config["offline_model"],
                                           config["fun_name"],
                                           config["uid_path"],
                                           config["mid_path"],
                                           config["cat_path"],
                                           config["uid_embedding_path"],
                                           config["mid_embedding_path"],
                                           config["cat_embedding_path"],
                                           int(config["device_id"]))
        else:
            from algorithm.app.rankingTF import RankingTF
            self.infer_ = RankingTF(config["model_name"],
                                    config["model_path"],
                                    config["uid_path"],
                                    config["mid_path"],
                                    config["cat_path"]
                                    )

    def process(self, userid, his_items, itemList):
        '''
        userid: string
        his_items: [(itemId, categories), ...]
        itemList: [(itemId, categories), ...]
        '''
        if not self.__using_pb:
            user_infos = []
            for (itemid, itemcat) in itemList:
                user_info = dataflow.UserInfo()
                user_info.user = userid
                user_info.item = itemid
                user_info.category = itemcat
                user_info.history_behaviors = his_items
                user_infos.append(user_info)
            result = self.infer_.process(user_infos)
        else:
            infer_data = [[userid, itemid, itemcat, his_items] for (itemid, itemcat) in itemList]
            result = self.infer_.process(infer_data)
        return [round(item, 6) for item in result]
