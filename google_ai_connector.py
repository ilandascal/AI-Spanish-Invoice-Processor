import os
from google.cloud import documentai
import config

# --- CONFIGURATION ---
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
# --------------------

def analyze_invoice_with_google(file_path, mime_type="application/pdf"):
    """
    Sends an invoice to Google Document AI and translates the result
    into our standard project dictionary format.
    """
    opts = {"api_endpoint": f"{config.GOOGLE_LOCATION}-documentai.googleapis.com"}
    client = documentai.DocumentProcessorServiceClient(client_options=opts)
    name = client.processor_path(config.GOOGLE_PROJECT_ID, config.GOOGLE_LOCATION, config.GOOGLE_PROCESSOR_ID)

    with open(file_path, "rb") as image:
        image_content = image.read()

    document = {"content": image_content, "mime_type": mime_type}
    request = {"name": name, "raw_document": document}

    print("  --> Sending to Google Document AI Specialist...")
    result = client.process_document(request=request)
    document = result.document

    # --- TRANSLATION LOGIC ---
    # This is where we convert Google's output into our format.
    extracted_data = {}
    for entity in document.entities:
        # We only take fields with a reasonable confidence score
        if entity.confidence > 0.4:  # 40% confidence threshold
            # Map Google's field names to our field names
            if entity.type_ == "supplier_name":
                extracted_data['supplier'] = entity.mention_text
            elif entity.type_ == "invoice_date":
                extracted_data['date'] = entity.mention_text
            elif entity.type_ == "invoice_id":
                extracted_data['invoice_id'] = entity.mention_text
            elif entity.type_ == "total_amount":
                extracted_data['total'] = entity.mention_text
            elif entity.type_ == "net_amount":
                extracted_data['subtotal'] = entity.mention_text
            elif entity.type_ == "total_tax_amount":
                extracted_data['total_tax'] = entity.mention_text

    # For now, we don't need to translate the breakdown, as our Python calculator
    # can work with the total, subtotal, and total_tax fields.

    return extracted_data