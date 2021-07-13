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

from flask import jsonify, session
from flask_restful import Resource

from plugin.utils import getSearchResult, getUserBehavior, getTopNHotItems, getAllTableNames
from plugin import MySQL, item_config, user_behavior_config, Redis, hot_item_config, BEHAVIOR_NUMBER, log
from plugin import ranking_input_queue, ranking_output_queue,\
    rankingtf_input_queue, rankingtf_output_queue

import time


class QuerySearch(Resource):
    def __init__(self):
        self.item_sql = MySQL(item_config, maxconnections=20)
        self.user_behavior_sql = MySQL(user_behavior_config)
        self.hot_item_handle = Redis(hot_item_config)
        self.item_table_names = getAllTableNames(self.item_sql, item_config["database"])

    def get(self, keyword):
        keyword = keyword.strip()
        if keyword:
            start_timestamp = time.clock()
            result = getSearchResult(self.item_sql, keyword, self.item_table_names)
            end_timestamp = time.clock()
            log.info("Search keyword mysql using time: {}".format(end_timestamp - start_timestamp))
            if 'userid' in session:
                login, userid = True, session['userid']
                item_list = [(item["item id"], item["sub categories"]) for item in result]
                # behavior = getUserBehavior(self.user_behavior_sql, userid, BEHAVIOR_NUMBER)
                behavior = None
                if not behavior:
                    hot_items = getTopNHotItems(self.hot_item_handle, BEHAVIOR_NUMBER)
                    behavior = [(item[0], item[1]) for item in hot_items]

                # # task: ranking
                # futures = []
                ranking_input_queue.put((userid, behavior, item_list))
                rankingtf_input_queue.put((userid, behavior, item_list))

                log.info("ranking processing...")
                mlu_ranking = ranking_output_queue.get()
                cpu_ranking = rankingtf_output_queue.get()

                json_result = []
                for item, mlu_ctr, cpu_ctr in zip(result, mlu_ranking, cpu_ranking):
                    item["MLU_CTR"] = mlu_ctr
                    item["CPU_CTR"] = cpu_ctr
                    json_result.append(item)

                return jsonify(self._getTopN(result))
            else:
                return jsonify(result)
        return jsonify([])

    def post(self):
        return jsonify({"id": "id"}), 201

    def delete(self):
        pass

    def put(self):
        pass

    def _getTopN(self, json_data):
        return sorted(json_data, key=lambda s: s["MLU_CTR"], reverse=True)
