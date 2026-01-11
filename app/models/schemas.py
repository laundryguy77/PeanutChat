from pydantic import BaseModel
from typing import Optional, List


class FileAttachment(BaseModel):
    name: str
    type: str  # 'pdf', 'zip', 'text', 'code'
    content: str  # base64 for binary, raw text for text files
    is_base64: Optional[bool] = False


class ChatRequest(BaseModel):
    message: str
    images: Optional[List[str]] = None  # Base64 encoded images
    think: Optional[bool] = None  # Enable extended reasoning mode
    files: Optional[List[FileAttachment]] = None  # Attached files

class ChatMessage(BaseModel):
    role: str
    content: str
    images: Optional[List[str]] = None

class ModelSelectRequest(BaseModel):
    model: str

class SettingsUpdate(BaseModel):
    persona: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    num_ctx: Optional[int] = None
    repeat_penalty: Optional[float] = None
    tts_enabled: Optional[bool] = None
    tts_speaker: Optional[int] = None
    tts_temperature: Optional[float] = None
    tts_topk: Optional[int] = None

class VideoStatus(BaseModel):
    video_id: str
    status: str  # queued, generating, complete, error
    url: Optional[str] = None
    error: Optional[str] = None
