from .database import SessionLocal
from .rag import answer_question


db = SessionLocal()

try:
    question = "What programming languages and technical skills does the candidate have?"

    result = answer_question(
        db=db,
        question=question,
        document_id=1,
        top_k=3
    )

    print("\n--- Question ---")
    print(question)

    print("\n--- RAG Answer ---")
    print(result["answer"])

    print("\n--- Sources ---")
    for source in result["sources"]:
        print(
            f"Chunk ID: {source['chunk_id']} | "
            f"Chunk Index: {source['chunk_index']}"
        )

finally:
    db.close()