import requests
from typing import List


def rerank(query: str, documents: List[str]):
    """
    对结果进行重排
    :param query:用户问题 ！
    :param documents: 召回结果列表！
    :return:
    """
    url = "https://api.siliconflow.cn/v1/rerank"
    payload = {
        "model": "BAAI/bge-reranker-v2-m3",
        "query": query,
        "documents": documents
    }
    headers = {
        "Authorization": "Bearer sk-xcvozhsdzgyqfzihvdazadzetwtcaijgyqwsgqvpdaqewuoe",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
