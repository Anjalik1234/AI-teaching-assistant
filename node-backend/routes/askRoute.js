const express = require("express");
const router = express.Router();

const { askQuery } = require("../controllers/askController");

router.post("/ask", askQuery);

module.exports = router;