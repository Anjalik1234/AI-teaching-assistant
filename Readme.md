# 🎓 AI Teaching Assistant using RAG

An AI-powered Teaching Assistant that allows students to ask natural language questions about a video course and instantly receive context-aware answers, relevant timestamps, lecture recommendations, and personalized learning insights.

The project uses a Retrieval-Augmented Generation (RAG) pipeline built from scratch with Whisper, BGE-M3 embeddings, Llama 3.2, Flask, Node.js, and React.

---

## 🚀 Features

- 🎥 Converts lecture videos into searchable knowledge using Whisper transcription.
- 🔍 Semantic search over lecture transcripts using BGE-M3 embeddings.
- 🤖 Generates context-aware answers using Llama 3.2 through Ollama.
- ⏱ Provides exact lecture timestamps for relevant explanations.
- 📚 Recommends semantically related lectures based on embedding similarity.
- 📈 Tracks learner proficiency dynamically using retrieval confidence.
- 💾 Persists learner progress across sessions.
- 🌐 Full-stack architecture using React, Node.js, and Flask.

---

# 🏗️ System Architecture

```
                Lecture Videos
                       │
                       ▼
          Whisper Speech-to-Text
                       │
                       ▼
             Transcript Chunks (JSON)
                       │
                       ▼
          BGE-M3 Embedding Generation
                       │
                       ▼
             embeddings.joblib
                       │
                       ▼
               Flask ML Service
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
 Semantic Retrieval          Lecture Recommendation
        │                             │
        └──────────────┬──────────────┘
                       ▼
            Llama 3.2 (Ollama)
                       │
                       ▼
             AI Generated Response
                       │
                       ▼
         Node.js Backend API Layer
                       │
                       ▼
               React Frontend
```

---

# 🧠 Tech Stack

### Frontend
- React.js
- Axios
- CSS

### Backend
- Node.js
- Express.js

### ML Service
- Flask
- Pandas
- NumPy
- Scikit-Learn

### AI Models
- Whisper (Speech-to-Text)
- BGE-M3 (Embeddings)
- Llama 3.2 (Answer Generation)
- Ollama

---

# 📂 Project Structure

```
Project-2(RAG)
│
├── data-preprocessing/
│   ├── video_to_mp3.py
│   ├── mp3_to_json.py
│   └── preprocess_json.py
│
├── dataset/
│   ├── audios/
│   └── jsons/
│
├── frontend/
│
├── node-backend/
│
├── ml-service/
│   ├── app.py
│   ├── embeddings.joblib
│   └── domain_topics.py
│
├── process_incoming.py
│
└── README.md
```

---

# ⚙️ Working Pipeline

## 1. Data Preprocessing

- Convert lecture videos to MP3 using FFmpeg.
- Transcribe audio into English using Whisper.
- Split transcripts into timestamped chunks.
- Generate embeddings using BGE-M3.
- Store all chunk embeddings inside `embeddings.joblib`.

---

## 2. Retrieval Pipeline

When a user asks a question:

1. Generate an embedding for the query.
2. Compute cosine similarity against all transcript chunks.
3. Rank chunks using:
   - Semantic Similarity
   - Keyword Overlap
4. Retrieve the Top-K relevant chunks.

---

## 3. Response Generation

The retrieved chunks are formatted into a prompt and passed to Llama 3.2.

The model generates:

- Context-aware answer
- Relevant lecture
- Timestamp reference
- Beginner-friendly explanation

---

## 4. Lecture Recommendation

Instead of recommending lectures sequentially, the system:

- Computes embeddings for every lecture by averaging transcript chunk embeddings.
- Compares the user query embedding against all lecture embeddings.
- Recommends the most semantically similar lectures.

This allows recommendations to automatically scale as more lectures are added.

---

## 5. Learner Proficiency Tracking

The assistant maintains a learner profile by tracking:

- Number of questions asked per topic
- Average retrieval confidence
- Learning status

Topics are automatically inferred from retrieved lectures without hardcoded mappings.

Example:

```
HTML Basics

Questions Asked: 5

Average Retrieval Score: 0.84

Status: Strong
```

The learner profile is stored in a JSON file, allowing progress to persist across sessions.

---

# 🛠️ Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/AI-Teaching-Assistant-RAG.git
cd AI-Teaching-Assistant-RAG
```

---

## Install Dependencies

### Frontend

```bash
cd frontend
npm install
```

### Backend

```bash
cd node-backend
npm install
```

### ML Service

```bash
cd ml-service
pip install -r requirements.txt
```

---

## Install Ollama Models

```bash
ollama pull llama3.2
ollama pull bge-m3
```

---

## Run ML Service

```bash
cd ml-service
python app.py
```

---

## Run Backend

```bash
cd node-backend
node server.js
```

---

## Run Frontend

```bash
cd frontend
npm start
```

---

# 📊 Future Improvements

- FAISS vector database for faster retrieval.
- Multi-course support.
- User authentication.
- Real-time indexing of uploaded lectures.
- Instructor analytics dashboard.

---

# 🎯 Learning Outcomes

This project demonstrates practical implementation of:

- Retrieval-Augmented Generation (RAG)
- Semantic Search
- Large Language Models
- Vector Embeddings
- Recommendation Systems
- Speech-to-Text Processing
- Full-Stack Development
- AI-powered Educational Systems

---
