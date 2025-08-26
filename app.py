# app.py (Final Version)
import streamlit as st
import pandas as pd
import os
import config

# We now import the main functions directly from our other modules
from main import process_all_invoices
from correlator import reconcile_sheets

# --- Page Configuration ---
st.set_page_config(page_title="Ibiza AI Invoice Processor", page_icon="🤖", layout="wide")

# --- Header ---
st.title("🤖 AI-Powered Invoice Processor")
st.markdown("Welcome! This tool automates your invoice processing and reconciliation.")

# --- Main Workflow ---
st.header("Step 1: Upload Invoices")
st.write(f"Files will be saved to: `{config.INVOICE_FOLDER}`")

uploaded_files = st.file_uploader(
    "Choose your invoice files (PDFs or images)",
    accept_multiple_files=True,
    type=['pdf', 'png', 'jpg', 'jpeg']
)

if st.button("Process Uploaded Invoices", type="primary"):
    if uploaded_files:
        saved_count = 0
        with st.spinner("Saving uploaded files to the processing folder..."):
            for uploaded_file in uploaded_files:
                # Construct the destination path
                dest_path = os.path.join(config.INVOICE_FOLDER, uploaded_file.name)
                # Write the file's content to the destination
                with open(dest_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                saved_count += 1
        st.success(f"{saved_count} file(s) saved to the processing folder.")

        # --- NOW, WE RUN OUR EXISTING, ROBUST BACKEND ENGINE ---
        st.write("--- Starting Invoice Processing Engine ---")
        # We can use st.expander to show the detailed log in a collapsible box
        with st.expander("Click to see the detailed processing log"):
            # We will need to adapt our scripts to "log" to the UI.
            # For now, we tell the user to check the console.
            st.info("Processing is running. Please check your PyCharm console for detailed logs.")
            process_all_invoices()
            st.success("Invoice processing complete! Files have been moved to the 'archive' or 'failed' folders.")

    else:
        st.warning("Please upload at least one invoice file.")

# --- Reconciliation Section ---
st.header("Step 2: Run Reconciliation")
st.write("This will compare all processed invoices in your Google Sheet with the bank payments.")

if st.button("Run Reconciliation"):
    with st.spinner("Running reconciliation... Please check your PyCharm console for detailed logs."):
        reconcile_sheets()
        st.success("Reconciliation complete!")
        st.info("To see the final report, please re-run the reconciliation or we will build the report viewer next.")