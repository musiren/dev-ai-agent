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

@pytest.mark.asyncio
async def test_browse_directory(mock_paramiko):
    mock_p, mock_client, mock_sftp = mock_paramiko
    # SFTP listdir_attr mock
    entry_dir = MagicMock()
    entry_dir.filename = "uploads"
    entry_dir.st_mode = 0o040755  # 디렉토리
    entry_file = MagicMock()
    entry_file.filename = "readme.txt"
    entry_file.st_mode = 0o100644  # 파일
    mock_sftp.listdir_attr.return_value = [entry_dir, entry_file]

    # 먼저 세션 생성
    from ssh_uploader.app import app, sessions
    test_session_id = "test-session-123"
    sessions[test_session_id] = (mock_client, mock_sftp)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/browse",
            params={"session_id": test_session_id, "path": "/home/user"},
        )
    assert response.status_code == 200
    data = response.json()
    assert len(data["entries"]) == 2
    assert data["entries"][0] == {"name": "uploads", "type": "dir", "path": "/home/user/uploads"}
    assert data["entries"][1] == {"name": "readme.txt", "type": "file", "path": "/home/user/readme.txt"}

@pytest.mark.asyncio
async def test_browse_invalid_session():
    from ssh_uploader.app import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/browse",
            params={"session_id": "invalid-session", "path": "/home/user"},
        )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_upload_files(mock_paramiko):

    mock_p, mock_client, mock_sftp = mock_paramiko
    mock_sftp.putfo = MagicMock()

    from ssh_uploader.app import app, sessions
    test_session_id = "upload-session-456"
    sessions[test_session_id] = (mock_client, mock_sftp)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/upload",
            data={"session_id": test_session_id, "target_path": "/home/user/uploads"},
            files=[
                ("files", ("hello.txt", b"hello world", "text/plain")),
                ("files", ("data.csv", b"a,b,c\n1,2,3", "text/csv")),
            ],
        )
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 2
    assert all(r["status"] == "ok" for r in data["results"])
    assert mock_sftp.putfo.call_count == 2

@pytest.mark.asyncio
async def test_upload_invalid_session():
    from ssh_uploader.app import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/upload",
            data={"session_id": "no-such-session", "target_path": "/tmp"},
            files=[("files", ("test.txt", b"data", "text/plain"))],
        )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_disconnect(mock_paramiko):
    mock_p, mock_client, mock_sftp = mock_paramiko
    from ssh_uploader.app import app, sessions
    test_session_id = "disconnect-session-789"
    sessions[test_session_id] = (mock_client, mock_sftp)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/disconnect",
            json={"session_id": test_session_id},
        )
    assert response.status_code == 200
    assert response.json() == {"status": "disconnected"}
    assert test_session_id not in sessions
    mock_sftp.close.assert_called_once()
    mock_client.close.assert_called_once()
