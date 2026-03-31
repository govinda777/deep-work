import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from src.memory.pinecone_manager import MemoryManager
import os

class TestMemoryManager(unittest.IsolatedAsyncioTestCase):
    @patch('src.memory.pinecone_manager.Pinecone')
    @patch('src.memory.pinecone_manager.OpenAIEmbeddings')
    @patch('src.memory.pinecone_manager.PineconeVectorStore')
    @patch('os.getenv')
    def test_init(self, mock_getenv, mock_vectorstore, mock_embeddings, mock_pinecone):
        mock_getenv.side_effect = lambda k, default=None: "test-value" if k == "PINECONE_API_KEY" else default
        mock_pc_instance = mock_pinecone.return_value
        mock_index = MagicMock()
        mock_index.name = "deep-work-memory"
        mock_pc_instance.list_indexes.return_value = [mock_index]
        memory = MemoryManager(index_name="deep-work-memory")
        self.assertEqual(memory.index_name, "deep-work-memory")
        mock_pinecone.assert_called_once_with(api_key="test-value")

    @patch('src.memory.pinecone_manager.Pinecone')
    @patch('src.memory.pinecone_manager.OpenAIEmbeddings')
    @patch('src.memory.pinecone_manager.PineconeVectorStore')
    @patch('os.getenv')
    async def test_aadd_memory(self, mock_getenv, mock_vectorstore, mock_embeddings, mock_pinecone):
        mock_getenv.return_value = "test-value"
        mock_pc_instance = mock_pinecone.return_value
        mock_index = MagicMock()
        mock_index.name = "test-index"
        mock_pc_instance.list_indexes.return_value = [mock_index]

        mock_vs_instance = mock_vectorstore.return_value
        mock_vs_instance.aadd_texts = AsyncMock()

        memory = MemoryManager(index_name="test-index")
        memory.vectorstore = mock_vs_instance

        await memory.aadd_memory("test text", {"meta": "data"})
        mock_vs_instance.aadd_texts.assert_awaited_once()
        args, kwargs = mock_vs_instance.aadd_texts.call_args
        self.assertEqual(args[0], ["test text"])
        self.assertEqual(kwargs['metadatas'][0]['meta'], 'data')

    @patch('src.memory.pinecone_manager.Pinecone')
    @patch('src.memory.pinecone_manager.OpenAIEmbeddings')
    @patch('src.memory.pinecone_manager.PineconeVectorStore')
    @patch('os.getenv')
    async def test_asearch_memory(self, mock_getenv, mock_vectorstore, mock_embeddings, mock_pinecone):
        mock_getenv.return_value = "test-value"
        mock_pc_instance = mock_pinecone.return_value
        mock_index = MagicMock()
        mock_index.name = "test-index"
        mock_pc_instance.list_indexes.return_value = [mock_index]

        mock_vs_instance = mock_vectorstore.return_value
        mock_vs_instance.asimilarity_search = AsyncMock(return_value=["res"])

        memory = MemoryManager(index_name="test-index")
        memory.vectorstore = mock_vs_instance

        results = await memory.asearch_memory("query", k=3)
        self.assertEqual(results, ["res"])
        mock_vs_instance.asimilarity_search.assert_awaited_once_with("query", k=3)

    @patch('src.memory.pinecone_manager.Pinecone')
    @patch('src.memory.pinecone_manager.OpenAIEmbeddings')
    @patch('src.memory.pinecone_manager.PineconeVectorStore')
    @patch('os.getenv')
    def test_delete_index(self, mock_getenv, mock_vectorstore, mock_embeddings, mock_pinecone):
        mock_getenv.return_value = "test-value"
        mock_pc_instance = mock_pinecone.return_value
        mock_index = MagicMock()
        mock_index.name = "test-index"
        mock_pc_instance.list_indexes.return_value = [mock_index]

        memory = MemoryManager(index_name="test-index")
        memory.delete_index()
        mock_pc_instance.delete_index.assert_called_once_with("test-index")

if __name__ == '__main__':
    unittest.main()
