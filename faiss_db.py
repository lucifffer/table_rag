import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import codecs
import json

# ===================== 配置 =====================
# 向量模型（输出维度384，固定不变）
EMBEDDING_MODEL = "/mnt/data/oss/models/bge-m3"
# FAISS索引类型（FlatL2：精准检索，适合小数据量，100%匹配）
INDEX_TYPE = "FlatL2"
# ================================================

class RowWiseFAISSDB:
    def __init__(self):
        # 加载向量模型
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        # 向量维度（必须和模型匹配，all-MiniLM-L6-v2=384）
        self.dim = self.model.get_sentence_embedding_dimension()
        # 初始化FAISS索引
        self.index = faiss.IndexFlatL2(self.dim)
        # 元数据：索引id → 行信息（page页码、row_num行号、text原文）
        self.metadata: List[Dict] = []

    def add_row(self, text: str):
        """
        核心：添加【单行文本】到向量库
        :param page: 页码
        :param row_num: 行号
        :param text: 单行文本内容
        """
        if not text.strip():  # 过滤空行
            return
        
        # 1. 对【单行文本】生成向量
        vector = self.model.encode([text.strip()])[0]
        # 转换为faiss要求的float32格式
        vector = np.array([vector], dtype=np.float32)
        
        # 2. 添加向量到FAISS索引
        self.index.add(vector)
        
        # 3. 绑定元数据（索引ID自动递增，与向量一一对应）
        self.metadata.append({
            "text": text.strip()
        })

    def build_from_mineru_data(self, structured_data):
        """
        从MinerU解析结果中，【逐行】构建向量库
        :param structured_data: mineru_parse_local_pdf 返回的结构化数据
        """
        for line in structured_data:
            self.add_row(text=line)
        self.save_db()
        with codecs.open('metadata.json', 'w', encoding='utf-8') as dump_f:
            json.dump(self.metadata,dump_f, ensure_ascii=False)
        # for page_data in structured_data:
        #     page_num = page_data["page"]
        #     # 按换行符分割，逐行处理
        #     raw_lines = page_data["raw_text"].split("\n")
        #     for row_idx, line in enumerate(raw_lines, 1):
        #         self.add_row(
        #             text=line
        #         )
        print(f"✅ 逐行向量库构建完成：总行数={self.index.ntotal}")

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        检索：输入问题，召回最相似的【行】
        :return: 带页码、行号、原文、相似度的结果
        """
        if self.index.ntotal == 0:
            return []
        
        # 问题生成向量
        query_vec = self.model.encode([query])
        query_vec = np.array(query_vec, dtype=np.float32)
        # FAISS检索（返回距离+索引ID）
        distances, indices = self.index.search(query_vec, top_k)
        # 组装结果（通过ID取回元数据）
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.metadata):
                res = self.metadata[idx].copy()
                res["similarity"] = 1 - (dist / 2)  # 距离转相似度
                results.append(res)
        return results

    def save_db(self, save_path: str = "row_wise_faiss.index"):
        """保存向量库到本地"""
        faiss.write_index(self.index, save_path)
        # 元数据可单独用json保存（自行扩展）
        print(f"💾 向量库已保存：{save_path}")

    def load_db(self, load_path: str = "row_wise_faiss.index"):
        """加载本地向量库"""
        self.index = faiss.read_index(load_path)
        print(f"📂 向量库已加载：{load_path}")

