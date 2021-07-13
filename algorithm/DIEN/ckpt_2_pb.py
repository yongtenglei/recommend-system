#coding=UTF-8<code>   
import tensorflow as tf
import numpy as np
import sys
#sys.path.append('./script')
from tensorflow.python.framework import graph_util
from tensorflow.python.platform import gfile
from tensorflow.python import pywrap_tensorflow
from data_iterator import DataIterator


from train import prepare_data


# 指定输出的节点名称，该节点名称必须是原模型中存在的节点
# PS：注意节点名称，应包含name_scope 和 variable_scope命名空间，并用“/”隔开，
def ckpt2pb(input_checkpoint, output_graph, output_node_name):
    # 检查目录下的ckpt文件状态是否可以用
    ckpt = tf.train.get_checkpoint_state(input_checkpoint)
    # 首先通过下面函数恢复图
    saver = tf.train.import_meta_graph(ckpt.model_checkpoint_path  + '.meta')
    # 然后通过下面函数获得默认的图
    graph = tf.get_default_graph()
    #打印操作节点名称
    tensor_name_list = [tensor.name for tensor in graph.as_graph_def().node]
    for tensor_name in tensor_name_list:
        print (tensor_name)
    # 返回一个序列化的图代表当前的图
    input_graph_def = graph.as_graph_def()

    with tf.Session() as sess:
        # 加载已经保存的模型，恢复图并得到数据
        saver.restore(sess, ckpt.model_checkpoint_path)
        # 在保存的时候，通过下面函数来指定需要固化的节点名称
        output_graph_def = graph_util.convert_variables_to_constants(
            # 模型持久化，将变量值固定
            sess=sess,
            input_graph_def=input_graph_def,  # 等于：sess.graph_def
            # freeze模型的目的是接下来做预测，
            # 所以 output_node_names一般是网络模型最后一层输出的节点名称，或者说我们预测的目标
            output_node_names=output_node_name.split(',')  # 如果有多个输出节点，以逗号隔开
        )

        with tf.gfile.GFile(output_graph, 'wb') as f:  # 保存模型
            # 序列化输出
            f.write(output_graph_def.SerializeToString())
        # # 得到当前图有几个操作节点
        print('%d ops in the final graph' % (len(output_graph_def.node)))

        # 这个可以得到各个节点的名称，如果断点调试到输出结果，看看模型的返回数据
        # 大概就可以猜出输入输出的节点名称
        for op in graph.get_operations():
            print(op.name)
            # print(op.name, op.values())

#打印ckpt的节点和shape
def read_node_name(input_checkpoint):

    ckpt = tf.train.get_checkpoint_state(input_checkpoint)
    reader = pywrap_tensorflow.NewCheckpointReader(ckpt.model_checkpoint_path)
    var_to_shape_map = reader.get_variable_to_shape_map()
    for key in var_to_shape_map:
        res = reader.get_tensor(key)
        print("tensor_name: ", key)
        print("a.shape:%s"%[res.shape])

#打印pb文件的输入输出节点
def check_pb_outnode_name(input_pb):
    # 读取并创建一个图graph来存放训练好的模型
    with tf.gfile.FastGFile(input_pb, 'rb') as f:
        # 使用tf.GraphDef() 定义一个空的Graph
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        # Imports the graph from graph_def into the current default Graph.
        tf.import_graph_def(graph_def, name='')

    tensor_name_list = [tensor.name for tensor in
                        tf.get_default_graph().as_graph_def().node]
    for tensor_name in tensor_name_list:
        print(tensor_name)


#pb转换为pbtxt
def convert_pb_to_pbtxt(input_pb):
    with gfile.FastGFile(input_pb, 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        tf.import_graph_def(graph_def, name='')
        tf.train.write_graph(graph_def, './', 'protobuf.pbtxt', as_text=True)


#test pb模型.
def pb_graph_infer(pb_path, test_file, uid_voc, mid_voc, cat_voc, batchSize = 1, maxLen = 8):
    
    with tf.Graph().as_default():
        output_graph_def = tf.GraphDef()
        with open(pb_path, 'rb') as f:
            output_graph_def.ParseFromString(f.read())
            # 恢复模型，从读取的序列化数据中导入网络结构即可
            tf.import_graph_def(output_graph_def, name="")
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())

            # 定义输入的张量名称，对应网络结构的输入张量
            # Inputs/mid_his_batch_ph:0 
            # Inputs/cat_his_batch_ph:0
            # Inputs/uid_batch_ph:0
            # Inputs/mid_batch_ph:0
            # Inputs/cat_batch_ph:0
            # Inputs/mask:0
            # Inputs/seq_len_ph:0
            mid_his_batch_ph = sess.graph.get_tensor_by_name('Inputs/mid_his_batch_ph:0')
            cat_his_batch_ph = sess.graph.get_tensor_by_name('Inputs/cat_his_batch_ph:0')
            uid_batch_ph = sess.graph.get_tensor_by_name('Inputs/uid_batch_ph:0')
            mid_batch_ph = sess.graph.get_tensor_by_name('Inputs/mid_batch_ph:0')
            cat_batch_ph = sess.graph.get_tensor_by_name('Inputs/cat_batch_ph:0')
            mask = sess.graph.get_tensor_by_name('Inputs/mask:0')
            seq_len_ph = sess.graph.get_tensor_by_name('Inputs/seq_len_ph:0')
            # 定义输出的张量名称:注意为节点名称 + “：”+id好
            output_prob = sess.graph.get_tensor_by_name('Softmax_2:0')

            # 准备测试样本
            test_data = DataIterator(test_file, uid_voc, mid_voc, cat_voc, batchSize, maxLen)
            for src, tgt in test_data:
                uids, mids, cats, mid_his, cat_his, mid_mask, target, sl, noclk_mids, noclk_cats = prepare_data(src, tgt, return_neg=True)
                probs = sess.run([output_prob], feed_dict = {
                                uid_batch_ph : uids,
                                mid_batch_ph : mids,
                                cat_batch_ph : cats,
                                mid_his_batch_ph : mid_his,
                                cat_his_batch_ph : cat_his,
                                mask : mid_mask,
                                seq_len_ph : sl, 
                }) 
                print(probs)

if __name__ == "__main__":
    # 输入ckpt模型路径
    #input_checkpoint = "./model/"
    #out_pb_path = "./model/DIEN.pb"
    #output_node_name = "Softmax_2"

    # 读取节点名称
    #read_node_name(input_checkpoint)

    # 调用freeze_graph将ckpt转pb
    #ckpt2pb(input_checkpoint, out_pb_path, output_node_name)

    # 打印pb模型的输出节点
    #check_pb_outnode_name(out_pb_path)
    
    #pb to pbtxt
    #convert_pb_to_pbtxt(out_pb_path)

    # 测试pb模型
    test_file = "./local_test_splitByUser"
    uid_voc = "./uid_voc.pkl" 
    mid_voc = "./mid_voc.pkl" 
    cat_voc = "./cat_voc.pkl" 
    #pb_graph_infer(out_pb_path, test_file, uid_voc, mid_voc, cat_voc)
