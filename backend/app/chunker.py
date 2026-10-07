import re


SECTION_HEADINGS = {
    "PROFESSIONAL SUMMARY",
    "ABOUT ME",
    "SUMMARY",
    "OBJECTIVE",

    "EDUCATION",
    "ACADEMIC BACKGROUND",

    "EXPERIENCE",
    "WORK EXPERIENCE",
    "INTERNSHIP",
    "INTERNSHIPS",

    "SKILLS",
    "TECHNICAL SKILLS",

    "CERTIFICATIONS",
    "CERTIFICATES",

    "PROJECTS",
    "ACADEMIC PROJECTS",

    "ACHIEVEMENTS",
    "ACTIVITIES",
    "EXTRACURRICULAR ACTIVITIES",

    "LANGUAGES",
    "INTERESTS",
    "PUBLICATIONS",
    "REFERENCES",
    "CONTACT",
}


MIN_CHUNK_LENGTH = 80


def normalize_line(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip()


def is_section_heading(line: str) -> bool:
    """
    A section is a heading only when the complete extracted
    line matches one of our known headings.
    """

    normalized = normalize_line(line)

    return normalized.upper() in SECTION_HEADINGS


def split_sentences(text: str):
    """
    Split text into useful sentence-level units.
    """

    parts = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    return [
        part.strip()
        for part in parts
        if part.strip()
    ]


def chunk_text(
    text: str,
    chunk_size: int = 900,
    overlap: int = 120
):

    if not text or not text.strip():
        return []

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    raw_lines = text.split("\n")

    chunks = []

    current_section = None
    current_parts = []
    current_length = 0

    def calculate_length(parts):

        return (
            sum(len(part) for part in parts)
            + max(0, len(parts) - 1)
        )

    def save_chunk(force=False):

        nonlocal current_parts
        nonlocal current_length

        if not current_parts:
            return

        content_parts = []

        if current_section:
            content_parts.append(
                f"[SECTION: {current_section}]"
            )

        content_parts.extend(current_parts)

        content = " ".join(
            content_parts
        ).strip()

        # Keep short sections when we are explicitly
        # reaching a new section heading.
        if force or len(content) >= MIN_CHUNK_LENGTH:
            chunks.append(content)

        # -----------------------------------------
        # Overlap
        # -----------------------------------------

        overlap_parts = []
        overlap_length = 0

        for part in reversed(current_parts):

            extra = len(part)

            if overlap_parts:
                extra += 1

            if overlap_length + extra > overlap:
                break

            overlap_parts.insert(
                0,
                part
            )

            overlap_length += extra

        current_parts = overlap_parts

        current_length = calculate_length(
            current_parts
        )

    # =============================================
    # PROCESS RAW PDF LINES
    # =============================================

    for raw_line in raw_lines:

        line = normalize_line(raw_line)

        if not line:
            continue

        # -----------------------------------------
        # EXACT SECTION HEADING
        # -----------------------------------------

        if is_section_heading(line):

            # Save previous section
            if current_parts:
                save_chunk(force=True)

            current_section = line.upper()

            current_parts = []

            current_length = 0

            continue

        # -----------------------------------------
        # NORMAL CONTENT
        # -----------------------------------------

        sentences = split_sentences(line)

        for sentence in sentences:

            if not sentence:
                continue

            sentence_length = len(sentence)

            # Chunk size reached
            if (
                current_parts
                and
                current_length
                + sentence_length
                + 1
                > chunk_size
            ):

                save_chunk()

            current_parts.append(
                sentence
            )

            current_length = calculate_length(
                current_parts
            )

    # =============================================
    # SAVE FINAL CHUNK
    # =============================================

    if current_parts:
        save_chunk(force=True)

    return chunks