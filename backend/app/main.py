from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import fitz

from .chunker import chunk_text
from .database import SessionLocal
from .models import Document, DocumentChunk
from .embed_document import embed_document
from .search import semantic_search
from .rag import answer_question


app = FastAPI(
    title="DealLens API",
    description="AI-powered due diligence and document analysis platform",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "message": "DealLens API is running",
        "status": "online"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/db-health")
def database_health(db: Session = Depends(get_db)):
    from sqlalchemy import text

    result = db.execute(text("SELECT 1"))

    return {
        "database": "connected",
        "result": result.scalar()
    }


@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    file_bytes = await file.read()

    try:
        pdf = fitz.open(
            stream=file_bytes,
            filetype="pdf"
        )

        page_count = len(pdf)
        text = ""

        for page in pdf:
            page_text = page.get_text("text", sort=True)
            text += page_text + "\n"

        pdf.close()

        # DEBUG: verify what FastAPI extracted
        print("=" * 60)
        print("EXTRACTION DEBUG")
        print("Characters extracted:", len(text))
        print(
            "Has CERTIFICATIONS:",
            "CERTIFICATIONS" in text.upper()
        )
        print(
            "Has PROJECTS:",
            "PROJECTS" in text.upper()
        )
        print(
            "Has Infosys Springboard:",
            "INFOSYS SPRINGBOARD" in text.upper()
        )
        print("=" * 60)

        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="No readable text found in the PDF."
            )

        document = Document(
            filename=file.filename,
            content=text,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        try:
            chunk_count = embed_document(
                document_id=document.id,
                db=db
            )

        except Exception as e:
            db.rollback()

            raise HTTPException(
                status_code=500,
                detail=f"Document embedding failed: {str(e)}"
            )

        return {
            "message": "PDF uploaded and processed successfully",
            "document_id": document.id,
            "filename": document.filename,
            "pages": page_count,
            "characters_extracted": len(text),
            "chunks_created": chunk_count
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to process PDF: {str(e)}"
        )


@app.get("/documents")
def get_documents(
    db: Session = Depends(get_db)
):
    documents = db.query(Document).order_by(
        Document.id.desc()
    ).all()

    return {
        "total_documents": len(documents),
        "documents": [
            {
                "document_id": document.id,
                "filename": document.filename,
                "characters": len(document.content),
                "chunks": db.query(DocumentChunk).filter(
                    DocumentChunk.document_id == document.id
                ).count()
            }
            for document in documents
        ]
    }


@app.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    filename = document.filename

    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully",
        "document_id": document_id,
        "filename": filename
    }


@app.get("/documents/{document_id}/chunks")
def get_document_chunks(
    document_id: int,
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    chunks = chunk_text(document.content)

    return {
        "document_id": document.id,
        "filename": document.filename,
        "total_chunks": len(chunks),
        "chunks": [
            {
                "chunk_id": index + 1,
                "characters": len(chunk),
                "text": chunk
            }
            for index, chunk in enumerate(chunks)
        ]
    }


from pydantic import BaseModel


class SearchRequest(BaseModel):
    document_id: int
    query: str
    top_k: int = 3


@app.post("/search")
def search_documents(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    results = semantic_search(
        db=db,
        query=request.query,
        document_id=request.document_id,
        top_k=request.top_k
    )

    return {
        "query": request.query,
        "document_id": request.document_id,
        "results": [
            {
                "chunk_id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "similarity": round(chunk.similarity, 4),
            }
            for chunk in results
        ]
    }


class AskRequest(BaseModel):
    document_id: int
    question: str
    top_k: int = 3


@app.post("/ask")
def ask_question(
    request: AskRequest,
    db: Session = Depends(get_db)
):
    result = answer_question(
        db=db,
        question=request.question,
        document_id=request.document_id,
        top_k=request.top_k
    )

    return {
        "question": request.question,
        "document_id": request.document_id,
        "answer": result["answer"],
        "sources": result["sources"]
    }