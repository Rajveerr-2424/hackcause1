# Drought Engine AI - District Command Center

An AI-driven, proactive drought warning and smart tanker management system designed to transition water governance from reactive crisis response to predictive planning. 

## Project Overview

**Drought Engine AI** is a modern web application built for district administrators and disaster management authorities. Instead of waiting for villages to run out of water, the system actively monitors and flags high-risk areas using a specialized **Water Stress Index**, allowing officials to deploy resources (like water tankers) *before* a crisis hits.

### The Core Problem It Solves
Traditional drought management is reactive. Authorities only dispatch water when villages send emergency requests or when ground-level reports indicate severe scarcity. This leads to delayed response times and uneven distribution of resources.

### The Solution: "Drought Engine AI"
This dashboard provides a **Live District Command Center** that visualizes water stress across all villages in real time. 

The system uses an algorithm to calculate a **Water Stress Index (0-10)** based on:
1. **Rainfall Deviation:** How much less rain a village received compared to its historical average.
2. **Groundwater Levels:** The current depth of the water table.

If a village crosses a stress index threshold of `8.0 / 10`, it is flagged as **CRITICAL**, and the system suggests an automatic or forced dispatch of a water tanker to that location.

---

## 🚀 Key Features

*   **Interactive Carto/Mapbox Visualization:** An immersive, dark-themed geographic map built with React-Leaflet that plots villages. 
*   **Real-time Threat Radar:** Critical villages (Stress > 8.0) pulsate red on the map, drawing immediate attention.
*   **"Glassmorphic" Live Dashboard:** A sleek, animated sidebar/bottom-tray (using Framer Motion) that categorizes villages into 'Critical', 'Warning', and 'Safe'.
*   **AI Stress Gauges:** Detailed inspection panels that slide in when a village is clicked, showing its exact AI stress score and demographic data.
*   **Smart Tanker Allocation UI:** Direct "Force Dispatch Tanker" buttons connected to critical zones.
*   **Automated Sorting:** The backend FastAPI server automatically ranks and returns villages based on their severity.

---

## 🛠️ Technology Stack

This project is a full-stack web application completely separated into a Backend (API) and a Frontend (UI).

### 1. Backend (Python API)
*   **Framework:** `FastAPI` (High performance, incredibly fast API routing).
*   **Database:** `SQLite` (Local file-based database for easy testing without complex server setups).
*   **ORM:** `SQLAlchemy` (Object Relational Mapper to interact with the database using Python objects).
*   **Data Validation:** `Pydantic` (Ensures data coming in and out of the API is correctly formatted).

### 2. Frontend (React Dashboard)
*   **Framework:** `React.js` powered by `Vite` (for lightning-fast building and hot-reloading).
*   **Styling:** `Tailwind CSS v4` (Utility-first CSS framework for rapid, custom design without leaving HTML/JSX).
*   **Animations:** `Framer Motion` (Powers the smooth sliding panels, progress bars, and modal popups).
*   **Maps:** `React-Leaflet` and `Leaflet.js` (Renders the interactive map using OpenStreetMap map tiles).
*   **Icons:** `Lucide-React` (Clean, modern SVG icons).

---

## ⚙️ How the Application Flows (Architecture)

1.  **The Database (`backend/drought_db.sqlite`):** Stores all structural data—village names, coordinates (Lat/Lng), populations, and their historical/current water metrics (rainfall, groundwater).
2.  **The Engine (`backend/crud.py`):** The Python server reads this data and applies the algorithm to generate the `Stress Index`. 
3.  **The API Entry Point (`backend/main.py`):** Opens a `/crisis-dashboard/` endpoint at `http://localhost:8000`. When visited, it returns a massive JSON list of all the villages sorted by who is in the most danger.
4.  **The Frontend (`frontend/src/App.jsx`):** The React app acts as the user interface. It sends an `axios` HTTP request to the Python backend every 30 seconds.
5.  **The Render:** React takes that JSON data and feeds it into the Leaflet Map (creating the dots) and the Framer Motion carousel (creating the sliding data cards).

---

## 💻 How to Run This Project Locally

You need two separate terminal windows open to run this application: one for the Backend, one for the Frontend.

### Step 1: Start the Backend (API Server)
1. Open a terminal.
2. Navigate into the backend folder:
   ```bash
   cd /workspace/hackcause1/backend
   ```
3. Activate the Python virtual environment:
   ```bash
   # On Windows:
   .\venv\Scripts\activate
   ```
4. Run the FastAPI server using Uvicorn:
   ```bash
   uvicorn main:app --reload
   ```
*(The API will now be running silently at http://127.0.0.1:8000)*

### Step 2: Start the Frontend (User Interface)
1. Open a **second, new terminal window**.
2. Navigate into the frontend folder:
   ```bash
   cd /workspace/hackcause1/frontend
   ```
3. Configure the frontend API URL:
   ```bash
   cp .env.example .env
   ```
   The default `.env.example` points to `http://127.0.0.1:8000` for direct local API usage.
   You can also keep `VITE_API_BASE_URL=/api` when using the built-in Vite proxy.
4. Start the Vite development server:
   ```bash
   npm run dev
   ```
*(The UI will open in your browser at http://localhost:5173/)*


---

## ☁️ Deploying on Vercel

This repo is now configured for a single Vercel project that serves both:
- **Frontend static app** (built from `frontend/`)
- **Backend FastAPI** as a Python serverless function at `/api` (`api/index.py`)

### Deploy steps
1. Import this repo into Vercel.
2. Keep the root directory as repository root.
3. Vercel will use `vercel.json` to build frontend + backend.
4. After deploy, frontend API calls will automatically use same-origin `/api`.

No extra rewrite setup is required.
