from datetime import datetime
import base64
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from app.core.auth import auth_client
from app.core.db import engine
from app.models.documents import Document, DocumentWithoutContent

documents_router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_FILE_TYPES = ["text/plain", "application/pdf", "text/markdown"]
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024


@documents_router.get("/")
def get_documents(
    auth_session=Depends(auth_client.require_session),
) -> list[DocumentWithoutContent]:
    user = auth_session.get("user")

    with Session(engine) as db_session:
        documents = db_session.exec(
            select(
                Document.id,
                Document.file_name,
                Document.file_type,
                Document.created_at,
                Document.updated_at,
                Document.user_id,
                Document.user_email,
                Document.shared_with,
            )
        ).all()

        return [
            DocumentWithoutContent(
                id=doc.id,
                file_name=doc.file_name,
                file_type=doc.file_type,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
                user_id=doc.user_id,
                user_email=doc.user_email,
                shared_with=doc.shared_with,
            )
            for doc in documents
        ]


@documents_router.post("/upload")
async def upload_document(
    file: UploadFile = File(), auth_session=Depends(auth_client.require_session)
) -> DocumentWithoutContent:
    user = auth_session.get("user")

    binary_content = await file.read()

    file_name = file.filename
    file_type = file.content_type

    if not file_name:
        raise HTTPException(status_code=400, detail="File name is required")

    if file_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed file types are: {','.join(ALLOWED_FILE_TYPES)}",
        )

    if len(binary_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds the maximum allowed size of {MAX_FILE_SIZE_MB} MB",
        )

    with Session(engine) as db_session:
        document = Document(
            content=binary_content,
            file_name=file_name,
            file_type=file_type,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            user_id=user.get("sub"),
            user_email=user.get("email"),
            shared_with=[],
        )

        db_session.add(document)
        db_session.commit()

        return document


@documents_router.get(
    "/{document_id}/content",
    dependencies=[Depends(auth_client.require_session)],
)
def get_document_content(document_id: str):
    with Session(engine) as db_session:
        document = db_session.get(Document, document_id)

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        encoded_content = base64.b64encode(document.content).decode("utf-8")

        return encoded_content


@documents_router.delete(
    "/{document_id}", dependencies=[Depends(auth_client.require_session)]
)
def delete_document(document_id: str):
    with Session(engine) as db_session:
        document = db_session.get(Document, document_id)

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        db_session.delete(document)
        db_session.commit()

        return {"message": "Document deleted successfully"}
