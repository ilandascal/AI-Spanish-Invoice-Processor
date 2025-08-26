import os


# clean_invoice_data(data_dict) Function: Our data cleaning utility
def clean_invoice_data(data_dict, filename):
    """
    Takes a dictionary of extracted invoice data and cleans/standardizes the values.
    """
    cleaned_data = {}

    cleaned_data['filename'] = filename
    # Clean the text fields by removing any leading/trailing whitespace
    supplier_name = data_dict.get('supplier', '').strip()
    if not supplier_name:  # If the supplier name is empty...
        name_from_file = os.path.splitext(os.path.basename(filename))[0]
        name_from_file = ''.join([i for i in name_from_file if not i.isdigit()]).strip()
        supplier_name = name_from_file.replace('_', ' ').replace('-', ' ')
        print(f"  --> AI did not find a supplier. Using fallback from filename: '{supplier_name}'")
    cleaned_data['supplier'] = supplier_name
    # ----------------------------------------
    cleaned_data['date'] = data_dict.get('date', '').strip()
    cleaned_data['invoice_id'] = data_dict.get('invoice_id', '').strip()

    # --- Clean the numeric fields ---
    # We will handle Tax first
    tax_str = data_dict.get('tax', '0').strip()
    # Replace comma with a period for a standard decimal, then remove the € symbol and any other spaces.
    tax_str_cleaned = tax_str.replace(',', '.').replace('€', '').strip()
    cleaned_data['tax'] = tax_str_cleaned

    # Now we handle Total
    total_str = data_dict.get('total', '0').strip()
    total_str_cleaned = total_str.replace(',', '.').replace('€', '').strip()
    cleaned_data['total'] = total_str_cleaned

    print(f"Cleaned data: {cleaned_data}")
    return cleaned_data

def verify_and_calculate_tax(data_dict):
    """
    Takes the raw extracted data from the AI, calculates, and verifies the tax.
    Returns the dictionary with a guaranteed, correct 'tax' field.
    """
    try:
        # Get numeric values for total and subtotal, default to 0.0 if not found
        total = float(data_dict.get('total', '0').replace(',', '.'))
        subtotal = float(data_dict.get('subtotal', '0').replace(',', '.'))

        # Path 1: An explicit total_tax exists. Let's verify it.
        if 'total_tax' in data_dict:
            explicit_tax = float(data_dict['total_tax'].replace(',', '.'))
            # Sanity Check: Is (Total - Subtotal) close to the explicit tax?
            if abs((total - subtotal) - explicit_tax) < 0.02:
                data_dict['tax'] = str(explicit_tax)
                return data_dict

        # Path 2: No explicit tax, or verification failed. Let's calculate from the breakdown.
        if 'iva_breakdown' in data_dict and isinstance(data_dict['iva_breakdown'], list):
            calculated_tax = sum(float(item.get('cuota', '0').replace(',', '.')) for item in data_dict['iva_breakdown'])
            # Sanity Check: Is (Total - Subtotal) close to our calculated tax?
            if abs((total - subtotal) - calculated_tax) < 0.02:
                data_dict['tax'] = f"{calculated_tax:.2f}"
                return data_dict

        # Path 3: All else fails. Mark as unverifiable.
        data_dict['tax'] = "ERROR: UNVERIFIABLE"
        return data_dict

    except (ValueError, TypeError) as e:
        print(f"  --> Error during tax verification: {e}")
        data_dict['tax'] = "ERROR: CALCULATION FAILED"
        return data_dict
