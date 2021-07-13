import tensorflow as tf
import numpy as np
import sys
from tensorflow.python.framework import graph_util
from tensorflow.python.platform import gfile
from tensorflow.python import pywrap_tensorflow
import json

class RankingTF:
  def __init__(self, model_name, pb_path, uid_voc, mid_voc, cat_voc):
    if model_name != "DIEN" and model_name != "WIDE":
      raise AssertionError("model need set to : DIEN or WIDE")  
    else: 
      self.model_name = model_name    

    self.sess = tf.Session()

    self.__uid_dict = self.__creatWord2RankDicts(uid_voc)
    self.__mid_dict = self.__creatWord2RankDicts(mid_voc)
    self.__cat_dict = self.__creatWord2RankDicts(cat_voc)

    self.__loadModel(pb_path)
    
    if self.model_name== "DIEN":            
      self.mid_his_batch_ph = self.sess.graph.get_tensor_by_name('Inputs/mid_his_batch_ph:0')
      self.cat_his_batch_ph = self.sess.graph.get_tensor_by_name('Inputs/cat_his_batch_ph:0')
      self.uid_batch_ph = self.sess.graph.get_tensor_by_name('Inputs/uid_batch_ph:0')
      self.mid_batch_ph = self.sess.graph.get_tensor_by_name('Inputs/mid_batch_ph:0')
      self.cat_batch_ph = self.sess.graph.get_tensor_by_name('Inputs/cat_batch_ph:0')
      self.mask = self.sess.graph.get_tensor_by_name('Inputs/mask:0')
      self.seq_len_ph = self.sess.graph.get_tensor_by_name('Inputs/seq_len_ph:0')           
      self.output_prob = self.sess.graph.get_tensor_by_name('Softmax_2:0')
    else: #WIDE
      self.mid_his_batch_ph = self.sess.graph.get_tensor_by_name('Inputs/mid_his_batch_ph:0')
      self.cat_his_batch_ph = self.sess.graph.get_tensor_by_name('Inputs/cat_his_batch_ph:0')
      self.uid_batch_ph = self.sess.graph.get_tensor_by_name('Inputs/uid_batch_ph:0')
      self.mid_batch_ph = self.sess.graph.get_tensor_by_name('Inputs/mid_batch_ph:0')
      self.cat_batch_ph = self.sess.graph.get_tensor_by_name('Inputs/cat_batch_ph:0')
      self.output_prob = self.sess.graph.get_tensor_by_name('Softmax:0')
 
  def __creatWord2RankDicts(self, filename):
    return json.load(open(filename, "rb"))

  def __loadModel(self, pb_path):
    tf.Graph().as_default()
    output_graph_def = tf.GraphDef()
    with open(pb_path, 'rb') as f:
      output_graph_def.ParseFromString(f.read())
      tf.import_graph_def(output_graph_def, name="")

  def __getNetInputs(self, batch_data):
    his_lenths = [len(s[4]) for s in batch_data]
    seqs_mid = [inp[3] for inp in batch_data]
    seqs_cat = [inp[4] for inp in batch_data]
    n_samples = len(seqs_mid)
    maxlen = np.max(his_lenths)

    his_items_id = np.zeros((n_samples, maxlen)).astype('int64')
    his_categories_id = np.zeros((n_samples, maxlen)).astype('int64')
    his_mask = np.zeros((n_samples, maxlen)).astype('float32')
    for idx, [s_x, s_y] in enumerate(zip(seqs_mid, seqs_cat)):
      his_mask[idx, :his_lenths[idx]] = 1.
      his_items_id[idx, :his_lenths[idx]] = s_x
      his_categories_id[idx, :his_lenths[idx]] = s_y

    users_id = np.array([inp[0] for inp in batch_data])
    items_id = np.array([inp[1] for inp in batch_data])
    categories_id = np.array([inp[2] for inp in batch_data])

    return [users_id, items_id, categories_id, his_items_id, his_categories_id, his_mask, np.array(his_lenths)]

  def __preproc(self, usr_infos):
    batch_data = []
    #map words to ranks by dicts
    for usr_info in usr_infos:
      user_id = self.__uid_dict[usr_info[0]] if usr_info[0] in self.__uid_dict.keys() else 0
      item_id = self.__mid_dict[usr_info[1]] if usr_info[1] in self.__mid_dict.keys() else 0
      category_id = self.__cat_dict[usr_info[2]] if usr_info[2] in self.__cat_dict.keys() else 0
      his_item_id = []
      his_category_id = []
      for his_pair in usr_info[3]:
        m = self.__mid_dict[his_pair[0]] if his_pair[0] in self.__mid_dict.keys() else 0
        c = self.__cat_dict[his_pair[1]] if his_pair[1] in self.__cat_dict.keys() else 0
        his_item_id.append(m)
        his_category_id.append(c)

      batch_data.append([user_id, item_id, category_id, his_item_id, his_category_id]) 

    return self.__getNetInputs(batch_data)

  def process(self, user_infos):
    net_inputs = self.__preproc(user_infos)
    '''
    self.uid_embeddings_var = self.sess.graph.get_tensor_by_name("uid_embedding_var:0")
    self.uid_batch_embedded = tf.nn.embedding_lookup(self.uid_embeddings_var, net_inputs[0])

    self.mid_embeddings_var = self.sess.graph.get_tensor_by_name("mid_embedding_var:0")
    self.mid_batch_embedded = tf.nn.embedding_lookup(self.mid_embeddings_var, net_inputs[1])
    self.mid_his_batch_embedded = tf.nn.embedding_lookup(self.mid_embeddings_var, net_inputs[3])

    self.cat_embeddings_var = self.sess.graph.get_tensor_by_name("cat_embedding_var:0")
    self.cat_batch_embedded = tf.nn.embedding_lookup(self.cat_embeddings_var, net_inputs[2])
    self.cat_his_batch_embedded = tf.nn.embedding_lookup(self.cat_embeddings_var, net_inputs[4])

    self.item_eb = tf.concat([self.mid_batch_embedded, self.cat_batch_embedded], 1)
    print("item_eb", self.sess.run(self.item_eb).shape)
    self.item_his_eb = tf.concat([self.mid_his_batch_embedded, self.cat_his_batch_embedded], 2)
    print("item_his_eb", self.sess.run(self.item_his_eb).shape)
    self.item_his_eb_sum = tf.reduce_sum(self.item_his_eb, 1)

    inp = tf.concat([self.uid_batch_embedded, self.item_eb, self.item_his_eb_sum], 1)
    print(self.sess.run(inp).shape)
    print("uid shape", self.sess.run(self.uid_embeddings_var).shape)
    print("mid shape", self.sess.run(self.mid_embeddings_var).shape)
    print("cat shape", self.sess.run(self.cat_embeddings_var).shape)
    print("uid batch_embedd", self.sess.run(self.uid_batch_embedded))
    print("mid batch_embedd", self.sess.run(self.mid_batch_embedded))
    print("cat batch_embedd", self.sess.run(self.cat_batch_embedded))
    print("his mid embedd", self.sess.run(self.mid_his_batch_embedded))
    print("cat cat embedd", self.sess.run(self.cat_his_batch_embedded))
    '''

    #infer        
    if self.model_name== "DIEN":                        
      prob = self.sess.run([self.output_prob], feed_dict = {
                       self.uid_batch_ph : net_inputs[0],
                       self.mid_batch_ph : net_inputs[1],
                       self.cat_batch_ph : net_inputs[2],
                       self.mid_his_batch_ph : net_inputs[3],
                       self.cat_his_batch_ph : net_inputs[4],
                       self.mask : net_inputs[5],
                       self.seq_len_ph : net_inputs[6], 
       })
    else:
      prob = self.sess.run([self.output_prob], feed_dict = {
                      self.uid_batch_ph : net_inputs[0],
                      self.mid_batch_ph : net_inputs[1],
                      self.cat_batch_ph : net_inputs[2],
                      self.mid_his_batch_ph : net_inputs[3],
                      self.cat_his_batch_ph : net_inputs[4],               
      })

    return prob[0][:,0].tolist()

if __name__ == "__main__":
    model_name = "WIDE"  #DIEN / WIDE
    pb_path = "/opt/shared/recommend/Wide.pb"
    uid_voc = "/opt/shared/recommend/uid_voc.json" 
    mid_voc = "/opt/shared/recommend/mid_voc.json" 
    cat_voc = "/opt/shared/recommend/cat_voc.json"
    #init
    ranking = RankingTF(model_name, pb_path, uid_voc, mid_voc, cat_voc)

    #infer  
    user_infos = [ 
        ['A2YII0ICP99QYQ', 'B00CUSSKUM', 'Contemporary Women', [('B004U3SWB2', 'Basic Cases') ,('B005SJBIVI', 'Screen Protectors'), ('B005SUHRVC', 'Basic Cases'), ('B006VWV956', 'Data Cables'), ('B008C6ASV0', 'Basic Cases')]]
        ]

    prob = ranking.process(user_infos)
    print(prob)
    user_infos = [ 
        ['A2YII0ICP99QYQ', 'B005SUHRVC', 'Basic Cases', [('B004U3SWB2', 'Basic Cases') ,('B005SJBIVI', 'Screen Protectors'), ('B005SUHRVC', 'Basic Cases'), ('B006VWV956', 'Data Cables'), ('B008C6ASV0', 'Basic Cases')]]
        ]
    prob = ranking.process(user_infos)
    print(prob)

