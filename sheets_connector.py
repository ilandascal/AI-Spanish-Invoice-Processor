# Import the libraries we need
import gspread
import config

# -----------------------------------------

def append_to_sheet(data_dict):
    """
    Appends a new row to the specified Google Sheet with invoice data.

    Args:
        data_dict (dict): A dictionary containing the invoice data.
    """
    try:
        print("Connecting to Google Sheets...")
        # Authenticate using the service account and the JSON key file.
        gc = gspread.service_account(filename=config.CREDENTIALS_FILE)

        # Open the spreadsheet by its name.
        spreadsheet = gc.open(config.INVOICE_SHEET_NAME)

        # Select the first worksheet.
        worksheet = spreadsheet.sheet1
        print(f"Successfully connected to worksheet: '{worksheet.title}'")

        # Prepare the data row in the correct order of your columns.
        # Make sure this order matches your Google Sheet columns exactly!
        row_to_add = [
            data_dict.get("supplier", ""),  # Column A: Supplier Name
            data_dict.get("date", ""),  # Column B: Invoice Date
            data_dict.get("invoice_id", ""),  # Column C: Invoice Number
            data_dict.get("tax", ""),  # Column D: Tax
            data_dict.get("total", ""),  # Column E: Total Amount
            "",  # Column F: Paid On (always blank on creation)
            data_dict.get("filename", "NO_FILENAME_PASSED"),  # Column G: Filename
            ""  # Column H: Match Percentage (always blank on creation)
        ]

        # Append the new row to the sheet.
        worksheet.append_row(row_to_add)
        print("Successfully appended a new row to the sheet!")
        return True

    except Exception as e:
        print(f"An error occurred while connecting to Google Sheets: {e}")
        return False
