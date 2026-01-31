import asyncio
from chromadbinit import chromadb_collection
from to_chunk import splitter
from embedding import embed_chunks_concurrent
from docstore import doc_store


async def process_and_save(doc_file: str):
    print("1. 开始切分父子块...")
    parents, children = splitter.split_main(doc_file)
    print(f"   - 生成父块: {len(parents)} 个")
    print(f"   - 生成子块: {len(children)} 个")

    # 2. 保存父块到 SQLite (不需要向量化，只存文本)
    print("2. 保存父块到 DocStore...")
    doc_store.save_parents(parents)

    # 3. 向量化子块 (高并发)
    print("3. 正在并发向量化子块...")
    child_texts = [c['content'] for c in children]

    # 每次处理一批，防止一次性内存爆炸
    batch_size = 50
    for i in range(0, len(children), batch_size):
        batch_children = children[i: i + batch_size]
        batch_texts = [c['content'] for c in batch_children]

        # 并发获取向量
        embeddings = await embed_chunks_concurrent(batch_texts, max_concurrency=20)

        # 准备写入 Chroma 的数据
        ids = [c['id'] for c in batch_children]
        metadatas = [{"parent_id": c['parent_id']} for c in batch_children]

        # 写入 Chroma
        chromadb_collection.add(
            ids=ids,
            documents=batch_texts,
            embeddings=embeddings,
            metadatas=metadatas
        )
        print(f"   - 已处理批次 {i} - {i + batch_size}")

    print("入库完成！")


if __name__ == "__main__":
    # 支持文档格式：txt, pdf, docx, xlsx, markdown, html, 各种编程脚本文件！
    asyncio.run(process_and_save("软件服务协议.docx"))
