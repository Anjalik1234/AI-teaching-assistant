from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import joblib
import os
import requests
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

from domain_topics import domain_topics

topic_tracker = defaultdict(int)

app = Flask(__name__)

# Load embeddings once at startup
df = joblib.load("embeddings.joblib")
df["number"] = df["number"].astype(int)

lecture_sequence = (
    df[["title", "number"]]
    .drop_duplicates()
    .sort_values("number")
    .reset_index(drop=True)
)

session_queries = []

def keyword_overlap_score(query, text):
    query_words = set(query.lower().split())
    text_words = set(text.lower().split())

    if len(query_words) == 0:
        return 0

    overlap = query_words.intersection(text_words)
    return len(overlap) / len(query_words)


def detect_domain(query):

    query = query.lower()

    domain_keywords = {
        "python": ["python", "loop", "function", "dictionary"],
        "machine learning": ["regression", "classification", "model", "training"],
        "dbms": ["sql", "database", "transaction", "normalization"],
        "data structures": ["stack", "queue", "tree", "graph"],
        "web development": ["html", "css", "javascript", "react"]
    }

    for domain, keywords in domain_keywords.items():
        for word in keywords:
            if word in query:
                return domain

    return None


def get_domain_recommendations(query):
    domain = detect_domain(query)

    if domain:
        return domain_topics[domain]

    return []


def title_match_score(query, title):
    query_words = set(query.lower().split())
    title_words = set(title.lower().split())

    if len(query_words) == 0:
        return 0

    overlap = query_words.intersection(title_words)
    return len(overlap) / len(query_words)


def build_lecture_embeddings(df):
    lecture_embeddings = {}

    for title in df["title"].unique():
        lecture_chunks = df[df["title"] == title]["embedding"].tolist()
        lecture_embeddings[title] = np.mean(lecture_chunks, axis=0)

    return lecture_embeddings


lecture_embedding_map = build_lecture_embeddings(df)
lecture_titles = list(lecture_embedding_map.keys())
lecture_vectors = np.vstack(list(lecture_embedding_map.values()))

def recommend_lectures(current_title, top_k=3):

    if current_title not in lecture_embedding_map:
        return []

    # Get current lecture number
    current_row = lecture_sequence[
        lecture_sequence["title"] == current_title
    ]

    if current_row.empty:
        return []

    current_number = current_row["number"].values[0]

    # Step 1: Get next lectures in course order
    next_lectures = lecture_sequence[
        lecture_sequence["number"] > current_number
    ]["title"].head(top_k).tolist()

    if len(next_lectures) >= top_k:
        return next_lectures

    # Step 2: fallback to semantic similarity if needed
    current_vector = lecture_embedding_map[current_title]

    similarities = cosine_similarity(
        lecture_vectors,
        [current_vector]
    ).flatten()

    ranked_indices = similarities.argsort()[::-1]

    semantic_fill = []

    for idx in ranked_indices:
        title = lecture_titles[idx]

        if title != current_title and title not in next_lectures:
            semantic_fill.append(title)

        if len(next_lectures) + len(semantic_fill) == top_k:
            break

    return next_lectures + semantic_fill


def detect_weak_topics(query, confidence):
    topic = detect_domain(query) or query.lower().strip()

    if confidence < 0.6:
        topic_tracker[topic] += 2
    else:
        topic_tracker[topic] += 1

    sorted_topics = sorted(
        topic_tracker.items(),
        key=lambda x: x[1],
        reverse=True
    )

    weak_topics_ranked = [
        {"topic": t[0], "score": t[1]}
        for t in sorted_topics[:5]
    ]

    return weak_topics_ranked

def create_embedding(text_list):
    raise Exception("Runtime embedding disabled in deployment mode")


@app.route("/")
def home():
    return "AI Teaching Assistant ML Service Running"

@app.route("/semantic-search", methods=["POST"])
def semantic_search():

    data = request.json
    query = data.get("query")
    session_queries.append(query)

    if not query:
        return jsonify({"error": "Query missing"}), 400


    # Detect domain first
    domain = detect_domain(query)

    dataset_domain = "web development"

    # If query belongs to another domain (Python, ML, DBMS, etc.)
    if domain and domain != dataset_domain:

        return jsonify({
            "query": query,
            "message": "This assistant currently retrieves timestamp-level results from the Web Development course dataset. However, related topics from other domains are suggested below.",
            "best_match": None,
            "recommended_lectures": [],
            "domain_recommendations": get_domain_recommendations(query),
            "weak_topics_ranked": detect_weak_topics(query, 0),
            "other_matches": []
        })


    # Continue normal semantic search for Web Dev queries
    query_vector = df[df["title"].str.contains(query, case=False, na=False)]

    if not query_vector.empty:
        question_embedding = np.mean(np.vstack(query_vector["embedding"]), axis=0)
    else:
        question_embedding = np.mean(np.vstack(df["embedding"]), axis=0)


    semantic_scores = cosine_similarity(
        np.vstack(df["embedding"]),
        [question_embedding]
    ).flatten()


    final_scores = []

    for i, row in df.iterrows():

        keyword_score = keyword_overlap_score(query, row["text"])
        title_score = title_match_score(query, row["title"])

        combined_score = (
            0.5 * semantic_scores[i]
            + 0.2 * keyword_score
            + 0.3 * title_score
        )

        final_scores.append(combined_score)


    final_scores = np.array(final_scores)

    top_k = 5
    indices = final_scores.argsort()[::-1][:top_k]

    results = []

    for idx in indices:
        row = df.iloc[idx]

        results.append({
            "video_number": int(row["number"]),
            "title": row["title"],
            "start": float(row["start"]),
            "end": float(row["end"]),
            "text": row["text"],
            "confidence": round(float(final_scores[idx]), 3)
        })


    best_match = results[0]

    recommended = recommend_lectures(best_match["title"])

    confidence = best_match["confidence"]

    weak_topics_ranked = detect_weak_topics(query, confidence)


    return jsonify({
        "query": query,
        "best_match": best_match,
        "recommended_lectures": recommended,
        "domain_recommendations": [],
        "weak_topics_ranked": weak_topics_ranked,
        "other_matches": results[1:]
    })



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)