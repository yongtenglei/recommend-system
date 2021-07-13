import json

from flask import jsonify, session
from flask_restful import Resource

from plugin import BEHAVIOR_NUMBER, thread_executor_, MySQL, user_behavior_config, item_config, \
    hot_item_config, Redis
from plugin import usercf_input_queue, usercf_output_queue, \
    itemcf_input_queue, itemcf_output_queue, \
    ranking_input_queue, ranking_output_queue, \
    rankingtf_input_queue, rankingtf_output_queue, log
from plugin.utils import getUserBehavior, getTopNHotItems, getItemInfo

import time


class GenerateRecommendTemplate:
    def __init__(self):
        self.item_sql = MySQL(item_config, maxconnections=30)
        self.user_behavior_sql = MySQL(user_behavior_config)
        self.hot_item_handle = Redis(hot_item_config)
        self.redis_cache = Redis(hot_item_config)
        self.redis_cache_r = Redis(hot_item_config)

    def recommendTemplate(self, userid, itemid=None):
        if itemid is None:
            log.info("GuessYouLike usercf_input_queue.put({})".format(userid))
            usercf_input_queue.put(userid)
            recall_data = usercf_output_queue.get()
            log.info("Recommend usercf calculation complete")
        else:
            log.info("Recommend itemcf_input_queue.put(({}, {}))".format(userid, itemid))
            itemcf_input_queue.put((userid, itemid))
            recall_data = itemcf_output_queue.get()
            log.info("Recommend usercf calculation complete")

        log.info("Get detail information of the product list")

        recall_data = recall_data[:20]
        futures = []
        for item_data in recall_data:
            # getItemInfo(handle, itemid, category)
            future = thread_executor_.submit(getItemInfo, self.item_sql, item_data[0], item_data[1])
            futures.append(future)

        log.info("get behavior data")
        # get behavior data
        behavior = getUserBehavior(self.user_behavior_sql, userid, BEHAVIOR_NUMBER)
        if len(behavior) < BEHAVIOR_NUMBER:
            hot_items = getTopNHotItems(self.hot_item_handle, BEHAVIOR_NUMBER)
            behavior.extend([(item[0], item[1]) for item in hot_items])
            behavior = behavior[0:BEHAVIOR_NUMBER]

        log.info("task: ranking")
        # task: ranking
        ranking_input_queue.put((userid, behavior, recall_data))
        rankingtf_input_queue.put((userid, behavior, recall_data))

        log.info("get result from thread pool")
        future_result = []
        # get result from thread pool
        for future in futures:
            future_result.append(future.result())

        log.info("222")
        future_result.append(rankingtf_output_queue.get())
        log.info("333")
        future_result.append(ranking_output_queue.get())

        log.info("parse result from thredpool result")
        # parse result from thredpool result
        json_result = future_result[:-2]
        ranking_cpu_result = future_result[-2]
        ranking_result = future_result[-1]
        result = []
        for item, ctr, cpu_ctr in zip(json_result, ranking_result, ranking_cpu_result):
            item["MLU_CTR"] = ctr
            item["CPU_CTR"] = cpu_ctr
            result.append(item)
        return result


genTemplate = GenerateRecommendTemplate()


class GuessYouLike(Resource):
    def __init__(self):
        global genTemplate
        self.genTemplate = genTemplate

    def get(self):
        login = False
        if 'userid' in session:
            login = True
            userid = session['userid']
            if userid in self.genTemplate.redis_cache.connection.keys():
                temp = self.genTemplate.redis_cache.get(userid)
                if temp == "":
                    json_result = self.genTemplate.recommendTemplate(userid)
                    json_result = self._getTopN(json_result)
                    self.genTemplate.redis_cache.set(userid, json.dumps(json_result))
                else:
                    json_result = json.loads(self.genTemplate.redis_cache.get(userid))
            else:
                json_result = self.genTemplate.recommendTemplate(userid)
                json_result = self._getTopN(json_result)
                self.genTemplate.redis_cache.set(userid, json.dumps(json_result))
            return jsonify(json_result)
#           return jsonify(self._getTopN(json_result, sort_key="MLU_CTR"))

        else:
            return "hello"

    def post(self):
        pass

    def delete(self):
        pass

    def put(self):
        pass

    def _getTopN(self, json_data, sort_key="MLU_CTR"):
        return sorted(json_data, key=lambda s: s[sort_key], reverse=True)


class Recommend(Resource):
    def __init__(self):
        global genTemplate
        self.genTemplate = genTemplate

    def get(self, itemid):
        login = False
        if 'userid' in session:
            login = True
            userid = session['userid']
            if userid in self.genTemplate.redis_cache_r .connection.keys():
                temp = self.genTemplate.redis_cache_r .get(userid)
                if temp == "":
                    json_result = self.genTemplate.recommendTemplate(userid, itemid)
                    json_result = self._getTopN(json_result)
                    self.genTemplate.redis_cache_r .set(userid, json.dumps(json_result))
                else:
                    json_result = json.loads(self.genTemplate.redis_cache_r .get(userid))
            else:
                json_result = self.genTemplate.recommendTemplate(userid, itemid)
                json_result = self._getTopN(json_result)
                self.genTemplate.redis_cache_r .set(userid, json.dumps(json_result))
            return jsonify(json_result)

        # if 'userid' in session:
        #     login, userid = True, session['userid']
        #     json_result = self.genTemplate.recommendTemplate(userid, itemid)
        #     return jsonify(self._getTopN(json_result, sort_key="MLU_CTR"))

    def post(self):
        return jsonify({"id": "id"}), 201

    def delete(self):
        pass

    def put(self):
        pass

    def _getTopN(self, json_data, sort_key="MLU_CTR"):
        return sorted(json_data, key=lambda s: s[sort_key], reverse=True)
