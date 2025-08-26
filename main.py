import shutil
import os
import config

from core_processing import process_single_invoice
from correlator import reconcile_sheets

# --- DEFINE FOLDERS USING THE CONFIG ---
ARCHIVE_FOLDER = os.path.join(config.INVOICE_FOLDER, "archive")
FAILED_FOLDER = os.path.join(config.INVOICE_FOLDER, "failed")
# -----------------------------------------

#process_all_invoices() Function to loop trough and process all invoice files
def process_all_invoices():
    """
    Scans the invoice folder and runs the core processing logic for each file.
    This is now just a "batch runner" for our core processing function.
    """
    print(f"Starting batch processing in folder: {config.INVOICE_FOLDER}")
    os.makedirs(ARCHIVE_FOLDER, exist_ok=True)
    os.makedirs(FAILED_FOLDER, exist_ok=True)

    if not os.path.exists(config.INVOICE_FOLDER):
        print(f"Error: The folder '{config.INVOICE_FOLDER}' was not found.")
        return

    files_in_folder = os.listdir(config.INVOICE_FOLDER)
    successful_files = 0
    failed_files = 0

    for filename in files_in_folder:
        full_file_path = os.path.join(config.INVOICE_FOLDER, filename)
        if os.path.isfile(full_file_path):
            print(f"\n--- Processing: {filename} ---")

            try:
                # Read the file's content into memory (bytes)
                with open(full_file_path, "rb") as f:
                    file_content = f.read()

                # Call our new, central processing function
                if process_single_invoice(file_content, filename):
                    # If successful, move the file to the archive
                    destination_path = os.path.join(ARCHIVE_FOLDER, filename)
                    print(f"  --> Batch success. Moving to archive: {destination_path}")
                    shutil.move(full_file_path, destination_path)
                    successful_files += 1
                else:
                    # If it fails, move to the failed folder
                    destination_path = os.path.join(FAILED_FOLDER, filename)
                    print(f"  --> Batch failure. Moving to failed folder: {destination_path}")
                    shutil.move(full_file_path, destination_path)
                    failed_files += 1

            except Exception as e:
                print(f"  --> A critical error occurred while processing {filename}: {e}")
                destination_path = os.path.join(FAILED_FOLDER, filename)
                shutil.move(full_file_path, destination_path)
                failed_files += 1

    print("\n--- Batch processing complete! ---")
    print(f"Successfully processed: {successful_files} file(s).")
    print(f"Failed to process: {failed_files} file(s).")

# This special block is the entry point of our application.
if __name__ == "__main__":
    process_all_invoices()
 # After processing, run the correlation to get an updated payment report.
    print("\n======================================")
    print("Starting correlation of all records...")
    reconcile_sheets()
    print("======================================")