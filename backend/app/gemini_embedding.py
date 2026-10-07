import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not set in the .env file"
    )


client = genai.Client(
    api_key=API_KEY
)


MODEL_NAME = "gemini-embedding-2"

EMBEDDING_DIMENSION = 768


def get_embedding(
    text: str,
    is_query: bool = False,
    title: str = "document"
) -> list[float]:

    if is_query:

        formatted_text = (
            f"task: question answering | "
            f"query: {text}"
        )

    else:

        formatted_text = (
            f"title: {title} | "
            f"text: {text}"
        )

    response = client.models.embed_content(
        model=MODEL_NAME,
        contents=formatted_text,
        config=types.EmbedContentConfig(
            output_dimensionality=EMBEDDING_DIMENSION
        )
    )

    return response.embeddings[0].values