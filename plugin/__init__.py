#!/usr/bin/env python3
# -*- coding:utf-8 _*-

import json
import multiprocessing as mp
import os

from plugin.log import log
from plugin.mysql_wrapper import MySQL
from plugin.redis_wrapper import Redis
from concurrent.futures import ThreadPoolExecutor

'''
const number 
'''
REVIEWER = 1  # behavior which 1 is reviewer, 2 is store up, ...
BEHAVIOR_NUMBER = 5  # behavior number, which decided by model


thread_executor_ = ThreadPoolExecutor(max_workers=20)

def getConfigPath():
    __PWD = os.path.abspath(os.path.dirname(__file__))
    CONFIG_FILE_PATH = os.path.join(__PWD, '..', 'config.json')
    assert os.path.exists(CONFIG_FILE_PATH)
    del __PWD
    return CONFIG_FILE_PATH


def loadConfig(config_name=getConfigPath(), module_name=None):
    with open(config_name, 'r') as f:
        config = json.loads(f.read())
    return config[module_name]


ranking_config = loadConfig(module_name="ranking")
ranking_with_pb_config = loadConfig(module_name="rankingTF")
user_config = loadConfig(module_name="user_database")
item_config = loadConfig(module_name="item_database")
reviewer_config = loadConfig(module_name="reviewer_database")
user_behavior_config = loadConfig(module_name="user_behavior_database")
hot_item_config = loadConfig(module_name="hot_item_database")
ncf_config = loadConfig(module_name="ncf")

# queue for plugin itemcf ...
ctx = mp.get_context()
itemcf_input_queue = ctx.Manager().Queue(5)
itemcf_output_queue = ctx.Manager().Queue(5)

usercf_input_queue = ctx.Manager().Queue(5)
usercf_output_queue = ctx.Manager().Queue(5)

ranking_input_queue = ctx.Manager().Queue(5)
ranking_output_queue = ctx.Manager().Queue(5)

rankingtf_input_queue = ctx.Manager().Queue(5)
rankingtf_output_queue = ctx.Manager().Queue(5)


