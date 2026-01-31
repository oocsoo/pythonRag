
from typing import List
from embedding import embed_chunk
from chromadbinit import chromadb_collection


def retrieve(query: str, top_k: int) -> List[str]:
    """
    使用用户的问题，向量化之后，到数据库中比对，召回top_k条数据！
    :param query: 用户问题
    :param top_k: 几条数据
    :return: 列表
    """
    # 将用户的问题向量化！
    query_embedding = embed_chunk(query)
    results = chromadb_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results['documents'][0]
