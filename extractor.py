import os
import base64
import fitz  # This is the PyMuPDF library
import config

from openai import OpenAI
from dotenv import load_dotenv

# This line looks for a .env file and makes the variables inside it available to our script.
load_dotenv()

# Set up the OpenAI client.
client = OpenAI()

# Define the main function that will do all the work.
def extract_invoice_data(file_content, file_name):
    """
    This function takes the content (bytes) of an invoice file,
    extracts the raw image bytes, sends it to GPT-4o for analysis,
    and returns the extracted data.

    Args:
        file_content (bytes): The raw bytes of the file.
        file_name (str): The original name of the file, used to determine type.
    """
    print(f"Reading file content for: {file_name}")
    image_bytes = None

    try:
        file_extension = os.path.splitext(file_name)[1].lower()

        if file_extension == ".pdf":
            # PyMuPDF can open a PDF from memory using 'stream=file_content'
            doc = fitz.open(stream=file_content, filetype="pdf")
            page = doc.load_page(0)
            pix = page.get_pixmap()
            image_bytes = pix.tobytes("png")
            doc.close()
            print("  --> PDF content processed successfully.")

        elif file_extension in [".png", ".jpg", ".jpeg", ".gif", ".bmp"]:
            # If it's an image, the content is already the image bytes.
            image_bytes = file_content
            print(f"  --> Image content ({file_extension}) read successfully.")

        else:
            print(f"  --> Unsupported file type: {file_extension}. Skipping.")
            return None

        #Encode the image data into a format the API can understand (Base64).
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        #Call the OpenAI API with our image and prompt.
        response = client.chat.completions.create(
            # We use gpt-4o because it's excellent at "vision" tasks.
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        # This is our detailed instruction (prompt) to the AI.
                        {
                            "type": "text",
                            "text": f"""
                            You are a highly precise data extraction bot specializing in Spanish invoices. You have two equally important tasks.
                    
                            **Task 1: Supplier Identification**
                    
                            Your first and most critical task is to identify the **Supplier** of the invoice. To do this, you must first find the two entities on the document (Supplier and Client) and distinguish between them using the following strict rules:
                    
                            1.  **Rule 1: Identify the Client Block.**
                                Scan the document for a block of text that contains the exact name "{config.MY_COMPANY_NAME}" AND the exact NIF/CIF "{config.MY_COMPANY_CIF}". This block of text identifies the **Client**. You must completely ignore this entire block for the purpose of supplier identification.
                    
                            2.  **Rule 2: Identify the Supplier Block.**
                                The *other* block of text on the document that contains a Name, a NIF/CIF, and an Address is the **Supplier**. This block will have these characteristics:
                                *   **Name:** The name is often a company, which might end in "S.L.", "SL", "S.A.", or "SA".
                                *   **NIF/CIF:** It will have a 9-character identification string (e.g., a letter followed by 8 digits like `B12345678`).
                                *   **Address:** A Spanish address.
                    
                            3.  **Rule 3: Extract the Supplier Name.**
                                Once you have confidently identified the Supplier block (by first identifying and excluding the Client block), extract only the **official company name** and use it for the `supplier` field.
                    
                            **After identifying the supplier, find these other identity fields:**
                            *   `date`: The invoice date (`fecha factura`), formatted as DD-MM-YYYY.
                            *   `invoice_id`: The invoice number (`número de factura`).
                    
                            **Task 2: Financial Extraction**
                    
                            Focus your search on the bottom half (above the footer of the document, if it has a footer) of the final page to find these financial summary fields.
                            *   `total`: The final, grand total of the invoice (`Total Factura`).
                            *   `subtotal`: The subtotal before taxes (`Base Imponible Total` or `Subtotal`).
                            *   `total_tax`: The explicit total tax amount, if present (`Total IVA`).
                            *   `iva_breakdown`: A list of all VAT breakdown lines. For each line, extract the `base` (`Base Imponible`) and the `cuota` (`Cuota IVA`).
                    
                            **Final Formatting Rules:**
                            *   Return a single, clean JSON object. If a field is not found, omit it from the JSON.
                            *   Do not add any conversation, explanations, or Markdown.
                    
                            **Example:**
                            {{
                                "supplier": "Exluib S.A.",
                                "date": "16-08-2025",
                                "invoice_id": "A-5899",
                                "total": "484.10",
                                "subtotal": "420.00",
                                "iva_breakdown": [
                                    {{"base": "200.00", "cuota": "42.00"}},
                                    {{"base": "220.00", "cuota": "22.10"}}
                                ]
                            }}
                            """
                        },
                        # Here we provide the actual image data.
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            # We can set the max tokens to prevent overly long responses.
            max_tokens=500,
            temperature=0.2
        )

        # Step 8: Extract and return the clean data from the AI's response.
        extracted_text = response.choices[0].message.content
        return extracted_text

    except Exception as e:
        # If anything goes wrong, we print the error and return None.
        print(f"An error occurred during file extraction:  {e}")
        return None
