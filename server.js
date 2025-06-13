const express = require("express");
const path = require("path");
const fs = require("fs");
const multer = require("multer");
const cors = require("cors");
const { exec } = require("child_process");
const { spawn } = require("child_process"); // Untuk menjalankan script Python

const app = express();
const port = 3000;

app.use(cors({ origin: "*" }));

// Serve static files (e.g., CSS, JS, images) from the "static" directory
app.use("/static", express.static(path.join(__dirname, "static")));

// Serve uploaded files from the "uploads" directory
app.use("/uploads", express.static(path.join(__dirname, "uploads"), {}));

const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, path.join(__dirname, "uploads"));
  },
  filename: function (req, file, cb) {
    cb(null, "uploaded_file.xlsx");
  },
});

const upload = multer({ storage: storage });

// Endpoint untuk mendapatkan file hasil pemrosesan (data_view.xlsx)
app.get("/uploads/excel-file", (req, res) => {
  const filePath = path.join(__dirname, "uploads", "data_view.xlsx");

  if (!fs.existsSync(filePath)) {
    return res.status(404).send("File not found.");
  }

  res.sendFile(filePath);
});

// Endpoint untuk mendapatkan file hasil pemrosesan (data_view_tingkat.xlsx)
app.get("/uploads/excel-file/data_view_tingkat", (req, res) => {
  const filePath = path.join(__dirname, "uploads", "data_view_tingkat.xlsx");

  if (!fs.existsSync(filePath)) {
    return res.status(404).send("File not found.");
  }

  res.sendFile(filePath);
});


// Endpoint untuk mendapatkan file hasil pemrosesan (data_view_status.xlsx)
app.get("/uploads/excel-file/data_view_status", (req, res) => {
  const filePath = path.join(__dirname, "uploads", "data_view_status.xlsx");

  if (!fs.existsSync(filePath)) {
    return res.status(404).send("File not found.");
  }

  res.sendFile(filePath);
});

// Endpoint untuk mendapatkan file hasil pemrosesan (data_view_lokasi.xlsx)
app.get("/uploads/excel-file/data_view_lokasi", (req, res) => {
  const filePath = path.join(__dirname, "uploads", "data_view_lokasi.xlsx");

  if (!fs.existsSync(filePath)) {
    return res.status(404).send("File not found.");
  }

  res.sendFile(filePath);
});

// Endpoint untuk mendapatkan file hasil pemrosesan (data_view_provinsi.xlsx)
app.get("/uploads/excel-file/data_view_provinsi", (req, res) => {
  const filePath = path.join(__dirname, "uploads", "data_view_provinsi.xlsx");

  if (!fs.existsSync(filePath)) {
    return res.status(404).send("File not found.");
  }

  res.sendFile(filePath);
});

// Endpoint untuk mendapatkan file hasil pemrosesan (data_view_jeniskelamin.xlsx)
app.get("/uploads/excel-file/data_view_jeniskelamin", (req, res) => {
  const filePath = path.join(__dirname, "uploads", "data_view_jeniskelamin.xlsx");

  if (!fs.existsSync(filePath)) {
    return res.status(404).send("File not found.");
  }

  res.sendFile(filePath);
});



// Last update harus mengambil dari data_view.xlsx
app.get("/uploads/excel-file/last-update", (req, res) => {
  const filePath = path.join(__dirname, "uploads", "data_view.xlsx");

  if (!fs.existsSync(filePath)) {
    return res.status(404).send("File not found.");
  }

  const stats = fs.statSync(filePath);
  const lastModified = stats.mtime;

  res.json({ lastModified: lastModified.toISOString() });
});

// Upload file, jalankan prepare_data.py, dan pastikan data_view.xlsx tersedia
app.post("/upload", upload.single("file"), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ message: "Tidak ada file yang di-upload" });
  }

  console.log("File uploaded:", req.file);

  const dataReadyPath = path.join(__dirname, "uploads", "data_view.xlsx");

  console.log("Menjalankan prepare_data.py...");
  const pythonScriptPath = path.join(__dirname, "uploads", "prepare_data.py");
  const pythonProcess = spawn("python3", [pythonScriptPath]);

  let outputData = "";
  let errorData = "";

  pythonProcess.stdout.on("data", (data) => {
    outputData += data.toString();
    console.log("Python Output:", data.toString()); // Logging untuk debug
  });

  pythonProcess.stderr.on("data", (data) => {
    errorData += data.toString();
    console.error("Python Error:", data.toString()); // Logging untuk debug
  });

  pythonProcess.on("close", (code) => {
    console.log(`prepare_data.py selesai dengan kode ${code}`);

    if (code === 0) {
      // Cek apakah data_view.xlsx ada setelah proses selesai
      if (fs.existsSync(dataReadyPath)) {
        res.json({
          message: "File berhasil di-upload dan diproses!",
          output: outputData,
        });
      } else {
        res.status(500).json({
          message:
            "File berhasil di-upload tetapi hasil proses tidak ditemukan.",
          output: outputData,
          error: errorData,
        });
      }
    } else {
      res.status(500).json({
        message: "Gagal memproses file.",
        error: errorData || "Terjadi kesalahan saat menjalankan script Python.",
      });
    }
  });
});

app.get("/load-content/:tab", (req, res) => {
  const tab = req.params.tab;
  const modelMap = {
    tab1: {
      script: "kmeans_model/kmeans_train_model.py",
      txt: "kmeans_model/kmeans_html_results.txt",
      images: [
        "kmeans_model/kmeans_clusters.png",
        "kmeans_model/kmeans_pca.png",
        "kmeans_model/kmeans_confusion_matrix.png",
      ],
    },
    tab2: {
      script: "gmm_model/gmm_train_model.py",
      txt: "gmm_model/gmm_html_results.txt",
      images: [
        "gmm_model/gmm_clusters.png",
        "gmm_model/gmm_pca.png",
        "gmm_model/gmm_confusion_matrix.png",
      ],
    },
    tab3: {
      script: "hierarchical_model/hierarchical_train_model.py",
      txt: "hierarchical_model/hierarchical_html_results.txt",
      images: [
        "hierarchical_model/hierarchical_dendrogram.png",
        "hierarchical_model/hierarchical_clusters.png",
        "hierarchical_model/hierarchical_pca.png",
        "hierarchical_model/hierarchical_confusion_matrix.png",
      ],
    },
    // Add KMeans Elbow model handling
    tab4: {
      script: "kmeans_elbow_model/kmeans_elbow_train_model.py",
      txt: "kmeans_elbow_model/kmeans_elbow_html_results.txt",
      images: [
        "kmeans_elbow_model/kmeans_elbow_clusters.png",
        "kmeans_elbow_model/kmeans_elbow_pca.png",
        "kmeans_elbow_model/kmeans_elbow_fit_time.png",
      ],
    },
    // --- Add these for GMM Elbow and Hierarchical Elbow ---
    tab5: {
      script: "gmm_elbow_model/gmm_elbow_train_model.py",
      txt: "gmm_elbow_model/gmm_elbow_html_results.txt",
      images: [
        "gmm_elbow_model/gmm_elbow_clusters.png",
        "gmm_elbow_model/gmm_elbow_pca.png",
        "gmm_elbow_model/gmm_elbow_fit_time.png"
      ],
    },
    tab6: {
      script: "hierarchical_elbow_model/hierarchical_elbow_train_model.py",
      txt: "hierarchical_elbow_model/hierarchical_elbow_html_results.txt",
      images: [
        "hierarchical_elbow_model/hierarchical_elbow_dendrogram.png",
        "hierarchical_elbow_model/hierarchical_elbow_clusters.png",
        "hierarchical_elbow_model/hierarchical_elbow_pca.png",
        "hierarchical_elbow_model/hierarchical_elbow_fit_time.png"
      ],
    },
    // ------------------------------------------------------
  };

  const model = modelMap[tab];
  if (!model) {
    return res.status(400).send("Invalid tab name.");
  }

  const scriptPath = path.join(__dirname, "uploads", model.script);

  // Run Python script
  const pythonProcess = spawn("python3", [scriptPath]);

  pythonProcess.stdout.on("data", (data) => {
    console.log(`Python Output: ${data}`);
  });

  pythonProcess.stderr.on("data", (data) => {
    console.error(`Error: ${data}`);
  });

  const filePath = path.join(__dirname, "uploads", model.txt);

  pythonProcess.on("close", (code) => {
    console.log(`Python script finished with code ${code}`);

    if (!fs.existsSync(filePath)) {
      return res.status(404).send("File not found.");
    }

    fs.readFile(filePath, "utf8", (err, data) => {
      if (err) {
        return res.status(500).send("Error reading file.");
      }
      res.json({
        images: model.images,
        content: data,
      });
    });
  });
});

app.get("/check-existing-images/:tab", (req, res) => {
  const tab = req.params.tab;
  const modelMap = {
    tab1: {
      txt: "kmeans_model/kmeans_html_results.txt",
      images: [
        "kmeans_model/kmeans_clusters.png",
        "kmeans_model/kmeans_pca.png",
        "kmeans_model/kmeans_confusion_matrix.png",
      ],
    },
    tab2: {
      txt: "gmm_model/gmm_html_results.txt",
      images: [
        "gmm_model/gmm_clusters.png",
        "gmm_model/gmm_pca.png",
        "gmm_model/gmm_confusion_matrix.png",
      ],
    },
    tab3: {
      txt: "hierarchical_model/hierarchical_html_results.txt",
      images: [
        "hierarchical_model/hierarchical_dendrogram.png",
        "hierarchical_model/hierarchical_clusters.png",
        "hierarchical_model/hierarchical_pca.png",
        "hierarchical_model/hierarchical_confusion_matrix.png",
      ],
    },
    // Add KMeans Elbow model handling
    tab4: {
      txt: "kmeans_elbow_model/kmeans_elbow_html_results.txt",
      images: [
        "kmeans_elbow_model/kmeans_elbow_clusters.png",
        "kmeans_elbow_model/kmeans_elbow_pca.png",
        "kmeans_elbow_model/kmeans_elbow_fit_time.png",
      ],
    },
    // --- Add these for GMM Elbow and Hierarchical Elbow ---
    tab5: {
      txt: "gmm_elbow_model/gmm_elbow_html_results.txt",
      images: [
        "gmm_elbow_model/gmm_elbow_clusters.png",
        "gmm_elbow_model/gmm_elbow_pca.png",
        "gmm_elbow_model/gmm_elbow_fit_time.png"
      ],
    },
    tab6: {
      txt: "hierarchical_elbow_model/hierarchical_elbow_html_results.txt",
      images: [
        "hierarchical_elbow_model/hierarchical_elbow_dendrogram.png",
        "hierarchical_elbow_model/hierarchical_elbow_clusters.png",
        "hierarchical_elbow_model/hierarchical_elbow_pca.png",
        "hierarchical_elbow_model/hierarchical_elbow_fit_time.png"
      ],
    },
    // ------------------------------------------------------
  };

  const model = modelMap[tab];
  if (!model) {
    return res.status(400).send("Invalid tab name.");
  }

  const txtPath = path.join(__dirname, "uploads", model.txt);
  const txtExists = fs.existsSync(txtPath);

  let txtContent = "";
  if (txtExists) {
    txtContent = fs.readFileSync(txtPath, "utf8"); // Baca isi file txt jika ada
  }

  const existingImages = model.images.filter((img) =>
    fs.existsSync(path.join(__dirname, "uploads", img))
  );

  res.json({
    images: existingImages,
    text: txtExists ? txtContent : null, // Jika tidak ada, return null
  });
});

app.get("/run-kmeans-pdf", (req, res) => {
  const scriptPath = path.join(
    __dirname,
    "uploads",
    "kmeans_model",
    "kmeans_pdf.py"
  );

  exec(`python3 ${scriptPath}`, (err, stdout, stderr) => {
    if (err) {
      console.error("Error executing Python script:", err);
      return res.status(500).send("Error generating KMeans PDF");
    }
    res.sendFile(
      path.join(__dirname, "uploads", "kmeans_model", "kmeans_report.pdf")
    );
  });
});

app.get("/run-gmm-pdf", (req, res) => {
  const scriptPath = path.join(__dirname, "uploads", "gmm_model", "gmm_pdf.py");

  exec(`python3 ${scriptPath}`, (err, stdout, stderr) => {
    if (err) {
      console.error("Error executing Python script:", err);
      return res.status(500).send("Error generating GMM PDF");
    }
    res.sendFile(
      path.join(__dirname, "uploads", "gmm_model", "gmm_report.pdf")
    );
  });
});

app.get("/run-hierarchical-pdf", (req, res) => {
  const scriptPath = path.join(
    __dirname,
    "uploads",
    "hierarchical_model",
    "hierarchical_pdf.py"
  );

  exec(`python3 ${scriptPath}`, (err, stdout, stderr) => {
    if (err) {
      console.error("Error executing Python script:", err);
      return res.status(500).send("Error generating Hierarchical PDF");
    }
    res.sendFile(
      path.join(
        __dirname,
        "uploads",
        "hierarchical_model",
        "hierarchical_report.pdf"
      )
    );
  });
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
