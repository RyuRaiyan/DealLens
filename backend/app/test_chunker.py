from .chunker import chunk_text


sample_text = """
DealLens is an AI-powered due diligence platform.
It can analyze company reports and extract important information.
Users can ask questions about financial performance, risks, opportunities,
and management outlook.
"""


chunks = chunk_text(sample_text)

print(f"Number of chunks: {len(chunks)}")

for i, chunk in enumerate(chunks, start=1):
    print(f"\n--- Chunk {i} ---")
    print(chunk)