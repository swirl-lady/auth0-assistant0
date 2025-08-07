import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr

from app.core.config import settings
from app.models.embeddings import Embedding

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=SecretStr(settings.OPENAI_API_KEY),
)


def generate_embeddings(
    document_id: uuid.UUID, file_name: str, text: str
) -> list[Embedding]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=10,
        length_function=len,
    )

    chunks = splitter.create_documents([text])
    embeddings = embedding_model.embed_documents(
        [chunk.page_content for chunk in chunks]
    )

    return [
        Embedding(
            document_id=document_id,
            meta={
                "file_name": file_name,
                "document_id": str(document_id),
            },
            content=chunk.page_content,
            embedding=embedding,
        )
        for chunk, embedding in zip(chunks, embeddings)
    ]
