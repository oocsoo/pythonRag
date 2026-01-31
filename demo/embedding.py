from openai import OpenAI
from typing import List


def embed_chunk(chunk: str) -> List[float]:
    """
    块向量化
    :param chunk: 块
    :return: 向量列表
    """
    client = OpenAI(
        api_key="sk-xcvozhsdzgyqfzihvdazadzetwtcaijgyqwsgqvpdaqewuoe",
        base_url="https://api.siliconflow.cn/v1"
    )

    response = client.embeddings.create(
        # 模型名称
        model="Qwen/Qwen3-Embedding-8B",
        input=chunk,
        # 可选：float 或 base64
        encoding_format="float"
    )
    # 获取嵌入向量
    return response.data[0].embedding
