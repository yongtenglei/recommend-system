import json
import os
import numpy as np
import tensorflow as tf

# 设置环境变量， cuda = -1 表示 TF 训练，推理运行在CPU上
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

# 定义负样本大小
NEGTIVE_SAMPLE_SIZE = 50
# 定义 用户规模、 商品规模 ，这里设置成一个很大的数字
USER_SIZE, ITEM_SIZE = 333260, 3039917


class NCF:
    def __init__(self, rating_path, model_path, user_dict_path, item_dict_path):
        # 用户id与用户index映射的字典文件路径
        self.user_dict_path_ = user_dict_path
        # 商品id与商品index映射的字典文件路径
        self.item_dict_path_ = item_dict_path
        #创建TF会话
        self.sess = tf.Session()
        # 做一些加载模型的初始化工作
        self.__loadModel(model_path)

        # 获取模型的输入输出节点
        self.user_onehot = self.sess.graph.get_tensor_by_name('input/user_onehot:0')
        self.item_onehot = self.sess.graph.get_tensor_by_name('input/item_onehot:0')
        self.TopKV2 = self.sess.graph.get_tensor_by_name('evaluation/TopKV2:1')

        # 加载用户id与用户index映射字典
        self.uid_dict = json.load(open(self.user_dict_path_, "r"))
        # 加载商品id与商品index映射的字典
        self.mid_dict = json.load(open(self.item_dict_path_, "r"))

        self._item_string_list = list(self.mid_dict.keys())
        self._item_index_list = list(self.mid_dict.values())

    def __loadModel(self, model_path):
        tf.Graph().as_default()
        output_graph_def = tf.GraphDef()
        # 打开PB模型，并导入图
        with open(model_path, 'rb') as f:
            output_graph_def.ParseFromString(f.read())
            tf.import_graph_def(output_graph_def, name="")

    # 模型前向传播时对输入数据的检查与用户ID到user index，商品ID到商品index的一个转换
    def __forward(self, user_input, item_input):
        userindex = 0
        if user_input in self.uid_dict.keys():
            userindex = int(self.uid_dict[user_input])
        itemindex = 0
        if item_input in self.mid_dict.keys():
            itemindex = int(self.mid_dict[item_input])
        return userindex, itemindex

    # 模型后处理 模型输出的商品index 映射到商品ID
    def __postProcess(self, net_output, item_pool):
        prediction = np.take(item_pool, net_output)
        re_list = []
        for k in prediction:
            re_list.append(self._item_string_list[k])
        return re_list

    # 某个商品ID 转换成OneHot表示
    def __transformOneHot(self, labels, size):
        result = []
        for item in labels:
            one_hot = np.zeros(size)
            if item < size:
                one_hot[item] = 1
            result.append(one_hot)
        return result

    # 模型前处理
    def __preProcess(self, user_input, item_input):
        # 输入数据预处理
        user_input, item_input = self.__forward(user_input, item_input)
        # print(user_input, item_input)
        feature_user, feature_item, labels_add, feature_dict = [], [], [], {}

        feature_user.append(user_input)
        feature_item.append(item_input)
        labels_add.append(item_input)

        neg_samples = np.random.choice(ITEM_SIZE, NEGTIVE_SAMPLE_SIZE).tolist()

        for k in neg_samples:
            feature_user.append(user_input)
            feature_item.append(k)
            labels_add.append(k)

        embedding_user = self.__transformOneHot(feature_user, USER_SIZE)
        embedding_item = self.__transformOneHot(feature_item, ITEM_SIZE)

        return embedding_user, embedding_item, feature_item

    # 模型推理
    def process(self, user_input, item_input, list_size=50):
        embedding_user, embedding_item, item_pool = self.__preProcess(user_input, item_input)
        net_output = self.sess.run([self.TopKV2], feed_dict={
            self.user_onehot: embedding_user,
            self.item_onehot: embedding_item,
        })

        net_output = net_output[0][0:list_size]
        result = self.__postProcess(net_output, item_pool)
        return result


if __name__ == '__main__':
    rating_path = '/opt/shared/recommend/ncf/ratings.dat'
    model_path = '/opt/shared/recommend/ncf/ncf.pb'
    user_dict_path = '/opt/shared/recommend/ncf/ranking_user.json'
    item_dict_path = '/opt/shared/recommend/ncf/ranking_item.json'
    ncf = NCF(rating_path, model_path, user_dict_path, item_dict_path)

    userid = "A10JPTQTDNTV43"
    itemid = "B000CSRJMC"
    list_size = 10  # list_size<50
    for i in range(1):
        result = ncf.process(userid, itemid, list_size)
        print(result)
