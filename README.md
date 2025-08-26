# 🤖 AI Invoice Processor

An intelligent, Python-based agent that automates the entire invoice processing and reconciliation workflow. This application uses a hybrid AI model to extract data from documents and a sophisticated logic engine to match invoices with bank payments, all managed through a clean, user-friendly web interface.

*(Optional: You can take a screenshot of your running app and embed it here for a professional touch!)*

## About The Project

This project was built to solve a common and time-consuming problem for small businesses: manually processing invoices and reconciling them with bank statements. The system is designed to be robust, accurate, and configurable, leveraging a modern AI stack and professional software architecture principles.

### Key Features

*   **Hybrid AI Extraction:** Utilizes a primary GPT-4o agent for speed and cost-effectiveness, with an automatic fallback to a specialist Google Document AI model for highly complex documents.
*   **Intelligent Reconciliation:** Matches invoices to payments using a multi-layered approach, including amount, fuzzy name matching (`thefuzz`), and configurable date tolerances.
*   **Robust Data Verification:** Employs a Python-based logic layer to verify AI-extracted data, performing calculations (e.g., for complex Spanish VAT) to ensure accuracy and prevent AI hallucinations.
*   **Automated File Management:** A professional, multi-stage file system that archives processed invoices, moves reconciled files to a dedicated folder, and isolates failed files for manual review.
*   **Secure and Configurable:** All user-specific settings (paths, sheet names, company info) and secrets (API keys) are managed in external configuration files (`config.py`, `.env`) for security and ease of setup.
*   **Interactive Web Interface:** A simple and intuitive UI built with Streamlit allows users to upload files and trigger processing and reconciliation with the click of a button.

## How It Works: Architecture Overview

The application is built on a modular, client-server architecture:

1.  **Frontend (`app.py`):** A Streamlit web interface acts as the "client." It handles file uploads and user commands.
2.  **Backend Engine (`main.py` & `core_processing.py`):** The Streamlit app sends jobs to the robust backend engine, which handles the entire file processing and business logic.
3.  **Specialized Tools:** The engine uses a suite of specialized modules for specific tasks:
    *   `extractor.py`: The primary AI agent (GPT-4o).
    *   `google_ai_connector.py`: The specialist AI agent (Google AI).
    *   `helpers.py`: Python-based data cleaning and verification functions.
    *   `sheets_connector.py`: Securely communicates with Google Sheets.
    *   `correlator.py`: The intelligent reconciliation engine.

## Getting Started

To get a local copy up and running, follow these steps.

### Prerequisites

*   Python 3.9+
*   A Google Cloud project with the **Sheets API** and **Document AI API** enabled.
*   An OpenAI API key with billing enabled.

### Installation & Configuration

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/ilandascal/AI-Spanish-Invoice-Processor.git
    cd AI-Spanish-Invoice-Processor
    ```

2.  **Set up a Python virtual environment:**
    ```sh
    python -m venv .venv
    # On Windows, run:
    .venv\Scripts\activate
    # On MacOS/Linux, run:
    # source .venv/bin/activate
    ```

3.  **Install the required packages:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Create your secrets file (`.env`):**
    *   Create a file named `.env` in the project root.
    *   Add your OpenAI API key to it: `OPENAI_API_KEY="sk-..."`

5.  **Configure the application (`config.py`):**
    *   Rename the `config_template.py` file to `config.py`.
    *   Open `config.py` and fill in all your specific details (folder paths, Google Sheet names, GCP project IDs, your company name, etc.).

6.  **Add your Google Cloud credentials:**
    *   Place your downloaded Google Cloud service account key file in the project root and name it `credentials.json` (or update the name in `config.py`).

## Usage

To launch the web application, run the following command in your terminal:

```sh
streamlit run app.py
```

Your web browser will open with the application running.

1.  **Step 1:** Drag and drop your invoice files and click "Process Uploaded Invoices."
2.  **Step 2:** Click "Run Reconciliation" to match the processed data with your bank payments.

## Project Structure

```
.
├── .venv/
├── archive/
│   └── reconciled/
├── failed/
├── .gitignore
├── README.md
├── app.py                  # The Streamlit Web UI Frontend
├── config.py               # (Local User Config - Ignored by Git)
├── config_template.py      # Template for configuration
├── core_processing.py      # Core logic for processing a single invoice
├── correlator.py           # The reconciliation engine
├── extractor.py            # The primary AI agent (GPT-4o)
├── google_ai_connector.py  # The specialist AI agent (Google AI)
├── helpers.py              # Data cleaning and verification functions
├── main.py                 # The command-line batch processor
├── requirements.txt        # Python package dependencies
└── sheets_connector.py     # Handles connection to Google Sheets
```