
---

# 高并发父子索引 RAG 系统
### Python实现，支持文件格式：Pdf，Word，Markdown，Html，Excel, Txt, 各种编程脚本！ 

这是一个基于 Python 实现的高性能 RAG（检索增强生成）系统。它采用了 **父子索引（Parent-Child Indexing / Small-to-Big Retrieval）** 策略来解决传统 RAG 中“检索片段破碎”和“上下文缺失”的问题，并使用 `asyncio` 实现高并发数据入库。

## ✨ 核心特性

1. **父子索引 (Parent-Child Splitter)**:
* **子块 (Child Chunk)**: 用于向量检索，粒度小，语义精准。
* **父块 (Parent Chunk)**: 用于喂给 LLM，粒度大，上下文完整。
* **关联机制**: 检索命中子块 -> 自动回溯父块 ID -> 返回完整父块内容。


2. **双层存储架构**:
* **ChromaDB**: 存储子块向量 + Parent ID (Metadata)。
* **SQLite (DocStore)**: 存储完整的父块文本，轻量且无需额外部署。


3. **高并发入库 (Async Embedding)**:
* 使用 `AsyncOpenAI` 和 `asyncio.Semaphore` 控制并发。
* 极大提升大规模文本的向量化速度。



## 🛠️ 环境准备

### 1. 安装依赖

Python 版本 3.13.10

```bash
pip install -r requirements.txt
```

`requirements.txt` 应包含：

```text
sentence_transformers
chromadb
openai
requests
python-dotenv
tqdm
aiohttp
pypdf
python-docx
pandas
openpyxl
```

### 2. 配置 API Key

打开 `.env`，将 API Key 替换为你自己的 SiliconFlow (或其他 OpenAI 兼容接口) 密钥。

**`.env`**:

```python
# 硅基流动向量模型！
EMBEDDING_BASE_URL=https://api.siliconflow.cn/v1
EMBEDDING_API_KEY=填写自己的秘钥
EMBEDDING_MODEL_NAME=Qwen/Qwen3-Embedding-8B

# 硅基流动重排模型！
RERANK_BASE_URL=https://api.siliconflow.cn/v1/rerank
RERANK_API_KEY=填写自己的秘钥
RERANK_MODEL_NAME=BAAI/bge-reranker-v2-m3
```

## 🚀 快速开始

### 第一步：数据入库 (Ingestion)

准备一个文本文件（例如 `data.txt`），（支持文件格式：txt, pdf, docx, xlsx, markdown, html, 各种编程脚本文件！）然后运行入库脚本。该脚本会自动进行父子切分、保存父块到 SQLite、并发计算子块向量并存入 ChromaDB。

修改 `emb_save_db.py` 底部的文件路径：

```python
if __name__ == "__main__":
    # 替换为你实际的文件路径
    asyncio.run(process_and_save("your_data_file.txt"))
```

运行脚本：

```bash
python emb_save_db.py
```

> **注意**: 你会看到进度条显示并发处理过程。生成的 `chromadb.db` (文件夹) 和 `docstore.db` (文件) 会保存在当前目录下。

### 第二步：检索 (Retrieval)

使用 `retrieve.py` 进行测试。它会根据你的问题，先找到最相关的子块，然后自动返回对应的完整父块。

修改 `retrieve.py` 底部的测试代码：

```python
if __name__ == "__main__":
    # 这里的 top_k 是你希望返回的父块数量
    results = retrieve("RAG的分块策略是怎样的？", top_k=3)
    
    for i, content in enumerate(results):
        print(f"--- 结果 {i+1} ---")
        print(content)
        print("\n")

```

运行脚本：

```bash
python retrieve.py
```

## 📂 项目结构说明

| 文件名                   | 作用         | 备注                                                     |
|-----------------------|------------|--------------------------------------------------------|
| **`to_chunk.py`**     | **切分逻辑**   | 实现了 `ParentChildSplitter`，负责将文本切分为父块和关联的子块。            |
| **`docstore.py`**     | **父块存储**   | 基于 SQLite 的简单键值存储，用于保存完整的父块文本。                         |
| **`embedding.py`**    | **向量化**    | 封装了 `AsyncOpenAI`，支持高并发 Embedding 并在 `retrieve` 时提供桥接。 |
| **`chromadbinit.py`** | **向量库**    | 初始化 ChromaDB 客户端和 Collection。                          |
| **`emb_save_db.py`**  | **入库主程序**  | 串联切分、存储、向量化流程的入口脚本。                                    |
| **`retrieve.py`**     | **检索主程序**  | 执行 Small-to-Big 检索逻辑：搜子块 -> 找父ID -> 拿父块。               |
| **`rerank.py`**       | **重排序**    | 对召回结果进行二次精排。                                           |
| **`data_loader.py`**  | **加载识别文件** | 支持word，excel，paf等。                            |

## ❓ 常见问题

**Q: 为什么检索返回的内容比通过向量库直接查出来的长？**
A: 这正是父子索引的作用。我们用“精准的短句”去匹配你的问题，但返回给你的是“包含该短句的完整段落”，这样 LLM 才能看懂上下文。

**Q: 如何调整切分大小？**
A: 在 `to_chunk.py` 中初始化 `ParentChildSplitter` 时修改参数：

```python
# parent_size: 父块字符数
# child_size: 子块字符数
splitter = ParentChildSplitter(parent_size=800, child_size=200, overlap=50)
```