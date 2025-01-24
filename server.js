const express = require("express");
const path = require("path");
const fs = require("fs");
const multer = require("multer");
const cors = require("cors");
const { spawn } = require("child_process"); // Untuk menjalankan script Python

const app = express();
const port = 3000;

app.use(cors());

const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, path.join(__dirname, "uploads"));
  },
  filename: function (req, file, cb) {
    cb(null, "uploaded_file.xlsx");
  },
});

const upload = multer({ storage: storage });

// check file exists
app.get("/uploads/excel-file", (req, res) => {
  const filePath = path.join(__dirname, "uploads", "uploaded_file.xlsx");

  if (!fs.existsSync(filePath)) {
    return res.status(404).send("File not found.");
  }

  res.sendFile(filePath);
});

// lastupdate
app.get("/uploads/excel-file/last-update", (req, res) => {
  const filePath = path.join(__dirname, "uploads", "uploaded_file.xlsx");

  if (!fs.existsSync(filePath)) {
    return res.status(404).send("File not found.");
  }

  const stats = fs.statSync(filePath);
  const lastModified = stats.mtime; // Get last modification time

  // Send last update
  res.json({ lastModified: lastModified.toISOString() });
});

// Endpoint untuk upload dan mengganti file Excel yang lama
app.post("/upload", upload.single("file"), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ message: "Tidak ada file yang di-upload" });
  }

  console.log("File uploaded and replaced:", req.file);
  res.json({ message: "File berhasil di-upload dan diganti!" });
});

app.get("/run-python", (req, res) => {
  const pythonScriptPath = path.join(__dirname, "algorithm.py");
  const pythonProcess = spawn("python3", [pythonScriptPath]);
  let outputData = "";

  pythonProcess.stdout.on("data", (data) => {
    outputData += data.toString(); // Append data from py
  });

  pythonProcess.stderr.on("data", (data) => {
    console.error(`Error: ${data}`);
  });

  // On process close, send the response back to the frontend
  pythonProcess.on("close", (code) => {
    console.log(`Python script finished with exit code ${code}`);
    res.send({ message: outputData }); // Send the output back
  });
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
