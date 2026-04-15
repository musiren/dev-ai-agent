import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient, ASGITransport
import io

@pytest.fixture
def mock_paramiko():
    with patch("ssh_uploader.app.paramiko") as mock:
        mock_client = MagicMock()
        mock_sftp = MagicMock()
        mock_client.open_sftp.return_value = mock_sftp
        mock.SSHClient.return_value = mock_client
        mock.AutoAddPolicy.return_value = MagicMock()
        # 키 클래스 mock
        mock_key = MagicMock()
        mock.RSAKey.from_private_key.return_value = mock_key
        mock.DSSKey.from_private_key.side_effect = Exception("not dss")
        mock.ECDSAKey.from_private_key.side_effect = Exception("not ecdsa")
        mock.Ed25519Key.from_private_key.side_effect = Exception("not ed25519")
        yield mock, mock_client, mock_sftp

@pytest.mark.asyncio
async def test_connect_success(mock_paramiko):
    mock_p, mock_client, _ = mock_paramiko
    from ssh_uploader.app import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/connect",
            data={"host": "example.com", "port": "22", "username": "ubuntu"},
            files={"key_file": ("id_rsa", b"-----BEGIN RSA PRIVATE KEY-----\ntest\n-----END RSA PRIVATE KEY-----", "text/plain")},
        )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data

@pytest.mark.asyncio
async def test_connect_auth_failure(mock_paramiko):
    mock_p, mock_client, _ = mock_paramiko
    import paramiko as real_paramiko
    mock_client.connect.side_effect = real_paramiko.AuthenticationException("auth failed")
    from ssh_uploader.app import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/connect",
            data={"host": "example.com", "port": "22", "username": "ubuntu"},
            files={"key_file": ("id_rsa", b"-----BEGIN RSA PRIVATE KEY-----\ntest\n-----END RSA PRIVATE KEY-----", "text/plain")},
        )
    assert response.status_code == 401
