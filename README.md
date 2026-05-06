🦠 COVID-19 Contact Tracing System
A geospatial contact tracing system that identifies and visualizes potential COVID-19 exposure networks using clustering algorithms on real-world mobility data from Hyderabad, India.

📌 Overview
This project was developed as part of the B.Tech Data Science program at B V Raju Institute of Technology (BVRIT), Hyderabad. It simulates a contact tracing pipeline using DBSCAN clustering and Haversine distance to detect proximity-based exposure between individuals, and presents the results through an interactive Streamlit dashboard with Plotly visualizations.

✨ Features

📍 Geospatial Clustering — Uses DBSCAN with Haversine distance to group individuals based on physical proximity
🔗 Exposure Network Detection — Identifies potential contact chains from location data
📊 Interactive Dashboard — Streamlit-based UI for real-time exploration of contact clusters
🗺️ Map Visualizations — Plotly-powered charts and maps for intuitive data interpretation
🏙️ Real Hyderabad Data — Built and tested on mobility data from Hyderabad, Telangana


🛠️ Tech Stack
TechnologyPurposePythonCore languageDBSCAN (scikit-learn)Geospatial clusteringHaversineDistance calculation between GPS coordinatesStreamlitInteractive web dashboardPlotlyData visualization & mappingPandas / NumPyData processing

📁 Project Structure
covid-contact-tracing/
│
├── data/                   # Mobility datasets (Hyderabad)
├── notebooks/              # Exploratory analysis notebooks
├── src/
│   ├── clustering.py       # DBSCAN + Haversine logic
│   ├── tracing.py          # Contact chain identification
│   └── visualizations.py   # Plotly chart generators
├── app.py                  # Streamlit dashboard entry point
├── requirements.txt
└── README.md

🚀 Getting Started
Prerequisites
bashPython 3.8+
Installation
bashgit clone https://github.com/saiharish587/covid-contact-tracing.git
cd covid-contact-tracing
pip install -r requirements.txt
Run the Dashboard
bashstreamlit run app.py

🔬 How It Works

Data Ingestion — Location data of individuals is loaded and preprocessed
Distance Computation — Haversine formula calculates real-world distances between GPS coordinates
DBSCAN Clustering — Groups individuals who were in close proximity within a time window
Contact Tracing — Identifies potential exposure chains from the clusters
Visualization — Results are displayed on an interactive Streamlit dashboard with Plotly maps and graphs


👥 Team
Developed as a group project by students of the B.Tech Data Science department, BVRIT Hyderabad.

📄 License
This project is for academic purposes only.
