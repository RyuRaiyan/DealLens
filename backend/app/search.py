import re

from sqlalchemy.orm import Session

from .models import DocumentChunk
from .gemini_embedding import get_embedding


SIMILARITY_THRESHOLD = 0.30
CANDIDATE_COUNT = 7
FINAL_COUNT = 3


# Useful terms for common document sections.
SECTION_HINTS = {
    "education": {
        "education",
        "study",
        "studying",
        "university",
        "college",
        "degree",
        "school",
        "academic",
        "course",
        "coursework",
    },

    "certifications": {
        "certification",
        "certifications",
        "certificate",
        "certificates",
        "certified",
    },

    "projects": {
        "project",
        "projects",
        "built",
        "developed",
        "application",
        "applications",
    },

    "experience": {
        "experience",
        "internship",
        "intern",
        "worked",
        "work",
        "job",
        "company",
    },

    "skills": {
        "skill",
        "skills",
        "technology",
        "technologies",
        "technical",
        "programming",
        "language",
        "languages",
        "framework",
        "frameworks",
        "tools",
    },

    "contact": {
        "email",
        "phone",
        "contact",
        "github",
        "linkedin",
        "profile",
    },
}


def normalize_text(text: str) -> list[str]:
    """
    Convert text into normalized words.
    """

    return re.findall(
        r"[a-zA-Z0-9+#.]+",
        text.lower()
    )


def lexical_score(query: str, content: str) -> float:
    """
    Calculate a lightweight keyword-overlap score.
    """

    query_words = set(normalize_text(query))
    content_words = set(normalize_text(content))

    if not query_words:
        return 0.0

    overlap = query_words.intersection(content_words)

    return len(overlap) / len(query_words)


def detect_section_hint(query: str) -> str | None:
    """
    Detect the likely document section the question refers to.
    """

    query_words = set(normalize_text(query))

    best_section = None
    best_score = 0

    for section, keywords in SECTION_HINTS.items():

        score = len(query_words.intersection(keywords))

        if score > best_score:
            best_score = score
            best_section = section

    return best_section


def section_score(query: str, content: str) -> float:
    """
    Give a small boost when the retrieved chunk appears
    relevant to the question's likely section.
    """

    section = detect_section_hint(query)

    if not section:
        return 0.0

    content_lower = content.lower()

    section_keywords = SECTION_HINTS[section]

    matches = sum(
        1
        for keyword in section_keywords
        if keyword in content_lower
    )

    if matches == 0:
        return 0.0

    return min(matches / 3.0, 1.0)


def rerank_results(
    query: str,
    results: list[tuple],
    final_count: int = FINAL_COUNT
):
    """
    Rerank semantic-search candidates using:
    
    - Gemini semantic similarity
    - lexical keyword overlap
    - section relevance
    """

    reranked = []

    for chunk, distance_value in results:

        semantic_similarity = 1 - float(distance_value)

        lexical = lexical_score(
            query,
            chunk.content
        )

        section = section_score(
            query,
            chunk.content
        )

        # Semantic similarity remains the dominant signal.
        final_score = (
            semantic_similarity * 0.70
            + lexical * 0.15
            + section * 0.15
        )

        reranked.append(
            (
                chunk,
                semantic_similarity,
                lexical,
                section,
                final_score
            )
        )

    reranked.sort(
        key=lambda item: item[4],
        reverse=True
    )

    return reranked[:final_count]


def semantic_search(
    db: Session,
    query: str,
    document_id: int,
    top_k: int = FINAL_COUNT
):
    """
    Retrieve a larger semantic candidate pool and
    rerank the candidates before returning the final chunks.
    """

    query_embedding = get_embedding(
        query,
        is_query=True
    )

    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    ).label("distance")

    # First retrieve a larger candidate pool.
    results = (
        db.query(DocumentChunk, distance)
        .filter(
            DocumentChunk.document_id == document_id,
            DocumentChunk.embedding.isnot(None)
        )
        .order_by(distance)
        .limit(CANDIDATE_COUNT)
        .all()
    )

    if not results:
        return []

    reranked = rerank_results(
        query=query,
        results=results,
        final_count=top_k
    )

    chunks = []

    for (
        chunk,
        semantic_similarity,
        lexical,
        section,
        final_score
    ) in reranked:

        if semantic_similarity >= SIMILARITY_THRESHOLD:

            chunk.similarity = semantic_similarity

            # Store additional debugging information.
            chunk.lexical_score = lexical
            chunk.section_score = section
            chunk.rerank_score = final_score

            chunks.append(chunk)

    print("\n========== RETRIEVAL RERANKING ==========")

    for chunk in chunks:

        print(
            f"Chunk {chunk.chunk_index} | "
            f"semantic={chunk.similarity:.4f} | "
            f"lexical={chunk.lexical_score:.4f} | "
            f"section={chunk.section_score:.4f} | "
            f"final={chunk.rerank_score:.4f}"
        )

    print("==========================================\n")

    return chunks