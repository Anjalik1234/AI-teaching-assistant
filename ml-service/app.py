from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import joblib
import os
import requests
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import json

from domain_topics import domain_topics

learner_profile = defaultdict(
    lambda: {
        "questions": 0,
        "confidences": []
    }
)

PROFILE_FILE = "learner_profile.json"

if os.path.exists(PROFILE_FILE):

    with open(PROFILE_FILE, "r") as f:

        saved_profile = json.load(f)

        for topic, data in saved_profile.items():

            learner_profile[topic]["questions"] = data["questions"]
            learner_profile[topic]["confidences"] = data["confidences"]

app = Flask(__name__)

# Load embeddings once at startup
df = joblib.load("embeddings.joblib")
df["number"] = df["number"].astype(int)


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
        "data structures": ["stack", "queue", "tree"],
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



def build_lecture_embeddings(df):
    lecture_embeddings = {}

    for title in df["title"].unique():
        lecture_chunks = df[df["title"] == title]["embedding"].tolist()
        lecture_embeddings[title] = np.mean(lecture_chunks, axis=0)

    return lecture_embeddings


lecture_embedding_map = build_lecture_embeddings(df)
lecture_titles = list(lecture_embedding_map.keys())
lecture_vectors = np.vstack(list(lecture_embedding_map.values()))

def recommend_lectures(query_embedding, current_title=None, top_k=3):

    similarities = cosine_similarity(
        lecture_vectors,
        [query_embedding]
    ).flatten()

    ranked_indices = similarities.argsort()[::-1]

    recommendations = []

    print("\nLecture Similarities:")

    for idx in ranked_indices:

        title = lecture_titles[idx]
        score = similarities[idx]

        print(f"{title} --> {score:.4f}")

        if current_title and title == current_title:
            continue

        recommendations.append(title)

        if len(recommendations) == top_k:
            break

    return recommendations


def detect_weak_topics(topic, confidence):

    # Update learner profile
    learner_profile[topic]["questions"] += 1
    learner_profile[topic]["confidences"].append(confidence)

    weak_topics = []

    for topic_name, data in learner_profile.items():

        avg_confidence = (
            sum(data["confidences"]) /
            len(data["confidences"])
        )

        # Assign proficiency level
        if avg_confidence >= 0.85:
            status = "Strong"

        elif avg_confidence >= 0.70:
            status = "Moderate"

        else:
            status = "Needs Practice"

        weak_topics.append({

            # Existing fields (frontend compatibility)
            "topic": topic_name,
            "score": round((1 - avg_confidence) * 100, 1),

            # New fields
            "questions": data["questions"],
            "average_confidence": round(avg_confidence, 3),
            "status": status

        })

    # Lowest confidence first
    weak_topics.sort(
        key=lambda x: x["average_confidence"]
    )

    with open(PROFILE_FILE, "w") as f:

        json.dump(
            dict(learner_profile),
            f,
            indent=4
        )

    return weak_topics[:5]



def create_embedding(text_list):
    r = requests.post(
        "http://localhost:11434/api/embed",
        json={
            "model": "bge-m3",
            "input": text_list
        }
    )

    r.raise_for_status()

    return r.json()["embeddings"]


def inference(prompt):
    r = requests.post("http://localhost:11434/api/generate", json={
        # "model": "deepseek-r1",
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False
    })

    response = r.json()
    return response


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


    question_embedding = create_embedding([query])[0]


    semantic_scores = cosine_similarity(
        np.vstack(df["embedding"]),
        [question_embedding]
    ).flatten()


    final_scores = []

    for i, row in df.iterrows():

        keyword_score = keyword_overlap_score(query, row["text"])

        combined_score = (
            0.9 * semantic_scores[i]
            + 0.1 * keyword_score
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

    context = ""

    for result in results:
        start_minutes = int(result["start"] // 60)
        start_seconds = int(result["start"] % 60)

        context += (
            f"Video {result['video_number']} - {result['title']}\n"
            f"Timestamp: {start_minutes}:{start_seconds:02d}\n"
            f"Transcript: {result['text']}\n\n"
        )


    prompt = f"""
    You are an AI Teaching Assistant for a Web Development course.

    Use ONLY the information provided below to answer the student's question.

    If the answer is not contained in the provided context, politely say that it is not covered in the available course material.

    Retrieved Course Content:

    {context}

    Student Question:
    {query}

    Instructions:
    - Give a clear and beginner-friendly explanation.
    - Mention the most relevant video number.
    - Mention the timestamp in MM:SS format.
    - If multiple videos are relevant, mention them.
    - Never make up information that is not present in the retrieved context.
    """


    best_match = results[0]

    recommended = recommend_lectures(question_embedding, best_match["title"])

    confidence = best_match["confidence"]

    weak_topics_ranked = detect_weak_topics(best_match["title"], confidence)

    llm_response = inference(prompt)

    answer = llm_response.get(
        "response",
        "Sorry, I couldn't generate an answer."
    )


    return jsonify({
        "query": query,

        "answer": answer,

        "best_match": best_match,

        "recommended_lectures": recommended,

        "domain_recommendations": [],

        "weak_topics_ranked": weak_topics_ranked,

        "other_matches": results[1:]
    })



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)