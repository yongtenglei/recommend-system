import dataflow

if __name__ == "__main__":
  model_path = "/opt/shared/recommend/Wide.cambricon"
  uid_path = "/opt/shared/recommend/uid_voc.json" 
  mid_path = "/opt/shared/recommend/mid_voc.json" 
  cat_path = "/opt/shared/recommend/cat_voc.json" 
  uid_embdding_path = "/opt/shared/recommend/uid_embeddings.json"
  mid_embdding_path = "/opt/shared/recommend/mid_embeddings.json"
  cat_embdding_path = "/opt/shared/recommend/cat_embeddings.json"
  func_name = "subnet0"
  dev_id = 0
  #init
  ranking = dataflow.Ranking(model_path, func_name, uid_path, mid_path, cat_path, uid_embdding_path, mid_embdding_path, cat_embdding_path, dev_id)
  user_info = dataflow.UserInfo()

  #infer  
  user_info.user = 'A2YII0ICP99QYQ'
  user_info.item = 'B00CUSSKUM'
  user_info.category = 'Contemporary Women'
  user_info.history_behaviors = [('B004U3SWB2', 'Basic Cases') ,('B005SJBIVI', 'Screen Protectors'), ('B005SUHRVC', 'Basic Cases'), ('B006VWV956', 'Data Cables'), ('B008C6ASV0', 'Basic Cases')]

  ctr = ranking.process([user_info])
  print(ctr)

  user_info.user = 'A2YII0ICP99QYQ'
  user_info.item = 'B005SUHRVC'
  user_info.category = 'Basic Cases'
  user_info.history_behaviors = [('B004U3SWB2', 'Basic Cases') ,('B005SJBIVI', 'Screen Protectors'), ('B005SUHRVC', 'Basic Cases'), ('B006VWV956', 'Data Cables'), ('B008C6ASV0', 'Basic Cases')]
  for i in range(100):
    ctr = ranking.process([user_info])
    print(ctr)

