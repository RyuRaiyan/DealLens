from .database import SessionLocal
from .search import semantic_search


db = SessionLocal()

try:
    query = "What programming languages and technical skills does the candidate have?"

    results = semantic_search(
        db=db,
        query=query,
        document_id=1,
        top_k=3
    )

    print(f"\nQuery: {query}")
    print(f"Retrieved chunks: {len(results)}")

    for i, chunk in enumerate(results, start=1):
        print(f"\n--- Result {i} ---")
        print(f"Chunk index: {chunk.chunk_index}")
        print(f"Characters: {len(chunk.content)}")
        print(f"Content:\n{chunk.content}")

finally:
    db.close()