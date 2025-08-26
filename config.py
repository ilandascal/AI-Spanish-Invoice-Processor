# config.py
# This file contains all the user-specific settings for the AI Invoice Processor.
# This is the ONLY file a new user should need to edit.

import os

# --- 1. File & Folder Paths ---
# The main folder where you drop new invoices to be processed.
INVOICE_FOLDER = r"C:\Users\kiaba\Documents\ilan\candurban\FacturasForAIParcer\NewDataFolder"
# Define the archive and failed folders relative to the main invoice folder
ARCHIVE_FOLDER = os.path.join(INVOICE_FOLDER, "archive")
FAILED_FOLDER = os.path.join(INVOICE_FOLDER, "failed")
# Define the reconciled folder inside the archive folder
RECONCILED_FOLDER = os.path.join(ARCHIVE_FOLDER, "reconciled")

# --- 2. Google Sheets Configuration ---
# The exact names of your Google Sheets.
INVOICE_SHEET_NAME = "Extracted Invoice Data"
BANK_SHEET_NAME = "Bank Payments"
# The name of the JSON file containing your Google service account credentials.
CREDENTIALS_FILE = "credentials.json"

# --- 3. Google Document AI (Specialist Agent) Configuration ---
# Your Google Cloud Project ID.
GOOGLE_PROJECT_ID = "invoiceparcerai"
# The location of your Document AI processor (e.g., "eu" or "us").
GOOGLE_LOCATION = "eu"
# The specific ID of your Document AI Invoice Processor.
GOOGLE_PROCESSOR_ID = "69ec5b3d2ea163c8"

# --- 4. Company-Specific Information (for Prompts) ---
# The name of YOUR company. This is used in the prompt to help the AI
# distinguish between the supplier and the client.
MY_COMPANY_NAME = "Purely Ibiza SL"
MY_COMPANY_CIF = "B01875434"

# --- 5. Reconciliation Logic Tuning ---
# The confidence score (out of 100) needed for a fuzzy name match.
PRIMARY_MATCH_THRESHOLD = 80
SECONDARY_MATCH_THRESHOLD = 90
# The tolerance in days for matching payments to invoices.
# A payment date can be this many days BEFORE the invoice date and still be considered a match.
PAYMENT_DATE_TOLERANCE_DAYS = 5