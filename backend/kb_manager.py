from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from utils import get_mongo_client
from config import MONGO_DB_NAME, MONGO_COLLECTION_NAME, EMBEDDING_MODEL

def ingest_documents():
    """
    Ingests documents from the knowledge base, splits them into chunks,
    embeds them, and stores them in MongoDB Atlas.
    """
    import os
    kb_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kb")
    loader = DirectoryLoader(
        kb_path, glob="**/*.txt", loader_cls=TextLoader, show_progress=True
    )
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(documents)

    embeddings = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)
    
    client = get_mongo_client()
    db = client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION_NAME]

    # Ensure the collection is empty before ingesting
    collection.delete_many({})

    MongoDBAtlasVectorSearch.from_documents(
        documents=split_docs,
        embedding=embeddings,
        collection=collection,
        index_name="default",
    )
    print("Documents ingested successfully into MongoDB Atlas.")

if __name__ == "__main__":
    ingest_documents()
