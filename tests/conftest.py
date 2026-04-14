import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_anthropic_client():
    """실제 API 호출 없이 테스트할 수 있는 mock client."""
    with patch("agents.base.anthropic.Anthropic") as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance

        # stream context manager mock 설정
        mock_stream = MagicMock()
        mock_stream.__enter__ = MagicMock(return_value=mock_stream)
        mock_stream.__exit__ = MagicMock(return_value=False)
        mock_stream.text_stream = iter(["테스트 응답입니다."])

        # get_final_message mock
        mock_final = MagicMock()
        mock_text_block = MagicMock()
        mock_text_block.type = "text"
        mock_text_block.text = "테스트 응답입니다."
        mock_final.content = [mock_text_block]
        mock_stream.get_final_message.return_value = mock_final

        mock_instance.messages.stream.return_value = mock_stream
        yield mock_instance


@pytest.fixture
def sample_code() -> str:
    return "def add(a: int, b: int) -> int:\n    return a + b"


@pytest.fixture
def sample_tests() -> str:
    return "def test_add():\n    assert add(1, 2) == 3"
