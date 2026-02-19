import logging
from uuid import uuid4
from time import time
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from app.db import get_redis, create_chat, chat_exists
from app.vector_db import get_qdrant
from app.assistants.assistant import RAGAssistant
from app.indexing import ingest_pdf_bytes

logger = logging.getLogger(__name__)

class ChatIn(BaseModel):
    message: str

# Get Redis db dependency
async def get_rdb():
    rdb = get_redis()
    try:
        yield rdb
    finally:
        await rdb.aclose()

router = APIRouter()

@router.post('/index')
async def index_pdf(request: Request, file: UploadFile | None = File(None)):
    """Accept a PDF file, extract text, chunk (1000 chars, 200 overlap), embed, and ingest into the Qdrant knowledge base.
    Send the file as form field 'file' (or any single file field if sent as multipart/form-data).
    """
    if file is None:
        form = await request.form()
        for key in form.keys():
            value = form[key]
            if isinstance(value, UploadFile):
                file = value
                break
        if file is None:
            raise HTTPException(
                status_code=422,
                detail="No file provided. Send a PDF as multipart/form-data with form field 'file'.",
            )
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail='File must be a PDF')
    content = await file.read()
    doc_name = file.filename.rsplit('.', 1)[0] or 'document'
    try:
        num_chunks = await ingest_pdf_bytes(content, doc_name=doc_name)
    except Exception as e:
        logger.exception("Failed to process PDF in /index")
        raise HTTPException(status_code=422, detail=f'Failed to process PDF: {e!s}')
    return {'filename': file.filename, 'doc_name': doc_name, 'chunks_indexed': num_chunks}

@router.post('/chats')
async def create_new_chat(rdb=Depends(get_rdb)):
    chat_id = str(uuid4())[:8]
    created = int(time())
    await create_chat(rdb, chat_id, created)
    return {'id': chat_id}

@router.post('/chats/{chat_id}')
async def chat(chat_id: str, chat_in: ChatIn):
    # Dependencies with yield don't work with Streaming responses after version 0.106
    rdb = get_redis()
    if not await chat_exists(rdb, chat_id):
        raise HTTPException(status_code=404, detail=f'Chat {chat_id} does not exist')
    vector_db = get_qdrant()
    assistant = RAGAssistant(chat_id=chat_id, rdb=rdb, vector_db=vector_db)
    sse_stream = assistant.run(message=chat_in.message)
    return EventSourceResponse(sse_stream, background=rdb.aclose)