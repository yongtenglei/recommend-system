#!/usr/bin/env python3
# -*- coding:utf-8 _*-

import pprint
import multiprocessing as mp
from signal import signal, SIGINT

from plugin.ranking.ranking_plugin import RankingPlugin
from plugin.ranking.rankingtf_plugin import RankingTfPlugin
from plugin.web.webui_plugin import WebUiPlugin
from plugin.ncf.itemcf_plugin import ItemCfPlugin
from plugin.ncf.user_plugin import UserCFPlugin
from plugin import itemcf_input_queue, itemcf_output_queue
from plugin import usercf_input_queue, usercf_output_queue
from plugin import *
from plugin.bus import workFlow


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


if __name__ == '__main__':

    webUiPlugin = WebUiPlugin()
    itemcfPluin = ItemCfPlugin()
    usercfPlugin = UserCFPlugin()
    rankingPlugin = RankingPlugin()
    rankingTfPlugin = RankingTfPlugin()

    workFlow.registBus(webUiPlugin.pluginNameUnique, webUiPlugin.worker, (), webUiPlugin.onExit)
    workFlow.registBus(itemcfPluin.pluginNameUnique,
                       itemcfPluin.worker,
                       (itemcf_input_queue, itemcf_output_queue),
                       itemcfPluin.onExit)
    workFlow.registBus(usercfPlugin.pluginNameUnique,
                       usercfPlugin.worker,
                       (usercf_input_queue, usercf_output_queue),
                       usercfPlugin.onExit)
    workFlow.registBus(rankingPlugin.pluginNameUnique,
                       rankingPlugin.worker,
                       (ranking_input_queue, ranking_output_queue),
                       rankingPlugin.onExit)
    workFlow.registBus(rankingTfPlugin.pluginNameUnique,
                       rankingTfPlugin.worker,
                       (rankingtf_input_queue, rankingtf_output_queue),
                       rankingTfPlugin.onExit)

    workFlow.busStart()

    while IS_MAIN_RUN.value == 1:
        pass