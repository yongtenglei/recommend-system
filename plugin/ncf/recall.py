import time
import json

from algorithm.app.ncfTF import  NCF
from plugin import MySQL, user_behavior_config, Redis, hot_item_config, ncf_config, thread_executor_, BEHAVIOR_NUMBER
from plugin.log import log
from plugin.utils import getUserBehavior, getTopNHotItems


class Recall:
    def __init__(self, config):
        self.__ncf = NCF(
            config["rating_path"],
            config["model_path"],
            config["user_dict_path"],
            config["item_dict_path"])


        #用户历史行为数据库
        self.user_behavior_sql = MySQL(user_behavior_config)
        self.hot_item_handle = Redis(hot_item_config)
        self.item_categoriey_dict_ = json.load(open(ncf_config["item_categoriey_dict_"]))

        self.thread_executor_ = thread_executor_


    def parseItemId(self, itemid_index):
        return self.item_categoriey_dict_[itemid_index][0]

    def getCFData(self, userid, itemid):
        return self.__ncf.process(userid, itemid)

class ItemCF(Recall):
    def __init__(self, config):
        super(ItemCF, self).__init__(config)


    def getData(self, userid, itemid):
        start_time = time.clock()
        recall_data = self.getCFData(userid, itemid)
        end_time = time.clock()
        log.debug("getData function using time:{}".format(end_time - start_time))
        recall_data = [(item, self.parseItemId(item)) for item in set(recall_data)]
        return recall_data

class UserCF(Recall):
    def __init__(self, config):
        super(UserCF, self).__init__(config)

    def getData(self, userid):
        start_time = time.clock()
        try:
            behavior = getUserBehavior(self.user_behavior_sql, userid, 5)
        except Exception as e:
            log.error(e.__str__())
            behavior = []

        end_time = time.clock()
        log.debug("getData function using time:{}".format(end_time - start_time))
        if len(behavior) < BEHAVIOR_NUMBER:
            hot_items = getTopNHotItems(self.hot_item_handle, BEHAVIOR_NUMBER)
            behavior.extend([(item[0], item[1]) for item in hot_items])
            behavior = behavior[:BEHAVIOR_NUMBER]

        start_time = time.clock()
        futures = []
        for item_id, item_cate in behavior:
            future = self.thread_executor_.submit(self.getCFData, userid, item_id)
            futures.append(future)

        dataset = []
        for future in futures:
            dataset.extend(future.result())
        end_time = time.clock()
        log.debug("run getCFData thread_executor using time：{}".format(end_time - start_time))
        recall_data_pool = [(itemid, self.parseItemId(itemid)) for itemid in set(dataset)]
        return recall_data_pool


if __name__ == '__main__':
    import pprint
    #test ItemCF
    # itemcf = ItemCF(config=ncf_config)
    # userid = "AU83JSGZFPDFV"
    # itemid = "0001048791"
    # recall_data = itemcf.getData(userid, itemid)
    # pprint.pprint(recall_data


    usercf = UserCF(config=ncf_config)
    userid = "AU83JSGZFPDFV"
    itemid = "0001048791"
    recall_data = usercf.getData(userid)
    pprint.pprint(recall_data)
