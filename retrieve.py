import asyncio
from typing import List, Optional
from embedding import embed_chunks_concurrent
from chromadbinit import chromadb_collection
from docstore import doc_store
from rerank import rerank_async
from dotenv import load_dotenv
import os

# 自动从当前目录的 .env 文件加载！
load_dotenv()


async def retrieve(query: str, top_k: int = 3) -> Optional[List[str]]:
    """
    RAG 检索全流程。增加阈值过滤，低于阈值返回 None。
    """

    # --- 阶段 1: 向量召回 (Recall) ---
    recall_factor = 10  # 稍微加大召回范围，给 Rerank 更多选择
    initial_k = top_k * recall_factor

    query_embeddings = await embed_chunks_concurrent([query])
    query_embedding = query_embeddings[0]

    # Chroma 查询
    results = chromadb_collection.query(
        query_embeddings=[query_embedding],
        n_results=initial_k
    )

    if not results['metadatas'] or not results['metadatas'][0]:
        return None

    # --- 阶段 2: 父级回溯 (Map to Parents) ---
    parent_ids = set()
    found_metadatas = results['metadatas'][0]

    unique_parent_ids = []
    for meta in found_metadatas:
        pid = meta.get('parent_id')
        if pid and pid not in parent_ids:
            parent_ids.add(pid)
            unique_parent_ids.append(pid)

    candidate_parents = []
    for pid in unique_parent_ids:
        content = doc_store.get_parent(pid)
        if content:
            candidate_parents.append(content)

    if not candidate_parents:
        return None

    # --- 阶段 3: 重排序 (Rerank) ---
    print(f"正在重排 {len(candidate_parents)} 条候选文档...")
    try:
        rerank_resp = await rerank_async(query, candidate_parents)
        ranked_results = rerank_resp.get('results', [])

        if not ranked_results:
            return None

        # 按分数降序排列
        ranked_results.sort(key=lambda x: x['relevance_score'], reverse=True)

        final_docs = []

        for item in ranked_results:
            score = item['relevance_score']
            index = item['index']
            content = candidate_parents[index]

            # 打印前几条的分数，方便你调整阈值
            # preview = content[:800].replace('\n', ' ')
            # print(f"分数: {score:.4f} | 内容: {preview}")

            # 阈值过滤
            if score <= float(os.getenv('RERANK_THRESHOLD')):
                continue

            final_docs.append(content)

            # 凑够了 top_k 个就停止
            if len(final_docs) >= top_k:
                break

        # 如果所有文档都被过滤掉了
        if not final_docs:
            print(f"⚠️ 所有结果均低于阈值 ({float(os.getenv('RERANK_THRESHOLD'))})，判定为无相关信息，请降低阈值！")
            return None

        return final_docs

    except Exception as e:
        print(f"Rerank 失败: {e}")
        return candidate_parents[:top_k]


if __name__ == "__main__":
    query = "多久交付？"
    result = asyncio.run(retrieve(query, top_k=3))

    if result is None:
        print("未找到相关文档！")
    else:
        for i, doc in enumerate(result):
            print(f"[{i}] {doc}")
