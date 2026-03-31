import os
import datetime
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

class MemoryManager:
    """
    Manages episodic and semantic memory using Pinecone.
    """
    def __init__(self, index_name=None):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = index_name or os.getenv("PINECONE_INDEX_NAME", "deep-work-memory")

        if not self.api_key:
            raise ValueError("PINECONE_API_KEY must be set in environment variables")

        self.pc = Pinecone(api_key=self.api_key)
        self.embeddings = OpenAIEmbeddings()

        # Ensure the index exists
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        if self.index_name not in existing_indexes:
            print(f"Creating Pinecone index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=1536, # OpenAI embeddings dimension
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )

        self.vectorstore = PineconeVectorStore(
            index_name=self.index_name,
            embedding=self.embeddings
        )

    def add_memory(self, text, metadata=None):
        """
        Adds a new memory (episodic) to the vector store.
        """
        metadata = metadata or {}
        if "timestamp" not in metadata:
            metadata["timestamp"] = datetime.datetime.now().isoformat()
        self.vectorstore.add_texts([text], metadatas=[metadata])

    async def aadd_memory(self, text, metadata=None):
        """
        Adds a new memory (episodic) to the vector store asynchronously.
        """
        metadata = metadata or {}
        if "timestamp" not in metadata:
            metadata["timestamp"] = datetime.datetime.now().isoformat()
        await self.vectorstore.aadd_texts([text], metadatas=[metadata])

    def search_memory(self, query, k=5):
        """
        Retrieves relevant memories (semantic) based on the query.
        """
        return self.vectorstore.similarity_search(query, k=k)

    async def asearch_memory(self, query, k=5):
        """
        Retrieves relevant memories (semantic) based on the query asynchronously.
        """
        return await self.vectorstore.asimilarity_search(query, k=k)

    def delete_index(self):
        """
        Deletes the current index. Use with caution.
        """
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        if self.index_name in existing_indexes:
            self.pc.delete_index(self.index_name)
