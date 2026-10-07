from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

text = "DealLens is an AI-powered due diligence platform."

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=text
)

embedding = response.data[0].embedding

print("Embedding created successfully!")
print("Vector dimensions:", len(embedding))
print("First 5 values:", embedding[:5])