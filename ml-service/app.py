from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import joblib
import requests
from sklearn.metrics.pairwise import cosine_similarity

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


def detect_weak_topics(session_queries, threshold=2):

    if len(session_queries) == 0:
        return []

    query_embeddings = create_embedding(session_queries)

    topic_counter = {}

    for embedding in query_embeddings:

        similarities = cosine_similarity(
            lecture_vectors,
            [embedding]
        ).flatten()

        best_match_index = similarities.argmax()
        best_topic = lecture_titles[best_match_index]

        topic_counter[best_topic] = topic_counter.get(best_topic, 0) + 1

    weak_topics = []

    for topic, count in topic_counter.items():
        if count >= threshold:
            weak_topics.append(topic)

    return weak_topics

def create_embedding(text_list):
    r = requests.post(
        "http://localhost:11434/api/embed",
        json={
            "model": "bge-m3",
            "input": text_list
        }
    )
    return r.json()["embeddings"]


@app.route("/semantic-search", methods=["POST"])
def semantic_search():

    data = request.json
    query = data.get("query")
    session_queries.append(query)

    if not query:
        return jsonify({"error": "Query missing"}), 400

    # Generate embedding
    question_embedding = create_embedding([query])[0]

    # Compute similarity
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
    weak_topics = detect_weak_topics(session_queries)

    return jsonify({
        "query": query,
        "best_match": best_match,
        "recommended_lectures": recommended,
        "weak_topics_detected": weak_topics,
        "other_matches": results[1:]
    })


if __name__ == "__main__":
    app.run(port=5001, debug=True)