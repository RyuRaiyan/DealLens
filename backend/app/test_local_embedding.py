from sentence_transformers import SentenceTransformer


model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

text = "DealLens is an AI-powered due diligence platform."

embedding = model.encode(text)

print("Embedding created successfully!")
print("Vector dimensions:", len(embedding))
print("First 5 values:", embedding[:5])