# 🧠 Airflow YouTube Comments ETL Project

This project implements an **Extract, Transform, Load (ETL)** pipeline using **Apache Airflow** to retrieve, clean, and store data from YouTube comments via the **YouTube Data API v3**.

This project modernizes a common tutorial (originally using the Twitter API) by demonstrating a practical, containerized approach to ETL with Airflow for real-world social data.

👉 [This is the video I'm referencing](https://www.youtube.com/watch?v=q8q3OFFfY6c)

## 💡 Project Motivation and Goal

The primary goal is to run a scheduled ETL workflow that transforms raw data into a clean, structured format, ready for downstream analysis or loading into a data warehouse.

| Stage | Data Source | Tool/Output |
| :--- | :--- | :--- |
| **Extract** | YouTube Data API v3 | `raw_youtube_comments.csv` |
| **Transform** | Raw CSV data (Pandas) | `clean_processesed_data.csv` |
| **Load** | Cleaned CSV data | `comments_final.json` (Local storage/Mock Load) |

---

## ⚙️ Prerequisites

Before starting, ensure you have the following installed and configured:

1.  **Docker & Docker Compose:** For running the containerized Airflow environment.
2.  **Git:** For cloning and version control.

### YouTube Data API Setup

You must obtain a developer API key to access YouTube data:

1.  Go to the **Google Cloud Console**.
2.  Create a new project.
3.  Navigate to **APIs & Services** → **Library** and **Enable** the **YouTube Data API v3**.
4.  Go to **APIs & Services** → **Credentials** → **Create Credentials** → **API Key**.
5.  **Copy the generated API Key.**

---

## 📁 Project Structure

Your local directory (e.g., `airflow/`) should have this structure for the Airflow containers to operate correctly:
``` bash
airflow/
├── dags/
│ ├── youtube_etl_dag.py                 # The core Airflow DAG definition
│ ├── extract_youtube_comments.py        # Python logic for API calls
│ └── data/                              # Output directory for ETL results
├── docker-compose.yml                   # Defines Airflow, Postgres, and setup services
└── requirements.txt                     # Project dependencies
```

### Required Dependencies (`requirements.txt`)

Ensure your `requirements.txt` file contains:

``` python
google-api-python-client pandas
```

---

## 🛠️ Implementation & Configuration

### 1. Update DAG Configuration

You must replace placeholders in the main DAG file (`dags/youtube_etl_dag.py`):

| Constant | Description | Example |
| :--- | :--- | :--- |
| `API_KEY` | **REQUIRED:** Your Google-generated YouTube Data API Key. | `"YOUR_API_KEY_HERE"` |
| `VIDEO_ID` | **REQUIRED:** The ID of the YouTube video you wish to analyze. | `"dQw4w9WgXcQ"` |

> **Note:** Hardcoding API keys is for demonstration only. In production, use Airflow **Connections** or a **Secrets Backend** for security.

### 2. The Extraction Logic (`extract_youtube_comments.py`)

This file contains the Python function that uses the `google-api-python-client` to connect to the YouTube API, fetch comments for the given `VIDEO_ID`, and handle pagination to collect results into a Pandas DataFrame.

### 3. The DAG Workflow (`youtube_etl_dag.py`)

The DAG defines a simple linear dependency: `extract` $\rightarrow$ `transform` $\rightarrow$ `load`.

-   **`extract_data`**: Fetches comments and saves them as `/dags/data/raw_youtube_comments.csv`.
-   **`transform_data`**: Reads the raw CSV, cleans text (removes newlines), drops rows with missing values, and saves to `/dags/data/cleaned_youtube_comments.csv`.
-   **`load_data`**: Reads the cleaned CSV and performs the mock load by converting the data to a JSON file (`/dags/data/comments_final.json`).

---

## ▶️ Running the Pipeline with Docker

Execute all commands from the root directory of your project (where `docker-compose.yml` is located).

### 1. Initialize Airflow

This command sets up the necessary database schema and creates the default admin user.

```bash
docker-compose up airflow-init
```
### 2. Start Airflow Services

Start the Airflow webserver, scheduler, and Postgres database in the background (-d).

``` bash
docker-compose up -d
```

### 3. Access Airflow UI
Open your browser and navigate to: http://localhost:8080

Log in with the default credentials:

| Key | Value |
| :--- | :--- |
| **Username** | airflow
| **Password** | airflow

### 4. Trigger the DAG

- Find the youtube_etl_dag in the DAGs list.

- Toggle the DAG to On.

- Manually Trigger the DAG to begin the ETL process.

### 5. Check Output
Upon successful completion of the DAG run, your final data will be available on your host machine inside the mounted volume:

``` bash
cd airflow/dags/data/
```

---
## 🛑 Troubleshooting Common Issues

This section addresses specific issues that users commonly encounter when setting up and running this Airflow pipeline.

### 1. How to resolve Permission Errors 
`` PermissionError: [Errno 13] Permission denied: '/opt/airflow/dags/data'``

This error occurs when the Airflow user inside the Docker container tries to create or write to the ``/opt/airflow/dags/data`` folder but doesn't have the necessary permissions on the host machine. This is a common issue with Docker volume mounting on Linux and macOS.

### Solution (Recommended)

Manually create the data folder on your host machine and apply liberal permissions to allow Docker access:
``` bash
# 1. Create the data directory (if it doesn't already exist)
mkdir -p ./dags/data

# 2. Grant full read/write/execute permissions (777)
chmod -R 777 ./dags/data

# 3. Restart Docker Compose to apply changes
docker-compose down
docker-compose up -d
```

### Cleaner Code Solution (Optional)

To make the script more robust, update the ``DATA_DIR`` definition in your ``dags/youtube_etl_dag.py`` to use relative paths. This ensures the directory is created adjacent to the DAG file:
``` python
import os

# Change this line in youtube_etl_dag.py
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)
# ... rest of the DAG code
```

### 2. How to Find the YouTube Video ID (VIDEO_ID)

The ``VIDEO_ID`` is a unique, 11-character alphanumeric identifier required by the YouTube Data API for the extraction process.

| URL Type | ExampleURL | Video ID |
| :--- | :--- | :--- |
| **Standard Watch URL** | https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=1sdQw4w9WgXcQ (After v=) |
| **Shortened URL** | https://youtu.be/dQw4w9WgXcQdQw4w9WgXcQ (After .be/) |
| **Playlist URL** | https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=...dQw4w9WgXcQ (After v=) |

**Rule:** Look for the 11-character string that follows either v= or the final / in the URL.
