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

import redis
from plugin.log import log

class Redis:
  def __init__(self, config):
    # log.debug("init redis Host:{} Port:{}".format(config["host"], config["port"]))
    pool = redis.ConnectionPool(host=config["host"], 
                                port=config["port"], 
                                db=config["database"],
                                decode_responses=True)
    self.connection = redis.Redis(connection_pool=pool)
  
  def set(self, key, value):
    if type(value) == list:
      for val in value:
        self.connection.lpush(key, val)
    elif type(value) == set:
      for val in value:
        self.connection.sadd(key, val)
    elif type(value) == dict or type(value) == tuple:
      pass
    else:
      self.connection.set(key, value)

  def get(self, key):
    key_type = self.connection.type(key)
    if key_type == "list":
      return self.connection.lrange(key, 0, -1)
    elif key_type == "string": 
      return self.connection.get(key)
    elif key_type == "set":
      return self.connection.getset(key)
    return None

  def empty(self):
    for key in self.connection.keys():
      self.connection.delete(key)
  
  def getAllValue(self):
    result = []
    for key in self.connection.keys():
      key_type = self.connection.type(key)
      if key_type == "list":
        result.append((key, self.connection.lrange(key, 0, -1)))
      elif key_type == "string": 
        result.append((key, [self.connection.get(key)]))
      elif key_type == "set":
        result.append((key, [self.connection.getset(key)]))
      else:
        pass
    return result

  def increase(self, key):
    self.connection.incr(key)


if __name__ == '__main__':
  import pprint
  config = {
    "host": "192.168.0.89",
    "port": 6379,
    "database": 2,
  }
  # category = ""
  # itemid = ""
  keys = ["1623313844,phone", "1623314174,phone",
          "1623310671,phone", "B000095RB4,Home_Improvement",
          "B000JHO4CY,Video_Games"]

  my_redis = Redis(config)

  my_redis.empty()

  result = my_redis.getAllValue()
  pprint.pprint(result)


  for key in keys:
    if not my_redis.get(key):
      my_redis.set(key, 50)
    else:
      my_redis.increase(key)
  result = my_redis.getAllValue()
  # my_redis.empty()
  print("-----------------------------------------")
  pprint.pprint(result)
