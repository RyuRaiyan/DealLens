from sqlalchemy.orm import Session

from .models import Document, DocumentChunk
from .chunker import chunk_text
from .gemini_embedding import get_embedding


def embed_document(
    document_id: int,
    db: Session,
):
    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if not document:
        raise ValueError(f"Document {document_id} not found.")

    chunks = chunk_text(document.content)

    print(f"Creating Gemini embeddings for {len(chunks)} chunks...")

    # Remove existing chunks if this document is processed again
    db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id
    ).delete()

    for index, chunk in enumerate(chunks):

        embedding = get_embedding(
        chunk,
        is_query=False,
        title=document.filename
    )

        document_chunk = DocumentChunk(
            document_id=document_id,
            chunk_index=index,
            content=chunk,
            embedding=embedding,
        )

        db.add(document_chunk)

        print(f"Embedded chunk {index + 1}/{len(chunks)}")

    db.commit()

    print("Document chunks and Gemini embeddings stored successfully.")

    return len(chunks)