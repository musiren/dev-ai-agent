import io
import stat
import uuid
from typing import List, Optional
from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import paramiko
from paramiko import AuthenticationException as SSHAuthenticationException

app = FastAPI()
sessions: dict[str, tuple] = {}


def load_private_key(key_content: str) -> paramiko.PKey:
    key_file = io.StringIO(key_content)
    for key_class in [paramiko.RSAKey, paramiko.DSSKey, paramiko.ECDSAKey, paramiko.Ed25519Key]:
        try:
            key_file.seek(0)
            return key_class.from_private_key(key_file)
        except Exception:
            continue
    raise ValueError("Unsupported or invalid SSH key format")


@app.post("/api/connect")
async def connect(
    host: str = Form(...),
    port: int = Form(22),
    username: str = Form(...),
    key_file: UploadFile = File(...),
):
    key_content = (await key_file.read()).decode("utf-8")
    try:
        pkey = load_private_key(key_content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=host, port=port, username=username, pkey=pkey, timeout=10)
    except SSHAuthenticationException:
        raise HTTPException(status_code=401, detail="SSH authentication failed")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Connection failed: {str(e)}")

    sftp = client.open_sftp()
    session_id = str(uuid.uuid4())
    sessions[session_id] = (client, sftp)
    return {"session_id": session_id}


@app.get("/")
async def index():
    return FileResponse("ssh_uploader/upload.html")
