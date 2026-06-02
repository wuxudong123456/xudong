import re
import os
import numpy as np
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

class SanguoProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.chapters = []

    def parse_chapters(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        pattern = r'([第][零一二三四五六七八九十百]+[回]\s+.+?)(?=[第][零一二三四五六七八九十百]+[回]|$)'
        matches = re.finditer(pattern, content, re.DOTALL)

        for match in matches:
            chapter_content = match.group(1).strip()
            if not chapter_content:
                continue

            title_match = re.match(r'([第][零一二三四五六七八九十百]+[回]\s+.+)', chapter_content)
            if title_match:
                title = title_match.group(1).strip()
                content_start = len(title)
                text = chapter_content[content_start:].strip()
            else:
                title = chapter_content[:50]
                text = chapter_content

            text = self.clean_text(text)
            chapter_num = self.extract_chapter_number(title)

            self.chapters.append({
                'chapter_num': chapter_num,
                'title': title,
                'content': text
            })

        print(f"共解析出 {len(self.chapters)} 章")
        return self.chapters

    def clean_text(self, text):
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    def extract_chapter_number(self, title):
        num_str = re.search(r'第([零一二三四五六七八九十百]+)回', title)
        if num_str:
            num_char = num_str.group(1)
            num_map = {'零':0, '一':1, '二':2, '三':3, '四':4, '五':5, '六':6, '七':7, '八':8, '九':9, '十':10, '百':100}
            result = 0
            temp = 0
            for c in num_char:
                if c == '十':
                    temp = temp * 10 + 10 if temp > 0 else 10
                elif c == '百':
                    temp = (temp if temp > 0 else 1) * 100
                else:
                    temp = temp * 10 + num_map[c]
                result = temp
            return result
        return len(self.chapters) + 1

class VectorGenerator:
    def __init__(self, vector_dim=64):
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.svd = TruncatedSVD(n_components=vector_dim)
        self.vector_dim = vector_dim
        self.fitted = False

    def fit(self, texts):
        print(f"正在使用TF-IDF生成{self.vector_dim}维向量...")
        X = self.vectorizer.fit_transform(texts)
        self.svd.fit(X)
        self.fitted = True
        print("向量模型训练完成")

    def transform(self, texts):
        if not self.fitted:
            self.fit(texts)
        X = self.vectorizer.transform(texts)
        return self.svd.transform(X)

class MilvusClient:
    def __init__(self, host='localhost', port='19530'):
        self.host = host
        self.port = port
        self.collection = None
        self.vector_generator = VectorGenerator(vector_dim=64)

    def connect(self):
        try:
            connections.connect(
                alias='default',
                host=self.host,
                port=self.port
            )
            print(f"成功连接到 Milvus: {self.host}:{self.port}")
        except Exception as e:
            print(f"连接失败: {e}")
            raise

    def create_collection(self, collection_name='sanguo', vector_dim=64):
        if utility.has_collection(collection_name):
            print(f"集合 {collection_name} 已存在，正在删除...")
            utility.drop_collection(collection_name)

        fields = [
            FieldSchema(name="chapter_num", dtype=DataType.INT64, is_primary=True),
            FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=200),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=vector_dim)
        ]

        schema = CollectionSchema(fields, description="三国演义章节数据")
        self.collection = Collection(name=collection_name, schema=schema)

        from pymilvus import Index
        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128}
        }
        self.collection.create_index(field_name="embedding", index_params=index_params)

        print(f"成功创建集合: {collection_name}, 向量维度: {vector_dim}")

    def insert_data(self, chapters):
        if not self.collection:
            raise Exception("请先创建集合")

        texts_to_embed = [f"{ch['title']} {ch['content'][:500]}" for ch in chapters]
        embeddings = self.vector_generator.transform(texts_to_embed)

        print(f"正在插入 {len(chapters)} 条数据...")
        print(f"每条向量维度: {embeddings.shape[1]}")
        print(f"向量总数: {embeddings.shape[0]}")

        entities = []
        for i, ch in enumerate(chapters):
            entities.append({
                "chapter_num": ch['chapter_num'],
                "title": ch['title'],
                "content": ch['content'],
                "embedding": embeddings[i].tolist()
            })

        result = self.collection.insert(entities)
        self.collection.flush()
        self.collection.load()
        print(f"成功插入 {len(chapters)} 条数据")
        return result

    def verify_data(self):
        if not self.collection:
            raise Exception("请先创建集合")

        stats = self.collection.num_entities
        print(f"集合中当前数据量: {stats}")

        result = self.collection.query(
            expr="chapter_num >= 1",
            limit=3,
            output_fields=["chapter_num", "title", "content"]
        )

        print("\n验证数据示例:")
        for item in result:
            print(f"章节: {item['chapter_num']}")
            print(f"标题: {item['title']}")
            print(f"内容预览: {item['content'][:100]}...")
            print("-" * 50)

def main():
    file_path = r'd:\项目阶段\项目课0505\RAG讲义\test_demo\三国演义\《三国演义》(1).txt'

    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return

    processor = SanguoProcessor(file_path)
    chapters = processor.parse_chapters()

    if not chapters:
        print("未解析到章节数据")
        return

    client = MilvusClient(host='localhost', port='19530')

    try:
        client.connect()
        client.create_collection('sanguo', vector_dim=64)
        client.insert_data(chapters)
        client.verify_data()
        print("\n任务完成！三国演义已成功切片并入库到Milvus。")
    except Exception as e:
        print(f"执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        connections.disconnect('default')

if __name__ == "__main__":
    main()