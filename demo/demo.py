
from to_chunk import split_into_chunks
from embedding import embed_chunk
from emb_save_db import save_embeddings
from retrieve import retrieve
from rerank import rerank


"""知识库处理存入向量数据库中！"""
# 将文件切成块！返回列表
# chunks = split_into_chunks('readme.md')
# print(chunks)
# # 每个块获取对应的向量！返回列表
# embeddings = [embed_chunk(chunk) for chunk in chunks]
#
# # 将块和其对应的向量存储到数据库中!
# save_embeddings(
#     chunks,
#     embeddings,
# )


"""用户提取从向量数据库中召回！"""

query = "双检索策略"
retrieved_chunks = retrieve(query, 3)
result = rerank(query, retrieved_chunks)

for i, chunk in enumerate(retrieved_chunks):
    print(f"[{i}] {chunk} \n")
print(result)

"""
#########输出结果########

[0] ### 💡 核心价值
- **智能记忆管理**：将原始数据转化为有价值的记忆知识
- **多模态支持**：统一处理文本、图像、音频、视频等多种格式
- **双检索策略**：结合 RAG 的高效性和 LLM 的深度理解
- **自演化能力**：记忆结构根据使用模式自适应优化
 

[1] ## 📖 项目概述 

[2] MemU 是一个面向 LLM 和 AI 智能体的记忆框架。它接收**多模态输入**（对话、文档、图像），将其提取为结构化记忆，并组织成**分层文件系统**，支持**基于嵌入的检索（RAG）** 和**非嵌入检索（LLM）**。 

{'id': '019c08453708704288a9b1a558b749d2', 'results': [{'index': 0, 'relevance_score': 0.6596528887748718}, {'index': 2, 'relevance_score': 0.0021518366411328316}, {'index': 1, 'relevance_score': 0.00012193472502985969}], 'meta': {'billed_units': {'input_tokens': 192, 'output_tokens': 0, 'search_units': 0, 'classifications': 0}, 'tokens': {'input_tokens': 192, 'output_tokens': 0}}}

"""