import unittest
from unittest.mock import MagicMock, patch
from src.memory.pinecone_manager import MemoryManager

class TestMemoryManager(unittest.TestCase):
    @patch('src.memory.pinecone_manager.Pinecone')
    @patch('src.memory.pinecone_manager.OpenAIEmbeddings')
    @patch('src.memory.pinecone_manager.PineconeVectorStore')
    @patch('os.getenv')
    def test_init(self, mock_getenv, mock_vectorstore, mock_embeddings, mock_pinecone):
        mock_getenv.side_effect = lambda k, default=None: "test-value" if k == "PINECONE_API_KEY" else default

        # Mocking the list_indexes behavior
        mock_pc_instance = mock_pinecone.return_value
        mock_pc_instance.list_indexes.return_value.names.return_value = ["deep-work-memory"]

        memory = MemoryManager(index_name="deep-work-memory")

        self.assertEqual(memory.index_name, "deep-work-memory")
        mock_pinecone.assert_called_once_with(api_key="test-value")

    @patch('src.memory.pinecone_manager.Pinecone')
    @patch('src.memory.pinecone_manager.OpenAIEmbeddings')
    @patch('src.memory.pinecone_manager.PineconeVectorStore')
    @patch('os.getenv')
    def test_add_memory(self, mock_getenv, mock_vectorstore, mock_embeddings, mock_pinecone):
        mock_getenv.return_value = "test-value"
        mock_pc_instance = mock_pinecone.return_value
        mock_pc_instance.list_indexes.return_value.names.return_value = ["test-index"]

        memory = MemoryManager(index_name="test-index")
        memory.add_memory("test text", {"meta": "data"})

        args, kwargs = memory.vectorstore.add_texts.call_args
        self.assertEqual(args[0], ["test text"])
        self.assertEqual(kwargs['metadatas'][0]['meta'], 'data')
        self.assertIn('timestamp', kwargs['metadatas'][0])

if __name__ == '__main__':
    unittest.main()
