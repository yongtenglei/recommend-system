#!/usr/bin/env python3
# -*- coding:utf-8 _*-


import multiprocessing as mp
import time
from plugin import log

class RankingTfPlugin():
    is_need_run = mp.Value('i', 1)

    def __init__(self):
        self.pluginNameUnique = self.__class__.__name__

    def worker(self, rankingtf_input_queue, rankingtf_output_queue):
        import queue
        import time
        from plugin.ranking.ranking import Ranking
        from plugin import ranking_with_pb_config

        start_timestamp = time.clock()
        ranking_ = Ranking(ranking_with_pb_config, using_pb=True)
        end_timestamp = time.clock()
        log.info("Ranking Tensorflow[CPU] init time used：{}".format(end_timestamp - start_timestamp))


        while self.is_need_run.value == 1:
            try:
                userid, his_items, itemList = rankingtf_input_queue.get_nowait()
                start_timestamp = time.clock()
                ranking_result = ranking_.process(userid, his_items, itemList)
                end_timestamp = time.clock()
                log.info("ranking_tf  process on cpu exec Time: {}".format(end_timestamp - start_timestamp))
                try:
                    rankingtf_output_queue.put_nowait(ranking_result)
                except queue.Full:
                    time.sleep(1)
                    rankingtf_output_queue.put_nowait(ranking_result)
            except queue.Empty:
                time.sleep(1)
        log.info('plugin:{} quit'.format(self.pluginNameUnique))

    def onExit(self):
        self.is_need_run.value = 0

    def registerPlugin(self):
        log.info('registerPlugin:{}'.format(self.pluginNameUnique))


if __name__ == '__main__':
    from signal import signal, SIGINT
    import pprint
    from plugin.utils import getSearchResult, getUserBehavior, getTopNHotItems, getAllTableNames

    IS_MAIN_RUN = mp.Value('i', 1)  # 整个程序运行标志位    1 需要运行  0 退出


    def onExit():
        """
        Ctrl + C 的回调函数， 作用退出结束整个程序
        :return:
        """
        global IS_MAIN_RUN
        workFlow.onExit()
        IS_MAIN_RUN.value = 0


    def handler(signum, stack):
        onExit()

    signal(SIGINT, handler)  # 按Ctrl + C退出整个程序
    from plugin import MySQL, item_config, user_behavior_config, Redis, hot_item_config, rankingtf_input_queue, rankingtf_output_queue, BEHAVIOR_NUMBER
    from plugin.bus import workFlow
    rankingtfplugin = RankingTfPlugin()
    workFlow.registBus(rankingtfplugin.pluginNameUnique, rankingtfplugin.worker, (rankingtf_input_queue, rankingtf_output_queue), rankingtfplugin.onExit)
    workFlow.busStart()

    item_sql = MySQL(item_config)
    user_behavior_sql = MySQL(user_behavior_config)
    hot_item_handle = Redis(hot_item_config)
    item_all_table = getAllTableNames(item_sql, item_config["database"])

    userid = "AU83JSGZFPDFV"

    start_timestamp = time.clock()
    result = getSearchResult(item_sql, "book", item_all_table)
    end_timestamp = time.clock()

    log.info("func getSearchResult item_sql exec time : {}".format(end_timestamp - start_timestamp))

    while IS_MAIN_RUN.value == 1:
        log.info("1")
        item_list = [(item["item id"], item["sub categories"]) for item in result]
        log.info("2")
        # behavior = getUserBehavior(user_behavior_sql, userid, BEHAVIOR_NUMBER)
        behavior = None
        log.info("3")
        if not behavior:
            log.info("4")
            hot_items = getTopNHotItems(hot_item_handle, BEHAVIOR_NUMBER)
            log.info("5")
            behavior = [(item[0], item[1]) for item in hot_items]
        log.info("6")
        rankingtf_input_queue.put((userid, behavior, item_list))
        log.info("7")
        pprint.pprint(rankingtf_output_queue.get())
        log.info("8")
        break
    onExit()