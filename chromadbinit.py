import chromadb


# 内存存储！
# chromadb_client_flask = chromadb.EphemeralClient()

# 本地磁盘存储！
chromadb_client_local = chromadb.PersistentClient("./chromadb.db")
chromadb_collection = chromadb_client_local.get_or_create_collection(name="default")
