from gemini_embedding import get_embedding


text = """
Mohamed Raiyan is an aspiring AI and Machine Learning professional
with experience in Python, Machine Learning, Deep Learning and Data Science.
"""


embedding = get_embedding(text)

print("Embedding created successfully!")
print("Vector dimensions:", len(embedding))
print("First 5 values:", embedding[:5])