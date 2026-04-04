import React, { useState } from "react";
import axios from "axios";

import {
  Container,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Stack,
  Chip
} from "@mui/material";


const videoMap = {
  1: "tVzUXW6siu0",
  2: "kJEsTjH5mVg",
  3: "BGeDBfCIqas",
  4: "nXba2-mgn1k",
  12: "5xFRg_TzlAg"
};

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
};

function App() {

  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);

  const handleSearch = async (searchQuery = query) => {

    if (!searchQuery) return;

    try {

      const response = await axios.post(
        "https://ai-teaching-node-backend.onrender.com/api/ask",
        { query: searchQuery }
      );

      setQuery(searchQuery);

      setResult(response.data);

    } catch (error) {

      console.error("Error fetching data:", error);

    }
  };

  return (

    <Container maxWidth="md" style={{ marginTop: "40px" }}>

      {/* TITLE */}

      <Typography variant="h4" gutterBottom>
        AI Teaching Assistant
      </Typography>


      {/* SEARCH BAR */}

      <TextField
        fullWidth
        label="Ask about any lecture topic..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      <Button
        variant="contained"
        sx={{ marginTop: 2 }}
        onClick={() => handleSearch()}
      >
        Search
      </Button>


      {/* BEST MATCH CARD */}

      {result?.best_match && videoMap[result.best_match.video_number] && (

        <Card sx={{ marginTop: 3 }}>
          <CardContent>

            <Typography variant="h6">
              Lecture Playback
            </Typography>

            <iframe
              width="80%"
              height="300"
              src={`https://www.youtube.com/embed/${videoMap[result.best_match.video_number]
                }?start=${Math.floor(result.best_match.start)}`}
              title="Lecture Player"
              allowFullScreen
            />

          </CardContent>
        </Card>

      )}

      {result?.best_match && (

        <Card sx={{ marginTop: 4 }}>
          <CardContent>

            <Typography variant="h6">
              {result.best_match.title}
            </Typography>

            <Typography>
              Video: {result.best_match.video_number}
            </Typography>

            <Typography>
              Start Time: {formatTime(result.best_match.start)}
            </Typography>

            <Typography>
              Confidence: {result.best_match.confidence?.toFixed(3)}
            </Typography>

          </CardContent>
        </Card>

      )}


      {/* RECOMMENDED LECTURES (CLICKABLE) */}

      {result?.recommended_lectures?.length > 0 && (

        <>

          <Typography variant="h6" sx={{ marginTop: 4 }}>
            Recommended Lectures
          </Typography>

          <Stack direction="row" spacing={2} sx={{ marginTop: 2 }}>

            {result.recommended_lectures.map((lecture, index) => (

              <Chip
                key={index}
                label={lecture}
                clickable
                color="primary"
                onClick={() => handleSearch(lecture)}
              />

            ))}

          </Stack>

        </>

      )}


      {/* WEAK TOPICS PANEL */}

      {result?.weak_topics_detected?.length > 0 && (

        <Card sx={{ marginTop: 4 }}>
          <CardContent>

            <Typography variant="h6">
              Weak Topics Detected
            </Typography>

            {result.weak_topics_detected.map((topic, index) => (

              <Typography key={index}>
                • {topic}
              </Typography>

            ))}

          </CardContent>
        </Card>

      )}

    </Container>
  );
}

export default App;