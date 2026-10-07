from sqlalchemy.orm import Session

from .search import semantic_search
from .llm import generate_answer


def answer_question(
    db: Session,
    question: str,
    document_id: int,
    top_k: int = 3
):
    """
    Retrieve relevant document chunks and generate a grounded answer
    using the Qwen LLM.
    """

    # ---------------------------------------------------------
    # 1. RETRIEVE RELEVANT CHUNKS
    # ---------------------------------------------------------

    chunks = semantic_search(
        db=db,
        query=question,
        document_id=document_id,
        top_k=top_k
    )

    # ---------------------------------------------------------
    # 2. HANDLE NO RESULTS
    # ---------------------------------------------------------

    if not chunks:
        return {
            "answer": "I could not find enough information in the document to answer this.",
            "sources": []
        }

    # ---------------------------------------------------------
    # 3. BUILD CONTEXT
    # ---------------------------------------------------------

    context_parts = []

    for chunk in chunks:
        context_parts.append(
            f"[Chunk {chunk.chunk_index}]\n{chunk.content}"
        )

    context = "\n\n".join(context_parts)

    # Print context for debugging
    print("\n========== RETRIEVED CONTEXT ==========")
    print(context)
    print("========================================\n")

    # ---------------------------------------------------------
    # 4. GENERATE ANSWER USING QWEN 7B
    # ---------------------------------------------------------

    answer = generate_answer(
        question=question,
        context=context
    )

    # ---------------------------------------------------------
    # 5. RETURN SOURCE INFORMATION
    # ---------------------------------------------------------

    sources = [
        {
            "chunk_id": chunk.id,
            "chunk_index": chunk.chunk_index,
            "similarity": round(chunk.similarity, 4),
            "content": chunk.content
        }
        for chunk in chunks
    ]

    # ---------------------------------------------------------
    # 6. RETURN FINAL RESPONSE
    # ---------------------------------------------------------

    return {
        "answer": answer,
        "sources": sources
    }