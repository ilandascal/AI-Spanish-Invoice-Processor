import json
import os

from extractor import extract_invoice_data
from helpers import verify_and_calculate_tax, clean_invoice_data
from sheets_connector import append_to_sheet
from google_ai_connector import analyze_invoice_with_google


def process_single_invoice(file_content, file_name):
    """
    The core logic for processing one invoice file from memory,
    including the fallback to the specialist agent.
    Returns True if successful, False otherwise.
    """
    # --- STEP 1: Primary Attempt with our GPT-4o agent ---
    extracted_data_json = extract_invoice_data(file_content, file_name)
    raw_data_dict = None

    if extracted_data_json:
        try:
            start_index = extracted_data_json.find('{')
            end_index = extracted_data_json.rfind('}') + 1
            if start_index != -1 and end_index != 0:
                clean_json_string = extracted_data_json[start_index:end_index]
                raw_data_dict = json.loads(clean_json_string)
        except json.JSONDecodeError:
            print(f"  --> Primary agent returned malformed JSON for {file_name}.")

    # --- STEP 2: Critical Field Check ---
    if not raw_data_dict or float(raw_data_dict.get('total', '0').replace(',', '.')) <= 0:
        print(f"  --> Primary agent failed. Falling back to specialist for {file_name}.")

        # --- STEP 3: Fallback to Specialist ---
        file_extension = os.path.splitext(file_name)[1].lower()
        mime_type = "application/pdf"
        if file_extension in [".jpg", ".jpeg"]:
            mime_type = "image/jpeg"
        elif file_extension == ".png":
            mime_type = "image/png"

        # The specialist needs a file path, so we must temporarily save the in-memory content.
        temp_file_path = os.path.join("temp_" + file_name)
        with open(temp_file_path, "wb") as f:
            f.write(file_content)

        # Call the specialist with the path to the temporary file
        raw_data_dict = analyze_invoice_with_google(temp_file_path, mime_type)

        # Clean up the temporary file immediately
        os.remove(temp_file_path)

    # --- STEP 4: Final Processing ---
    if raw_data_dict:
        print(f"Data for processing for {file_name}: {raw_data_dict}")
        verified_data_dict = verify_and_calculate_tax(raw_data_dict)
        clean_data_dict = clean_invoice_data(verified_data_dict, file_name)

        if append_to_sheet(clean_data_dict):
            print(f"  --> Successfully processed and saved {file_name} to Google Sheets.")
            return clean_data_dict  # <-- SUCCESS: Return the dictionary
        else:
            print(f"  --> Failed to write {file_name} to Google Sheets.")
            return None  # <-- FAILURE: Return None
    else:
        print(f"  --> Both agents failed to extract data for {file_name}.")
        return None  # <-- FAILURE: Return None
