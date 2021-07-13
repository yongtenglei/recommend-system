import multiprocessing as mp
import threading
import time
from plugin.log import log
from plugin.web.webui import app


class WebUiPlugin():
    is_need_run = mp.Value('i', 1)

    def __init__(self):
        self.pluginNameUnique = self.__class__.__name__

    def worker(self, *args):
        p = threading.Thread(target=app.run, args=('0.0.0.0', 8001), daemon=True)
        p.start()
        log.info('webui plugin start ...')
        while self.is_need_run.value == 1:
            time.sleep(1)
        log.info('webui plugin woker exit')

    def onExit(self):
        self.is_need_run.value = 0

    def registerPlugin(self):
        log.info('registerPlugin:{}'.format(self.pluginNameUnique))


if __name__ == '__main__':
    webUiPlugin = WebUiPlugin()
    webUiPlugin.worker()
