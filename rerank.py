
import aiohttp
import asyncio
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
import os

# 自动从当前目录的 .env 文件加载！
load_dotenv()


async def _rerank_batch(session: aiohttp.ClientSession, query: str, docs: List[str], start_index: int) -> List[Dict]:
    """
    处理单个批次的 Rerank 请求
    :param start_index: 该批次在原列表中的起始下标，用于修正返回结果的 index
    """
    payload = {
        "model": os.getenv('RERANK_MODEL_NAME'),
        "query": query,
        "documents": docs,
        "top_n": len(docs)  # 让它返回所有结果的分数，我们自己排序
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('RERANK_API_KEY')}",
        "Content-Type": "application/json"
    }

    try:
        async with session.post(os.getenv('RERANK_BASE_URL'), json=payload, headers=headers) as response:
            if response.status != 200:
                text = await response.text()
                print(f"Rerank API Error: {text}")
                return []

            result = await response.json()
            results = result.get('results', [])

            # 修正 index：API 返回的 index 是相对于当前批次的 (0-batch_size)，我们需要加上 offset
            for item in results:
                item['index'] += start_index

            return results
    except Exception as e:
        print(f"Batch request failed: {e}")
        return []


async def rerank_async(query: str, documents: List[str], batch_size: int = 20) -> Dict[str, Any]:
    """
    异步并发 Rerank
    :param query: 用户问题
    :param documents: 候选文档列表
    :param batch_size: 每个请求处理多少个文档 (并发切分)
    """
    if not documents:
        return {"results": []}

    async with aiohttp.ClientSession() as session:
        tasks = []
        # 将文档列表切分为多个 batch，并发请求
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i: i + batch_size]
            task = _rerank_batch(session, query, batch_docs, start_index=i)
            tasks.append(task)

        # 等待所有批次完成
        batch_results = await asyncio.gather(*tasks)

    # 合并所有批次的结果
    all_results = []
    for res in batch_results:
        all_results.extend(res)

    # 重新按照分数从高到低排序 (因为并发返回顺序不一定)
    all_results.sort(key=lambda x: x['relevance_score'], reverse=True)

    return {"results": all_results}


