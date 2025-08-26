# correlator.py (Gold Standard Version)

import os
import pandas as pd
import gspread
import config
import shutil
from thefuzz import fuzz

# --- SCORING LOGIC ---
# These variables define the score to assign upon a successful match.
# They are part of the core logic, so they live here, not in the config file.
PRIMARY_MATCH_SCORE = 100
SECONDARY_MATCH_SCORE = 85


# --------------------

def reconcile_sheets():
    """
    Reads data, finds matches, updates sheets, and moves reconciled files.
    """
    os.makedirs(config.RECONCILED_FOLDER, exist_ok=True)
    print(f"Reconciled files will be moved to: {config.RECONCILED_FOLDER}")
    try:
        # --- 1. CONNECT AND FETCH DATA ---
        print("Connecting to Google Sheets...")
        gc = gspread.service_account(filename=config.CREDENTIALS_FILE)
        invoice_sheet = gc.open(config.INVOICE_SHEET_NAME).sheet1
        bank_sheet = gc.open(config.BANK_SHEET_NAME).sheet1

        invoice_data = invoice_sheet.get_all_values()
        bank_data = bank_sheet.get_all_values()

        invoices_df = pd.DataFrame(invoice_data[1:], columns=invoice_data[0])
        bank_df = pd.DataFrame(bank_data[1:], columns=bank_data[0])

        invoices_df['gspread_row'] = invoices_df.index + 2
        bank_df['gspread_row'] = bank_df.index + 2
        print(f"Found {len(invoices_df)} invoices and {len(bank_df)} bank payments.")

        # --- 2. PREPARE DATA ---
        print("Cleaning and standardizing data types...")
        invoices_df['Invoice Date'] = pd.to_datetime(invoices_df['Invoice Date'], dayfirst=True, errors='coerce')
        bank_df['Date'] = pd.to_datetime(bank_df['Date'], dayfirst=True, errors='coerce')
        invoices_df.dropna(subset=['Invoice Date'], inplace=True)
        bank_df.dropna(subset=['Date'], inplace=True)
        print("Date columns successfully converted.")

        for col in ['Total Amount', 'Tax']:
            if col in invoices_df.columns:
                invoices_df[col] = pd.to_numeric(
                    invoices_df[col].astype(str).str.replace('€', '').str.replace(',', '.').str.strip(),
                    errors='coerce')

        if 'Amount' in bank_df.columns:
            bank_df['Amount'] = pd.to_numeric(
                bank_df['Amount'].astype(str).str.replace('€', '').str.replace(',', '.').str.strip(), errors='coerce')

        invoices_df.dropna(subset=['Total Amount'], inplace=True)
        bank_df.dropna(subset=['Amount'], inplace=True)
        invoices_df['Total Amount'] = invoices_df['Total Amount'].astype(float)
        bank_df['Amount'] = bank_df['Amount'].astype(float)
        print("Data cleaning complete.")

        # --- 3. THE ADVANCED MATCHING LOGIC ---
        print("\n--- Starting Advanced Reconciliation ---")
        invoice_updates = []
        bank_updates = []
        unpaid_invoices = invoices_df[invoices_df['Paid On'] == ''].copy()
        available_payments = bank_df[bank_df['Matched Invoice ID'] == ''].copy()

        for index, invoice in unpaid_invoices.iterrows():
            invoice_id_lower = invoice['Invoice Number'].lower()
            supplier_name_lower = invoice['Supplier Name'].lower()
            invoice_date = invoice['Invoice Date']
            invoice_amount = invoice['Total Amount']
            print(
                f"\n--- Checking Invoice: {invoice_id_lower} ({supplier_name_lower}) | Date: {invoice_date.strftime('%d-%m-%Y')} | Amount: {invoice_amount} ---")

            potential_payments = available_payments[available_payments['Amount'] == invoice_amount]
            if potential_payments.empty:
                print("  --> No payments found with matching amount.")
                continue

            print(f"  --> Found {len(potential_payments)} payment(s) with matching amount. Checking date and name...")
            for _, payment in potential_payments.iterrows():
                payment_date = payment['Date']
                cutoff_date = invoice_date - pd.Timedelta(days=config.PAYMENT_DATE_TOLERANCE_DAYS)
                is_date_valid = payment_date >= cutoff_date

                print(f"    - Checking Payment on: {payment_date.strftime('%d-%m-%Y')}")
                print(
                    f"      - Is Payment Date ({payment_date.strftime('%d-%m-%Y')}) >= Cutoff Date ({cutoff_date.strftime('%d-%m-%Y')})? -> {is_date_valid}")

                if not is_date_valid:
                    print("      - Date is NOT valid. Skipping this payment.")
                    continue

                match_found = False
                match_score = 0
                description_lower = payment['Description'].lower()
                primary_name_score = fuzz.token_set_ratio(supplier_name_lower, description_lower)

                print(f"      - Comparing with '{payment['Description']}': Primary Score = {primary_name_score}")
                if primary_name_score >= config.PRIMARY_MATCH_THRESHOLD:
                    print(f"        ✅ PRIMARY MATCH: Score is valid.")
                    match_found = True
                    match_score = PRIMARY_MATCH_SCORE  # <-- Now uses the variable defined at the top
                else:
                    details1_lower = payment.get('Bank Details 1', '').lower()
                    details2_lower = payment.get('Bank Details 2', '').lower()
                    combined_details = description_lower + " " + details1_lower + " " + details2_lower
                    secondary_name_score = fuzz.token_set_ratio(supplier_name_lower, combined_details)
                    print(f"      - Comparing with combined details: Secondary Score = {secondary_name_score}")
                    if secondary_name_score >= config.SECONDARY_MATCH_THRESHOLD:
                        print(f"        ✅ SECONDARY MATCH: Score is valid.")
                        match_found = True
                        match_score = SECONDARY_MATCH_SCORE  # <-- Now uses the variable defined at the top

                if match_found:
                    payment_date_string = payment['Date'].strftime('%d-%m-%Y')
                    invoice_updates.append({'range': f"F{invoice['gspread_row']}", 'values': [[payment_date_string]]})
                    invoice_updates.append({'range': f"H{invoice['gspread_row']}", 'values': [[str(match_score)]]})
                    bank_updates.append({'range': f"D{payment['gspread_row']}:E{payment['gspread_row']}",
                                         'values': [[invoice['Invoice Number'], invoice['Filename']]]})

                    available_payments.drop(payment.name, inplace=True)

                    filename_to_move = invoice['Filename']
                    source_path = str(os.path.join(config.ARCHIVE_FOLDER, filename_to_move))
                    destination_path = str(os.path.join(config.RECONCILED_FOLDER, filename_to_move))
                    if os.path.exists(source_path):
                        print(f"  --> Reconciled. Moving '{filename_to_move}' to reconciled folder.")
                        shutil.move(source_path, destination_path)

                    break

        # --- 4. BATCH UPDATE THE SHEETS ---
        if invoice_updates:
            print(f"\nUpdating {len(invoice_updates) // 2} rows in '{config.INVOICE_SHEET_NAME}'...")
            invoice_sheet.batch_update(invoice_updates)
        if bank_updates:
            print(f"Updating {len(bank_updates)} rows in '{config.BANK_SHEET_NAME}'...")
            bank_sheet.batch_update(bank_updates)

        # --- 5. Return the final results ---
        # We need to re-fetch the data to see the updates we just made.
        updated_invoice_data = invoice_sheet.get_all_records()
        final_invoices_df = pd.DataFrame(updated_invoice_data)

        print("\n--- Reconciliation Complete! ---")
        return final_invoices_df  # <-- SUCCESS: Return the full, updated dataframe

    except Exception as e:
        print(f"An error occurred during reconciliation: {e}")


if __name__ == "__main__":
    reconcile_sheets()