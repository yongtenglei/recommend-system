import multiprocessing as mp
from plugin.log import log



class UserCFPlugin():
    is_need_run = mp.Value('i', 1)

    def __init__(self):
        self.pluginNameUnique = self.__class__.__name__

    def worker(self, usercf_input_queue, usercf_output_queue):
        import queue
        import time
        from plugin.ncf.recall import UserCF
        from plugin import ncf_config

        RATE = 1 / 200

        _usercf = UserCF(ncf_config)
        log.info("UserCF ncf init complete")

        while self.is_need_run.value == 1:
            try:
                userid = usercf_input_queue.get_nowait()
                log.info(userid)
                data = _usercf.getData(userid)
                try:
                    usercf_output_queue.put_nowait(data)
                except queue.Full:
                    time.sleep(RATE)
                    usercf_output_queue.put_nowait(data)
            except queue.Empty:
                time.sleep(RATE)
        log.info('plugin:{} quit'.format(self.pluginNameUnique))

    def onExit(self):
        self.is_need_run.value = 0

    def registerPlugin(self):
        log.info('registerPlugin:{}'.format(self.pluginNameUnique))


if __name__ == '__main__':
    import pprint
    userCFPlugin = UserCFPlugin()
    import threading
    from plugin import usercf_input_queue, usercf_output_queue
    t1 = threading.Thread(target=userCFPlugin.worker, args=(usercf_input_queue, usercf_output_queue))
    t1.start()
    userid = "AU83JSGZFPDFV"
    itemid = "0001048791"
    usercf_input_queue.put(userid)
    recall_data = usercf_output_queue.get()
    pprint.pprint(recall_data)
