import chromadb
import datetime
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import pysqlite3 as sqlite3


client = chromadb.PersistentClient(path="./chromadb_persistent_storage/")
collection = client.get_or_create_collection(
    name="test", 
    metadata={
        "description": "testing",
        "created": str(datetime.now())
    }  
)

collection.add(
    documents=["lorem ipsum...", "lorlorsumsum", "lorsumeeee", ...],
    metadatas=[{"chapter": "3", "verse": "16"}, {"chapter": "3", "verse": "5"}, {"chapter": "29", "verse": "11"}, ...],
    ids=["id1", "id2", "id3", ...]
)

collection.query(
    query_embeddings=[[11.1, 12.1, 13.1],[1.1, 2.3, 3.2], ...],
    n_results=10,
    where={"chapter": "3"},
    where_document={"$contains":"l"}
)