#!/usr/bin/env python3
# -*- coding:utf-8 _*-


import multiprocessing as mp
from plugin import log, itemcf_output_queue, itemcf_input_queue


class ItemCfPlugin():
    is_need_run = mp.Value('i', 1)

    def __init__(self):
        self.pluginNameUnique = self.__class__.__name__

    def worker(self, itemcf_input_queue, itemcf_output_queue):
        import queue
        import time
        from plugin.ncf.recall import ItemCF
        from plugin import ncf_config
        _itemcf = ItemCF(ncf_config)
        log.info("ItemCF ncf init complete")
        RATE = 1 / 200

        while self.is_need_run.value == 1:
            try:
                userid, itemid = itemcf_input_queue.get_nowait()
                recall_data = _itemcf.getData(userid, itemid)
                try:
                    itemcf_output_queue.put_nowait(recall_data)
                except queue.Full:
                    time.sleep(RATE)
                    itemcf_output_queue.put_nowait(recall_data)
            except queue.Empty:
                time.sleep(RATE)
        log.info('plugin:{} quit'.format(self.pluginNameUnique))

    def onExit(self):
        self.is_need_run.value = 0

    def registerPlugin(self):
        log.info('registerPlugin:{}'.format(self.pluginNameUnique))


if __name__ == '__main__':
    import pprint

    itemCFPlugin = ItemCfPlugin()
    import threading
    from plugin import itemcf_input_queue, itemcf_output_queue

    t1 = threading.Thread(target=itemCFPlugin.worker, args=(itemcf_input_queue, itemcf_output_queue))
    t1.start()
    userid = "AU83JSGZFPDFV"
    itemid = "0001048791"
    itemcf_input_queue.put((userid, itemid))
    recall_data = itemcf_output_queue.get()
    pprint.pprint(recall_data)
