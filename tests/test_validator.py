import unittest
from unittest.mock import MagicMock, patch
from src.agents.validator import Validator

class TestValidator(unittest.TestCase):
    @patch('src.agents.validator.ChatOpenAI')
    def test_validate_action_text_only(self, mock_llm):
        mock_llm_instance = mock_llm.return_value
        mock_result = MagicMock()
        mock_result.is_successful = True
        mock_result.feedback = "Looks good"

        mock_chain = MagicMock()
        mock_chain.invoke.return_value = mock_result
        mock_llm_instance.with_structured_output.return_value = mock_chain

        validator = Validator()
        # Ensure we use the mock chain we just created
        validator.chain = mock_chain

        result = validator.validate_action(
            action_description="Click login",
            intended_outcome="Logged in",
            page_content="Welcome user!"
        )

        self.assertTrue(result.is_successful)
        self.assertEqual(result.feedback, "Looks good")

    @patch('src.agents.validator.ChatOpenAI')
    @patch('src.agents.validator.ChatPromptTemplate')
    def test_validate_action_with_screenshot(self, mock_prompt_template, mock_llm):
        mock_llm_instance = mock_llm.return_value
        mock_result = MagicMock()
        mock_result.is_successful = False
        mock_result.feedback = "Login failed"

        mock_chain = MagicMock()
        mock_chain.invoke.return_value = mock_result

        # When screenshot_base64 is provided, it creates a new prompt and chain
        mock_prompt_template.from_messages.return_value.__or__.return_value = mock_chain
        mock_llm_instance.with_structured_output.return_value = mock_chain

        validator = Validator()
        with patch.object(validator, 'llm', mock_llm_instance):
            result = validator.validate_action(
                action_description="Click login",
                intended_outcome="Logged in",
                page_content="Error: Wrong password",
                screenshot_base64="abc123base64"
            )

        self.assertFalse(result.is_successful)

if __name__ == '__main__':
    unittest.main()
