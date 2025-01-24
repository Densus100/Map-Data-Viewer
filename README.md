---Map Data Viewer---

Tech Stack
Frontend: HTML, JavaScript (Node.js)
Backend: Express.js
Algorithm: Python (algorithm.py)

Features
Serve Excel files from the server
Upload new Excel file and replace the old one
Call and execute Python scripts from the Express server

Getting Started
Prerequisites
Make sure you have the following installed on your machine:
- Node.js - Download and install from https://nodejs.org.
- Python (for executing the algorithm) - Install from https://www.python.org/downloads/.

Installation
1. Clone the repository: git clone https://github.com/sannnttiii/Map-Data-Viewer.git
2. Navigate into the project directory
3. Install dependencies : npm install
(Optional) Set the port if needed (defaults to 5500 for frontend, 3000 for backend).
4. Running the Project : Start the backend server: node server.js
- The Express server will run at http://localhost:3000.
- For the frontend, you can use a local static server (e.g., Visual Studio Code with Live Server extension) or run it directly by opening static/index.html.
- The default URL for frontend would be: http://localhost:5500/static/index.html.
5. Test the functionality of uploading Excel files and triggering Python scripts directly from your frontend page (button in tab interface).

Usage
Upload New File: The previous Excel file will be replaced with the new one upon upload.
Trigger Python Algorithm: The Express server calls algorithm.py when required.
