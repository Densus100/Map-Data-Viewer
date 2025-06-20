# Map Data Viewer

A web-based tool for visualizing and analyzing map-related data using clustering algorithms. The project combines a Node.js/Express backend, a simple HTML/JavaScript frontend, and Python scripts for data processing and machine learning.

## Tech Stack

- **Frontend:** HTML, JavaScript
- **Backend:** Node.js (Express.js)
- **Algorithms:** Python (see `algorithm.py` and scripts in `uploads/`)

## Features

- Serve and visualize Excel data files on an interactive map
- Upload new Excel files and replace the old data
- Run clustering algorithms (KMeans, GMM, Hierarchical, etc.) via Python scripts
- Display clustering results and related images (e.g., clusters, PCA, dendrograms)
- Interactive map with clickable regions

## Folder Structure

```
.
├── algorithm.py
├── package.json
├── server.js
├── static/
│   ├── index.html
│   ├── img/
│   ├── js/
│   └── ...
├── uploads/
│   ├── data_ready.xlsx
│   ├── prepare_data.py
│   ├── requirements.txt
│   ├── uploaded_file.xlsx
│   ├── kmeans_model/
│   ├── gmm_model/
│   ├── hierarchical_model/
│   └── ...
└── README.md
```

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/)
- [Python 3.x](https://www.python.org/downloads/)

### Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/sannnttiii/Map-Data-Viewer.git
   cd Map-Data-Viewer
   ```

2. **Install Node.js dependencies:**

   ```sh
   npm install
   ```

3. **Install Python dependencies:**
   ```sh
   pip install -r uploads/requirements.txt
   ```

### Running the Project

1. **Start the backend server:**

   ```sh
   node server.js
   ```

   The Express server will run at [http://localhost:3000](http://localhost:3000).

2. **Start the frontend:**
   - Open `static/index.html` directly in your browser, or
   - Use a static server (e.g., VS Code Live Server extension) to serve the `static/` folder (default port: 5500).

## Usage

- Upload Excel files and view the data on the interactive map.
- Select clustering options to run Python scripts and visualize results.
- Click on map regions for more detailed information.

## Customization

- **Python scripts:** Add or modify clustering algorithms in `uploads/`.
- **Frontend:** Update `static/index.html` and `static/js/script.js` for UI changes.
- **Map images:** Replace or add images in `static/img/`.

## License

Open Source

---

_Created for educational and data visualization purposes._
