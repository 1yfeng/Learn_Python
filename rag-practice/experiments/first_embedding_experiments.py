from sentence_transformers import SentenceTransformer, util

class FirstEmbeddingExperiment:
    def embedding_experiment(self):
        # model = SentenceTransformer('all-MiniLM-L6-v2')
        # sentences = ["Steve Jobs holding an Apple phone","The cat is running on the grass", "The little cat is playing", "I like to eat apple"]
        model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
        sentences = ["乔布斯发布苹果新品","猫在草地上跑", "那只小猫在玩耍", "我喜欢吃苹果", "皇后","狗在沙发上睡觉",  "男人", "国王"]
        query = "宠物正在休息"
        embeddings = model.encode(sentences, convert_to_tensor=True)
        query_embedding = model.encode(query, convert_to_tensor=True)
        print(f"embeddings:{embeddings.shape}")
        print(embeddings)
        cosine_scores = util.cos_sim(query_embedding, embeddings)
        print(cosine_scores)




if __name__ == "__main__":
    exp = FirstEmbeddingExperiment()
    exp.embedding_experiment()