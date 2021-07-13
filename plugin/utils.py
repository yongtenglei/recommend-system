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
##########################################################################
import time

from plugin import thread_executor_
from plugin import log


def getAllTableNames(handle, database_name):
    sql = "select table_name from information_schema.tables where table_schema='{}' ".format(database_name)
    table_names = [table['table_name'] for table in handle.fetchAllDB(sql)]
    return table_names


def isValid(handle, username, password):
    try:
        sql = "SELECT * FROM user where `user id`='{}'".format(username)
        result = handle.fetchOneDB(sql)
        if result:
            return True
        else:
            return False
    except Exception as e:
        return False


def getUserBehavior(handle, userid, num):
    '''
    userid(string): the id of user
    num(int): the number of user behavior
    return [(itemid, item cagtegory), ...]
    return parameter is a list which make up of tuples
    the first parameter of tuple is item id
    the second parameter of tuple is item category
    '''
    sql = "SELECT `item id`, `categories` FROM `{}` ORDER BY `time` DESC LIMIT 10".format(userid)
    result = handle.fetchAllDB(sql)
    if len(result) < num:
        result = result * num
    return [(item["item id"], item["categories"]) for item in result][0:num]


def getSearchResult(handle, keyword, tables, num=10):
    '''
    keyword(string): search keyword
    tables(string): database table name
    return json string
    '''
    result = []
    search_tasks = []
    for table in tables:
        sql = "SELECT * FROM `{}` WHERE MATCH(`title`) AGAINST('%{}%' IN BOOLEAN MODE) LIMIT {}".format(table, keyword, num)
        search_task = thread_executor_.submit(handle.fetchAllDB, sql)
        search_tasks.append(search_task)

    for task, table in zip(search_tasks, tables):
        items = [dict(item, **{"categories": table}) for item in task.result()]
        result.extend(items)
    return result

def getItemInfo(handle, itemid, category):
    '''
    itemid(string): id of item
    category(string): category of item
    return json string
    '''
    sql = "SELECT * FROM `{}` WHERE `item id` = '{}' ".format(category, itemid)
    log.debug(sql)
    data = handle.fetchOneDB(sql)
    data["categories"] = category
    return data


def saveUserBehavior(handle, userid, itemid, category, behavior):
    sql = "INSERT INTO {} (`item id`, `categories`, `behavior`, `time`) VALUES('{}', '{}', {}, NOW())".format(userid,
                                                                                                              itemid,
                                                                                                              category,
                                                                                                              behavior)
    return handle.exe(sql)


def createUserBehavior(handle, table_name):
    sql = """CREATE table IF NOT EXISTS {} (
           `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, 
           `item id` varchar(255) NOT NULL,
           `categories` varchar(255) NOT NULL,
           `behavior` int(3) NOT NULL,
           `time` TIMESTAMP
           ) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=0
       """.format(table_name)
    handle.exe(sql)


def saveHotItem(handle, itemid, category):
    new_key = category + "," + itemid
    if not handle.get(new_key):
        handle.set(new_key, 1)
    else:
        handle.increase(new_key)


def getTopNHotItems(handle, num):
    '''
    return:[(item, category, click_number), ...]
    return parameter is a list which makes up of tuples
    the first parameter of tuple is 'item id'
    the second parameter of tuple is 'item category'
    the third parameter of tuple is the click number of 'item id'
    '''
    result = handle.getAllValue()
    result = sorted(result, key=lambda x: x[1][0], reverse=True)
    result = [(item[0].split(",")[0], item[0].split(",")[-1], item[1][0]) for item in result]
    if len(result) < num:
        result = result * num
    return result[0:num]


if __name__ == '__main__':
    import pprint
    from plugin import loadConfig
    from plugin.mysql_wrapper import MySQL
    from plugin.redis_wrapper import Redis

    user_config = loadConfig(module_name="user_database")
    item_config = loadConfig(module_name="item_database")
    reviewer_config = loadConfig(module_name="reviewer_database")
    user_behavior_config = loadConfig(module_name="user_behavior_database")
    hot_item_config = loadConfig(module_name="hot_item_database")

    user_sql = MySQL(user_config)
    item_sql = MySQL(item_config, maxconnections=10)
    reviewer_sql = MySQL(reviewer_config)
    user_behavior_sql = MySQL(user_behavior_config)
    hot_item_handle = Redis(hot_item_config)

    # 查询全部数据表的表名
    # pprint.pprint([user_config["database"], "AllTables：", getAllTableNames(user_sql, user_config["database"])])
    # pprint.pprint([item_config["database"], "AllTables：", getAllTableNames(item_sql, item_config["database"])])
    # pprint.pprint([reviewer_config["database"], "AllTables：", getAllTableNames(reviewer_sql, reviewer_config["database"])])
    # pprint.pprint([user_behavior_config["database"], "AllTables：", getAllTableNames(user_behavior_sql, user_behavior_config["database"])])

    # 查询指定user-id 的历史数据
    # pprint.pprint(getUserBehavior(user_behavior_sql, "AU83JSGZFPDFV", 10))

    # 查找商品
    start = time.clock()
    pprint.pprint(getSearchResult(item_sql, 'xiaomi', getAllTableNames(item_sql, item_config["database"])))
    # pprint.pprint(getSearchResult(item_sql, 'rock', getAllTableNames(item_sql, item_config["database"])))
    # pprint.pprint(getSearchResult(item_sql, 'wide', getAllTableNames(item_sql, item_config["database"])))
    # pprint.pprint(getItemInfo(item_sql, "B0053TJJR8", "Tools_and_Home_Improvement"))
    end = time.clock()
    log.info("func getSearchResult item_sql exec time: {}".format(end - start))

    # 获取Item Info
    # pprint.pprint(getItemInfo(item_sql, "B009XBQEIO", "book"))

    # pprint.pprint(getTopNHotItems(hot_item_handle, 10))
    #
    # createUserBehavior(user_behavior_sql, "A8D92CT3UVIWY")
    # saveUserBehavior(user_behavior_sql, "A1MOVM99QR3SMO", "B002R0Z2RM", ",Automotive", 1)

    print("================")
    tables = getAllTableNames(item_sql, 'item_categories')
    print(tables)
    print("=============")

    # 添加索引
    def addindex(handle, tables):
        for table_name in tables:
            sql = "create index item_id_index on {}(`item id`)".format(table_name)
            handle.exe(sql)

    addindex(item_sql, tables)
