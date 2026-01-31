
from typing import List
from chromadbinit import chromadb_collection


def save_embeddings(chunks: List[str], embeddings: List[List[float]]) -> None:
    """
    向量列表数据和块列表数据，存入数据库@
    :param chunks: 块列表数据
    :param embeddings: 向量列表数据
    :return:
    """
    ids = [str(i) for i in range(len(chunks))]
    chromadb_collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
    )
