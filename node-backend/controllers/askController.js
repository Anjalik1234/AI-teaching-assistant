const axios = require("axios");

exports.askQuery = async (req, res) => {
  try {
    const { query } = req.body;

    if (!query) {
      return res.status(400).json({
        error: "Query is required",
      });
    }

    // Call Python ML service
    const response = await axios.post(
      "http://localhost:5001/semantic-search",
      { query }
    );

    res.json(response.data);

  } catch (error) {
    console.error(error.message);

    res.status(500).json({
      error: "Error communicating with ML service",
    });
  }
};