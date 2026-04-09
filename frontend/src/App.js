import React, { useState, useEffect } from "react";
import axios from "axios";
import { motion } from "framer-motion";

const videoMap = {
  1: "tVzUXW6siu0",
  2: "kJEsTjH5mVg",
  3: "BGeDBfCIqas",
  4: "nXba2-mgn1k",
  12: "5xFRg_TzlAg"
};

const styles = {
  app: {
    minHeight: "100vh",
    backgroundColor: "#5840400f",
    color: "#ffffff",
    fontFamily: "system-ui, -apple-system, sans-serif",
    display: "flex",
    flexDirection: "column",
    margin: "0",
    padding: "0"
  },
  container: {
    maxWidth: "1200px",
    width: "100%",
    margin: "0 auto",
    padding: "40px 20px",
    boxSizing: "border-box"
  },

  // Center Landing
  landingContainer: {
    flex: 1,
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    minHeight: "80vh"
  },
  gradientTitle: {
    fontSize: "clamp(2rem, 8vw, 4rem)", // Responsive font size
    fontWeight: "bold",
    background: "linear-gradient(90deg, #6366f1, #22d3ee)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
    textAlign: "center"
  },

  // Search Hero
  heroContainer: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    minHeight: "70vh"
  },
  heroContent: {
    width: "100%",
    maxWidth: "600px",
    textAlign: "center"
  },
  heroTitle: {
    fontSize: "2rem",
    fontWeight: "bold",
    marginBottom: "24px"
  },
  searchRow: {
    display: "flex",
    gap: "10px",
    marginBottom: "20px"
  },
  input: {
    flex: 1,
    padding: "12px 16px",
    fontSize: "16px",
    border: "1px solid #334155",
    borderRadius: "8px",
    backgroundColor: "#1e293b",
    color: "#ffffff",
    outline: "none",
    minWidth: "0" // Prevents input from breaking flex layout
  },
  button: {
    padding: "12px 24px",
    fontSize: "16px",
    backgroundColor: "#6366f1",
    color: "#ffffff",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontWeight: "500",
    whiteSpace: "nowrap"
  },
  chipsContainer: {
    display: "flex",
    gap: "8px",
    marginTop: "20px",
    flexWrap: "wrap",
    justifyContent: "center"
  },
  chip: {
    padding: "6px 14px",
    backgroundColor: "#334155",
    color: "#cbd5e1",
    borderRadius: "20px",
    cursor: "pointer",
    fontSize: "13px",
    border: "1px solid #475569",
    transition: "all 0.2s"
  },

  // Results Dashboard
  dashboard: {
    display: "flex",
    flexDirection: "column",
    gap: "20px",
    marginTop: "20px"
  },
  row: {
    display: "flex",
    gap: "20px",
    flexWrap: "wrap" // Ensures responsiveness on smaller screens
  },
  panel: {
    backgroundColor: "#1e293b",
    borderRadius: "12px",
    padding: "24px",
    border: "1px solid #334155"
  },
  searchPanel: {
    flex: "1 1 350px", // Grow/shrink but aim for 350px
  },
  videoPanel: {
    flex: "2 1 500px",
  },
  bottomPanel: {
    flex: "1 1 400px",
  },
  panelTitle: {
    fontSize: "1.25rem",
    fontWeight: "600",
    marginBottom: "20px"
  },
  iframe: {
    width: "100%",
    aspectRatio: "16/9", // Keeps video proportions perfect
    border: "none",
    borderRadius: "8px"
  },
  chipList: {
    display: "flex",
    flexDirection: "column",
    gap: "10px"
  },
  recommendationChip: {
    padding: "12px 16px",
    backgroundColor: "#0f172a",
    color: "#e2e8f0",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "14px",
    border: "1px solid #334155",
    textAlign: "left"
  },
  topicItem: {
    marginBottom: "16px"
  },
  topicLabel: {
    fontSize: "14px",
    marginBottom: "8px",
    color: "#94a3b8"
  },
  progressBarBg: {
    height: "10px",
    backgroundColor: "#0f172a",
    borderRadius: "5px",
    overflow: "hidden"
  },
  progressBarFill: {
    height: "100%",
    backgroundColor: "#22d3ee",
    borderRadius: "5px",
    transition: "width 0.5s ease-out"
  }
};

function App() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [showSearch, setShowSearch] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setShowSearch(true), 2500);
    return () => clearTimeout(timer);
  }, []);

  const handleSearch = async (searchQuery = query) => {
    if (!searchQuery) return;
    try {
      const response = await axios.post(
        "https://ai-teaching-node-backend.onrender.com/api/ask",
        { query: searchQuery }
      );
      setResult(response.data);
    } catch (error) {
      console.error("Search failed:", error);
    }
  };

  return (
    <div style={styles.app}>
      <div style={styles.container}>

        {!showSearch && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            style={styles.landingContainer}
          >
            <h1 style={styles.gradientTitle}>AI Teaching Assistant</h1>
          </motion.div>
        )}

        {showSearch && !result && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={styles.heroContainer}
          >
            <div style={styles.heroContent}>
              <h2 style={styles.heroTitle}>What would you like to learn?</h2>
              <div style={styles.searchRow}>
                <input
                  type="text"
                  placeholder="e.g. How to use Flexbox..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  style={styles.input}
                />
                <button style={styles.button} onClick={() => handleSearch()}>
                  Search
                </button>
              </div>
              <div style={styles.chipsContainer}>
                {["First HTML website", "VS Code Setup", "CSS Selectors", "React Hooks"].map((example) => (
                  <button
                    key={example}
                    style={styles.chip}
                    onClick={() => {
                      setQuery(example);
                      handleSearch(example);
                    }}
                  >
                    {example}
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {result && (
          <div style={styles.dashboard}>
            <div style={styles.row}>
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                style={{ ...styles.panel, ...styles.searchPanel }}
              >

                <div style={{ textAlign: "center" }}>

                  <h2 style={{
                    fontSize: "1.8rem",
                    marginBottom: "20px"
                  }}>
                    What would you like to learn?
                  </h2>

                  <div style={styles.searchRow}>

                    <input
                      type="text"
                      placeholder="e.g. How to use Flexbox..."
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      style={styles.input}
                    />

                    <button
                      style={styles.button}
                      onClick={() => handleSearch()}
                    >
                      Search
                    </button>

                  </div>


                  {/* Suggestion chips also visible after search */}

                  <div style={{
                    ...styles.chipsContainer,
                    marginTop: "15px"
                  }}>

                    {[
                      "First HTML website",
                      "VS Code Setup",
                      "CSS Selectors",
                      "React Hooks"
                    ].map((example) => (

                      <button
                        key={example}
                        style={styles.chip}
                        onClick={() => {
                          setQuery(example);
                          handleSearch(example);
                        }}
                      >
                        {example}
                      </button>

                    ))}

                  </div>
                  {result?.best_match && (
                    <div
                      style={{
                        marginTop: "25px",
                        padding: "18px",
                        backgroundColor: "#0f172a",
                        borderRadius: "10px",
                        border: "1px solid #334155",
                        textAlign: "left"
                      }}
                    >
                      <h3 style={{ marginBottom: "10px", color: "#e2e8f0" }}>
                        {result.best_match.title}
                      </h3>

                      <p style={{ margin: "4px 0", color: "#cbd5e1" }}>
                        <strong>Video:</strong> {result.best_match.video_number}
                      </p>

                      <p style={{ margin: "4px 0", color: "#cbd5e1" }}>
                        <strong>Start Time:</strong>{" "}
                        {Math.floor(result.best_match.start / 60)}:
                        {String(Math.floor(result.best_match.start % 60)).padStart(2, "0")}
                      </p>

                      <p style={{ margin: "4px 0", color: "#cbd5e1" }}>
                        <strong>Confidence:</strong>{" "}
                        {result.best_match.confidence.toFixed(3)}
                      </p>
                    </div>
                  )}

                </div>

              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                style={{ ...styles.panel, ...styles.videoPanel }}
              >
                <h4 style={styles.panelTitle}>Lecture Playback</h4>
                <iframe
                  style={styles.iframe}
                  src={`https://www.youtube.com/embed/${videoMap[result.best_match.video_number]}?start=${Math.floor(result.best_match.start)}`}
                  title="Lecture Player"
                  allowFullScreen
                />
              </motion.div>
            </div>

            <div style={styles.row}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                style={{ ...styles.panel, ...styles.bottomPanel }}
              >
                <h4 style={styles.panelTitle}>Recommended Lectures</h4>
                <div style={styles.chipList}>
                  {result.recommended_lectures?.map((lecture, index) => (
                    <div
                      key={index}
                      onClick={() => handleSearch(lecture)}
                      style={{
                        background: "#0f172a",
                        padding: "16px",
                        borderRadius: "10px",
                        border: "1px solid #334155",
                        cursor: "pointer",
                        transition: "0.2s",
                      }}
                    >
                      📘 {lecture}
                    </div>
                  ))}
                </div>

                {result.domain_recommendations?.length > 0 && (
                  <>
                    <h4 style={{ ...styles.panelTitle, marginTop: "20px" }}>
                      Related Topics from Other Domains
                    </h4>

                    <div style={styles.chipList}>
                      {result.domain_recommendations.map((topic, index) => (
                        <div
                          key={index}
                          onClick={() => handleSearch(topic)}
                          style={{
                            background: "#0f172a",
                            padding: "16px",
                            borderRadius: "10px",
                            border: "1px solid #334155",
                            cursor: "pointer",
                            transition: "0.2s",
                          }}
                        >
                          🧠 {topic}
                        </div>
                      ))}
                    </div>
                  </>
                )}
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                style={{ ...styles.panel, ...styles.bottomPanel }}
              >
                <h4 style={styles.panelTitle}>Topic Proficiency</h4>

                <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                  {result.weak_topics_ranked?.map((topic, index) => {

                    let level = "";
                    let color = "";

                    if (topic.score >= 7) {
                      level = "Strong";
                      color = "#22c55e";
                    }
                    else if (topic.score >= 4) {
                      level = "Moderate";
                      color = "#facc15";
                    }
                    else {
                      level = "Needs Practice";
                      color = "#ef4444";
                    }

                    return (
                      <div
                        key={index}
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          background: "#0f172a",
                          padding: "14px 16px",
                          borderRadius: "8px",
                          border: "1px solid #334155"
                        }}
                      >
                        <span style={{ color: "#e2e8f0" }}>
                          {topic.topic}
                        </span>

                        <span
                          style={{
                            background: color,
                            width: "100px",
                            height: "32px",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            borderRadius: "6px",
                            fontSize: "13px",
                            fontWeight: "600",
                            color: "#000"
                          }}
                        >
                          {level}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </motion.div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;