import joblib
import numpy as np
import requests
from sklearn.metrics.pairwise import cosine_similarity

# Load vector database
df = joblib.load("embeddings.joblib")

# Generate query embedding
query = "What is HTML?"

r = requests.post(
    "http://localhost:11434/api/embed",
    json={
        "model": "bge-m3",
        "input": [query]
    }
)

query_embedding = r.json()["embeddings"][0]

# Compute similarity
similarities = cosine_similarity(
    np.vstack(df["embedding"]),
    [query_embedding]
).flatten()

# Get top 5 matches
top_indices = similarities.argsort()[::-1][:5]

print("\nTop 5 Results:\n")

for idx in top_indices:
    row = df.iloc[idx]

    print("=" * 60)
    print("Lecture :", row["title"])
    print("Video   :", row["number"])
    print("Start   :", row["start"])
    print("Score   :", similarities[idx])
    print("Text    :", row["text"])