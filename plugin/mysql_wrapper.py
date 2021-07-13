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

import pymysql
from DBUtils.PooledDB import PooledDB



class MySQL:
    def __init__(self, config, maxconnections=10):
        # log.debug("init mysql Host:{} Port:{} Using db:{}".format(config['host'], config["port"], config["database"]))
        self.__pool = PooledDB(pymysql,
                               maxconnections,
                               host=config["host"],
                               user=config["user"],
                               port=config["port"],
                               passwd=config["password"],
                               db=config["database"],
                               use_unicode=True)
        # log.debug("mysql PooledDB Init")

    def fetchOneDB(self, sql):
        con = self.__pool.connection()
        cur = con.cursor()
        cur.execute(sql)
        result = cur.fetchone()
        if result:
            fields = [tup[0] for tup in cur._cursor.description]
            result = dict(zip(fields, result))
        return result

    def fetchAllDB(self, sql):
        con = self.__pool.connection()
        cur = con.cursor()
        cur.execute(sql)
        result = cur.fetchall()
        if result:
            fields = [tup[0] for tup in cur._cursor.description]
            result = [dict(zip(fields, row)) for row in result]
        return result

    def exe(self, sql):
        con = self.__pool.connection()
        cur = con.cursor()
        cur.execute(sql)
        con.commit()


if __name__ == '__main__':
    import pprint
    from plugin import item_config

    # item_sql = MySQL(item_config, maxconnections=10)
    # search_condition = "select * from book limit 5"
    # users = item_sql.fetchOneDB(search_condition)
    # users = [users]
    # for user in users:
    #     pprint.pprint(user)

    # 查用户
    from plugin import user_config
    user_sql = MySQL(user_config)
    search_condition = "select * from user limit 5"
    users = user_sql.fetchOneDB(search_condition)
    users = [users]
    for user in users:
        pprint.pprint(user)