
import asyncio
from typing import List
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

# 自动从当前目录的 .env 文件加载！
load_dotenv()

# 初始化异步客户端
aclient = AsyncOpenAI(
    api_key=os.getenv("EMBEDDING_API_KEY"),
    base_url=os.getenv("EMBEDDING_BASE_URL")
)


async def embed_single(text: str, semaphore: asyncio.Semaphore) -> List[float]:
    """单个异步向量化，受信号量控制并发数"""
    async with semaphore:
        try:
            response = await aclient.embeddings.create(
                model=os.getenv('EMBEDDING_MODEL_NAME'),
                input=text,
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding error: {e}")
            return []


async def embed_chunks_concurrent(chunks: List[str], max_concurrency=10) -> List[List[float]]:
    """
    高并发批量向量化
    :param chunks: 文本列表
    :param max_concurrency: 最大并发数（根据API限制调整）
    """
    semaphore = asyncio.Semaphore(max_concurrency)
    tasks = [embed_single(chunk, semaphore) for chunk in chunks]
    # 等待所有任务完成
    return await asyncio.gather(*tasks)